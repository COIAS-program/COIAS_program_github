#!/usr/bin/env python3
# -*- coding: UTF-8 -*
#COIAS ver 1.0
#timestamp 2022/5/26 15:30 sugiura

import tkinter as tk
from tkinter import messagebox,simpledialog
from PIL import Image, ImageTk
from astropy.io import fits
import traceback
import sys
import glob
import re
import math
import calcrect

### GLOBAL CONSTANTS #################################################
try:
    PNGSIZES  = Image.open('1_disp-coias.png').size
    FITSSIZES = (fits.open('warp1_bin.fits')[0].header['NAXIS1'],fits.open('warp1_bin.fits')[0].header['NAXIS2'])
except FileNotFoundError:
    print("1st png file or fits file are not found!")
    print(traceback.format_exc())
    sys.exit(1)

NALLIMAGES = len(glob.glob("*_disp-coias.png"))
if NALLIMAGES <= 1:
    print("Number of images is smaller than 1! NALLIMAGES={0:d}".format(NALLIMAGES))
    sys.exit(1)

ROOT = tk.Tk()
WINDOWWIDTH  = int(ROOT.winfo_screenwidth())
WINDOWHEIGHT = int(ROOT.winfo_screenheight())
WINDOWRATIO  = float(WINDOWWIDTH)/1440.0
######################################################################


### Functions for converting fits coords between png tk coords ########
def convertFits2PngCoords(fitsPosition):
    if fitsPosition[0]>FITSSIZES[0] or fitsPosition[1]>FITSSIZES[1]:
        raise ValueError("invalid fits positions! X={0:d} Xmax={1:d} Y={2:d} Ymax={3:d}".format(fitsPosition[0],FITSSIZES[0],fitsPosition[1],FITSSIZES[1]))
    
    fitsXRelPos = float(fitsPosition[0])/float(FITSSIZES[0])
    fitsYRelPos = float(fitsPosition[1])/float(FITSSIZES[1])

    pngXRelPos = fitsXRelPos
    pngYRelPos = 1.0 - fitsYRelPos

    pngXPosition = int(pngXRelPos*PNGSIZES[0])
    pngYPosition = int(pngYRelPos*PNGSIZES[1])

    return (pngXPosition, pngYPosition)

def convertPng2FitsCoords(pngPosition):
    if pngPosition[0]>PNGSIZES[0] or pngPosition[1]>PNGSIZES[1]:
        raise ValueError("invalid png positions! X={0:d} Xmax={1:d} Y={2:d} Ymax={3:d}".format(pngPosition[0],PNGSIZES[0],pngPosition[1],PNGSIZES[1]))

    pngXRelPos = float(pngPosition[0])/float(PNGSIZES[0])
    pngYRelPos = float(pngPosition[1])/float(PNGSIZES[1])

    fitsXRelPos = pngXRelPos
    fitsYRelPos = 1.0 - pngYRelPos

    fitsXPosition = int(fitsXRelPos*FITSSIZES[0])
    fitsYPosition = int(fitsYRelPos*FITSSIZES[1])

    return (fitsXPosition, fitsYPosition)
######################################################################


### Class for store a data of an asteroid in an image ################
class DataOfAnAsteroidInAnImage:
    #attributes: --------------------------------------------
    #            astName(str)
    #            NImage(int)
    #            fitsPosition(int tuple[2])
    #            pngPosition(int tuple[2])
    #            isManualAst(bool)
    #            aparturePngPoints(int list[3]tuple[2])
    #            apartureFitsPoints(int list[3]tuple[2])
    #            isSurvive(bool)
    #            isKnownAsteroid(bool)
    #--------------------------------------------------------
    
    def __init__(self, astName, NImage, fitsPosition, isManualAst=False, aparturePngPoints=[None, None, None]):
        if type(astName)!=str or NImage>=NALLIMAGES or len(fitsPosition)!=2 or fitsPosition[0]>FITSSIZES[0] or fitsPosition[1]>FITSSIZES[1]:
            raise ValueError("Some values for initializing data class are invalid.")
        if isManualAst:
            if type(isManualAst)!=bool or len(aparturePngPoints)!=3 or len(aparturePngPoints[0])!=2 or len(aparturePngPoints[1])!=2 or len(aparturePngPoints[2])!=2:
                raise ValueError("Some manual values for initializing data class are invalid.")
            for i in range(3):
                if aparturePngPoints[i][0]>PNGSIZES[0] or aparturePngPoints[i][1]>PNGSIZES[1]:
                    raise ValueError("Some aparture points are invalid.")
        
        self.astName = astName
        self.NImage = NImage
        self.fitsPosition = fitsPosition
        self.pngPosition = convertFits2PngCoords(fitsPosition)
        self.isManualAst = isManualAst
        self.aparturePngPoints = aparturePngPoints
        if isManualAst:
            self.apartureFitsPoints = []
            for i in range(3):
                self.apartureFitsPoints.append( convertPng2FitsCoords(aparturePngPoints[i]) )
        else:
            self.apartureFitsPoints = [None, None, None]

        if re.search(r'^H......',self.astName)!=None:
            self.isSurvive = False
            self.isKnownAsteroid = False
        else:
            self.isSurvive = True
            self.isKnownAsteroid = True
######################################################################


### Class for store all asteroids data ###############################
class DataOfAllAsteroids:
    #attributes: --------------------------------------------
    #            Ndata(int)
    #            astData(list of DataOfAnAsteroidInAnImage)
    #            NHMax(int)
    #--------------------------------------------------------
    
    #---constructor------------------------------------------
    def __init__(self, mode):
        if not (mode=="COIAS" or mode=="MANUAL" or mode=="RECOIAS"):
            raise ValueError("invalid mode for initializeing DataOfAllAsteroids instance")

        if mode=="COIAS":
            inputFileName = "disp.txt"
        else:
            inputFileName = "redisp.txt"

        f = open(inputFileName,"r")
        dataLines = f.readlines()
        f.close()
            
        self.Ndata = len(dataLines)
        self.astData = []
        for line in dataLines:
            contents = line.split()
            self.astData.append( DataOfAnAsteroidInAnImage(contents[0], int(contents[1]), (int(float(contents[2])),int(float(contents[3]))) ) )

        self.NHMax = 0
        f = open("disp.txt","r")
        lines = f.readlines()
        f.close()
        for line in lines:
            contents = line.split()
            if re.search(r'^H......',contents[0])!=None:
                NH = int(contents[0].lstrip('H'))
                if NH > self.NHMax:
                    self.NHMax = NH
        self.NHMax += 1
    #----------------------------------------------------------

    #---add an asteroid data for manual pickup-----------------
    def addManualAsteroidData(self, isSameAsPrevious, NImage, pngPosition, aparturePngPoints, isSpecified=False, NH=None):
        if type(isSameAsPrevious)!=bool:
            raise ValueError("isSameAsPrevious in addManualAsteroidData is not boolean value.")

        if isSpecified:
            if NH==None or type(NH)!=int:
                raise ValueError("please specify NH in int for specified mode.")

        if not isSpecified:
            if not isSameAsPrevious:
                self.NHMax += 1
            astName = "H"+str(self.NHMax).rjust(7,'0')
        else:
            astName = "H"+str(NH).rjust(7,'0')

        self.Ndata += 1
        self.astData.append( DataOfAnAsteroidInAnImage(astName, NImage, convertPng2FitsCoords(pngPosition), True, aparturePngPoints) )
    #----------------------------------------------------------

    #---delete asteroid data for manual mode-------------------
    def delManualAsteroidData(self, astName, NImage):
        isNotFound = True
        for i in range(self.Ndata):
            if self.astData[i].astName==astName and self.astData[i].NImage==NImage and self.astData[i].isManualAst:
                isNotFound = False
                break

        if isNotFound:
            print("we cannot find match astdata in delManualAsteroidData")
        else:
            del self.astData[i]
            self.Ndata -= 1
    #----------------------------------------------------------

    #---output approved H numbers to memo.txt in COIAS mode----
    def outputMemoTxt(self):
        outputNList = []
        f = open("memo.txt","w",newline="\n")
        for i in range(self.Ndata):
            if (not self.astData[i].isKnownAsteroid) and (self.astData[i].isSurvive) and (not self.astData[i].isManualAst):
                outputFlag = True
                for outputN in outputNList:
                    if outputN == int(self.astData[i].astName.lstrip('H')):
                        outputFlag = False
                if outputFlag:
                    f.write(self.astData[i].astName.lstrip('H')+"\n")
                    outputNList.append(int(self.astData[i].astName.lstrip('H')))

        f.close()
    #----------------------------------------------------------

    #---output manual information to memo_manual.txt in MANUAL mode
    def outputMemoManualTxt(self):
        sortedAstData = sorted(self.astData, key=lambda u: u.astName+str(u.NImage))
        f = open("memo_manual.txt","w",newline="\n")
        for i in range(self.Ndata):
            if sortedAstData[i].isManualAst:
                f.write(sortedAstData[i].astName.lstrip('H')+" "+str(sortedAstData[i].NImage)+" "+str(sortedAstData[i].fitsPosition[0])+" "+str(sortedAstData[i].fitsPosition[1])+" "+str(sortedAstData[i].apartureFitsPoints[0][0])+" "+str(sortedAstData[i].apartureFitsPoints[0][1])+" "+str(sortedAstData[i].apartureFitsPoints[1][0])+" "+str(sortedAstData[i].apartureFitsPoints[1][1])+" "+str(sortedAstData[i].apartureFitsPoints[2][0])+" "+str(sortedAstData[i].apartureFitsPoints[2][1])+"\n")

        f.close()
    #--------------------------------------------------------------
######################################################################


### Class for Tk inter ###############################################
class COIAS:
    #---constructor---------------------------------------
    #---this defines first window-------------------------
    #---important attributes: ----------------------------
    #                         maskOrNonmaskVar(int)-------
    #                         COIASModeVar(int)-----------
    def __init__(self, master=None):
        #---title of 1st window
        master.title("COIAS ver.1 mode selection")
        
        #---local constants
        fontSizeFirstWindow = int(20*WINDOWRATIO)
        padSizeFirstWindow = int(5*WINDOWRATIO)
        
        #---buttons for load img and quit
        self.firstWinLoadImgButton = tk.Button(ROOT, text="Load img", font=("",fontSizeFirstWindow), command = self.makeMainWindow)
        self.firstWinLoadImgButton.grid(row=0, column=0,sticky=tk.W+tk.E, padx=padSizeFirstWindow, pady=padSizeFirstWindow)
        self.firstWinQuitButton = tk.Button(ROOT, text="Quit", font=("",fontSizeFirstWindow), command = ROOT.quit)
        self.firstWinQuitButton.grid(row=0, column=1, sticky=tk.W+tk.E, padx=padSizeFirstWindow, pady=padSizeFirstWindow)

        #---just label
        self.firstWinLabel1 = tk.Label(ROOT, text="mode select", font=("",fontSizeFirstWindow), bg="LightSkyBlue")
        self.firstWinLabel1.grid(row=1, column=0, columnspan=3, sticky=tk.W+tk.E, padx=padSizeFirstWindow, pady=padSizeFirstWindow)

        #---radio buttons for mask or nonmask select
        #---self.maskOrNonmaskVar: 0 = mask
        #---                       1 = nonmask
        self.firstWinLabelRadio = tk.Label(ROOT, text="image preference", font=("",fontSizeFirstWindow), bg="gray80")
        self.firstWinLabelRadio.grid(row=2, column=0, sticky=tk.W, padx=padSizeFirstWindow, pady=padSizeFirstWindow)

        self.maskOrNonmaskVar = tk.IntVar()
        self.maskOrNonmaskVar.set(0)
        self.rdoMask = tk.Radiobutton(ROOT, value=0, variable=self.maskOrNonmaskVar, text="mask", font=("",fontSizeFirstWindow))
        self.rdoMask.grid(row=3, column=0, sticky=tk.W, padx=padSizeFirstWindow, pady=padSizeFirstWindow)
        self.rdoNonmask = tk.Radiobutton(ROOT, value=1, variable=self.maskOrNonmaskVar, text="nonmask", font=("",fontSizeFirstWindow))
        self.rdoNonmask.grid(row=3, column=1, sticky=tk.W, padx=padSizeFirstWindow, pady=padSizeFirstWindow)

        #---radio buttons for mode select
        #---self.COIASMode: 0 = COIAS
        #---                1 = MANUAL
        #---                2 = RECOIAS
        self.firstWinLabelMode = tk.Label(ROOT, text="COIAS mode", font=("",fontSizeFirstWindow), bg="gray80")
        self.firstWinLabelMode.grid(row=4, column=0, sticky=tk.W, padx=padSizeFirstWindow, pady=padSizeFirstWindow)
        
        self.COIASModeVar = tk.IntVar()
        self.COIASModeVar.set(0)
        self.rdoCOIAS = tk.Radiobutton(ROOT, value=0, variable=self.COIASModeVar, text="search", font=("",fontSizeFirstWindow))
        self.rdoCOIAS.grid(row=5, column=0, sticky=tk.W, padx=padSizeFirstWindow, pady=padSizeFirstWindow)
        self.rdoMANUAL = tk.Radiobutton(ROOT, value=1, variable=self.COIASModeVar, text="manual measure", font=("",fontSizeFirstWindow))
        self.rdoMANUAL.grid(row=5, column=1, sticky=tk.W, padx=padSizeFirstWindow, pady=padSizeFirstWindow)
        self.rdoRECOIAS = tk.Radiobutton(ROOT, value=2, variable=self.COIASModeVar, text="reconfirm", font=("",fontSizeFirstWindow))
        self.rdoRECOIAS.grid(row=5, column=2, sticky=tk.W, padx=padSizeFirstWindow, pady=padSizeFirstWindow)


    #---produce main window----------------------------
    #---important attributes: -------------------------
    #---                      COIASMode(str)-----------
    #---                      presentMaskOrNonmask(int)
    #---                      asteroidData(DataOfAllAsteroids)
    #---                      pngImages(tk.PhotoImage)-
    #---                      presentImageNumber(int)--
    #---                      sqOnOffFlag(bool)--------
    #---                      doBlink(bool)------------
    #---                      specifyHNumber(bool)-----
    #---                      mousePngPosition(int list[2])
    #---                      coldPresentMousePosition(int list[2])
    #---                      coldPresentImageNumber(int)-----
    #---                      coldSpecifyHNumber(bool)--------
    #---                      isActivateSubWin(bool)
    def makeMainWindow(self):
        canvasWidth  = int(WINDOWWIDTH*0.92)
        canvasHeight = int(WINDOWHEIGHT*0.80)
        
        #---local constants
        fontSizeMainWindow = int(14*WINDOWRATIO)
        numberBoxSize = 9
        coordsBoxSize = 22
        messageBoxSize = 45

        #---store the mode when the window is produced
        if self.COIASModeVar.get()==0:
            self.COIASMode = "COIAS"
        elif self.COIASModeVar.get()==1:
            self.COIASMode = "MANUAL"
        elif self.COIASModeVar.get()==2:
            self.COIASMode = "RECOIAS"
        self.presentMaskOrNonmask = self.maskOrNonmaskVar.get()
        
        #---produce main window itself
        self.main_win = tk.Toplevel(ROOT)
        self.main_win.title("COIAS ver. 1 " + self.COIASMode + " mode")

        #---set widgets 1: first row
        self.blinkStartStopButton = tk.Button(self.main_win, text='Blink start', font=("",fontSizeMainWindow), command = self.startStopBlinking)
        self.blinkStartStopButton.grid(row=0, column=0, sticky=tk.W)
        self.backButton = tk.Button(self.main_win, text='Back', font=("",fontSizeMainWindow), command = self.onBackButton)
        self.backButton.grid(row=0, column=1, sticky=tk.W)
        self.nextButton = tk.Button(self.main_win, text="Next",font=("",fontSizeMainWindow), command = self.onNextButton)
        self.nextButton.grid(row=0, column=2, sticky=tk.W)
        self.sqOnOffButton = tk.Button(self.main_win, text="Sq. Off", font=("",fontSizeMainWindow), command = self.sqOnOff)
        self.sqOnOffButton.grid(row=0, column=3, sticky=tk.W)
        self.numberBox = tk.Entry(self.main_win, font=("", fontSizeMainWindow), width=numberBoxSize)
        self.numberBox.grid(row=0, column=4, sticky=tk.W)
        self.coordsBox = tk.Entry(self.main_win, font=("", fontSizeMainWindow), width=coordsBoxSize)
        self.coordsBox.grid(row=0, column=5, sticky=tk.W)
        self.messageBox = tk.Entry(self.main_win, font=("", fontSizeMainWindow), width=messageBoxSize)
        self.messageBox.grid(row=0, column=6, sticky=tk.W)
        if self.COIASMode == "MANUAL":
            self.specifyHNumberButton = tk.Button(self.main_win, text="Manual H Number: Auto", font=("",fontSizeMainWindow), command = self.changeSpecifyHNumber)
            self.specifyHNumberButton.grid(row=0, column=7, sticky=tk.W)
        if self.COIASMode == "COIAS" or self.COIASMode == "MANUAL":
            self.outputButton = tk.Button(self.main_win, text="Output",font=("",fontSizeMainWindow), command = self.output)
            self.outputButton.grid(row=0, column=8, sticky=tk.W)

        #---set widgets 2: main canvas
        self.canvas = tk.Canvas(self.main_win, width=canvasWidth, height=canvasHeight)
        self.canvas.grid(row=1, column=0, columnspan=9, sticky=tk.W+tk.E+tk.N+tk.S)
        self.canvas.bind('<Motion>', self.getMouseCoord)
        self.canvas.bind('<ButtonPress-1>', self.onClicked)

        #---set widgets 3: scroll bars
        self.xscroll = tk.Scrollbar(self.main_win, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.xscroll.grid(row=2, column=0, columnspan=9, sticky=tk.W+tk.E)
        self.yscroll = tk.Scrollbar(self.main_win, orient=tk.VERTICAL, command=self.canvas.yview)
        self.yscroll.grid(row=1, column=9, sticky=tk.N+tk.S)
        self.canvas.config(xscrollcommand = self.xscroll.set)
        self.canvas.config(yscrollcommand = self.yscroll.set)
        self.canvas.config(scrollregion = (0, 0, PNGSIZES[0], PNGSIZES[1]))

        #---read asteroid data
        self.asteroidData = DataOfAllAsteroids(self.COIASMode)

        #---load png images
        if self.maskOrNonmaskVar.get()==0:
            imageNameList = sorted(glob.glob("*_disp-coias.png"))
        elif self.maskOrNonmaskVar.get()==1:
            imageNameList = sorted(glob.glob("*_disp-coias_nonmask.png"))
        self.pngImages = []
        for i in range(NALLIMAGES):
            self.pngImages.append(tk.PhotoImage(file = imageNameList[i]))

        #---initialize some important attributes
        self.presentImageNumber = 0
        self.sqOnOffFlag = True
        self.doBlink = False
        self.specifyHNumber = False
        self.mousePngPosition = [0,0]
        self.coldPresentMousePosition = [0,0]
        self.isActivateSubWin = False

        #---initial draw
        self.draw()
        self.numberBox.insert(tk.END, "Image # 1")
        self.coordsBox.insert(tk.END, "X pix 0, Y pix 0")
        self.messageBox.insert(tk.END, "message:")
    #--------------------------------------------------

    
    #---draw png image and asteroid data---------------
    def draw(self):
        self.canvas.delete("image")
        self.canvas.create_image(PNGSIZES[0]/2, PNGSIZES[1]/2, image=self.pngImages[self.presentImageNumber], tag="image")
        self.drawAsteroidOnly()
    #--------------------------------------------------

    #---draw asteroid rectangles and names-------------
    def drawAsteroidOnly(self):
        fontSizeAstName = int(16*WINDOWRATIO)
        dispAstName = int(30*(0.7+WINDOWRATIO*0.3))
        
        self.canvas.delete("asteroid")
        for i in range(self.asteroidData.Ndata):
            if self.asteroidData.astData[i].NImage==self.presentImageNumber and self.sqOnOffFlag:
                #---choose color
                if self.asteroidData.astData[i].isManualAst:
                    color = "#219DDD"
                elif self.asteroidData.astData[i].isKnownAsteroid:
                    color = "#000000"
                elif self.asteroidData.astData[i].isSurvive:
                    color = "#FF0000"
                else:
                    color = "#000000"

                #---draw rectangles and names
                self.canvas.create_rectangle(self.asteroidData.astData[i].pngPosition[0]-20, self.asteroidData.astData[i].pngPosition[1]-20, self.asteroidData.astData[i].pngPosition[0]+20, self.asteroidData.astData[i].pngPosition[1]+20, outline=color, width=5, tag="asteroid")
                self.canvas.create_text(self.asteroidData.astData[i].pngPosition[0]-dispAstName, self.asteroidData.astData[i].pngPosition[1]-dispAstName, text=self.asteroidData.astData[i].astName, fill=color, font=("Purisa",fontSizeAstName), tag="asteroid")
    #--------------------------------------------------


    #---method for blinkStartStopButton----------------
    def startStopBlinking(self):
        if self.doBlink:
            self.doBlink = False
            self.blinkStartStopButton["text"] = "Blink start"
        else:
            self.doBlink = True
            self.blinkStartStopButton["text"] = "Blink stop"
            self.blink()

    def blink(self):
        if self.doBlink:
            self.presentImageNumber += 1
            if self.presentImageNumber == NALLIMAGES:
                self.presentImageNumber = 0

            self.draw()
            self.numberBox.delete(0, tk.END)
            self.numberBox.insert(tk.END, "Image # " + str(self.presentImageNumber+1))
            
            ROOT.after(100, self.blink)
    #--------------------------------------------------


    #---method for backButton--------------------------
    def onBackButton(self):
        if self.presentImageNumber == 0:
            self.presentImageNumber = NALLIMAGES - 1
        else:
            self.presentImageNumber -= 1

        self.draw()
        self.numberBox.delete(0, tk.END)
        self.numberBox.insert(tk.END, "Image # " + str(self.presentImageNumber+1))
    #--------------------------------------------------


    #---method for nextButton--------------------------
    def onNextButton(self):
        self.presentImageNumber += 1
        if self.presentImageNumber == NALLIMAGES:
            self.presentImageNumber = 0

        self.draw()
        self.numberBox.delete(0, tk.END)
        self.numberBox.insert(tk.END, "Image # " + str(self.presentImageNumber+1))
    #--------------------------------------------------


    #---method for sqOnOffButton-----------------------
    def sqOnOff(self):
        if self.sqOnOffFlag:
            self.sqOnOffFlag = False
            self.sqOnOffButton["text"] = "Sq. On"
        else:
            self.sqOnOffFlag = True
            self.sqOnOffButton["text"] = "Sq. Off"

        self.drawAsteroidOnly()
    #--------------------------------------------------


    #---method for specifyHNumberButton----------------
    def changeSpecifyHNumber(self):
        if self.specifyHNumber:
            self.specifyHNumber = False
            self.specifyHNumberButton["text"] = "Manual H Number: Auto"
        else:
            self.specifyHNumber = True
            self.specifyHNumberButton["text"] = "Manual H Number: Self"
    #--------------------------------------------------


    #---method for mouse motion on the canvas----------
    def getMouseCoord(self, event):
        xRelPosScrBar = self.xscroll.get()[0]
        yRelPosScrBar = self.yscroll.get()[0]
        xPosScrBar = int(xRelPosScrBar*PNGSIZES[0])
        yPosScrBar = int(yRelPosScrBar*PNGSIZES[1])
        self.mousePngPosition[0] = xPosScrBar + event.x
        self.mousePngPosition[1] = yPosScrBar + event.y
        self.coordsBox.delete(0,tk.END)
        self.coordsBox.insert(tk.END,"X pix "+str(self.mousePngPosition[0])+", Y pix "+str(self.mousePngPosition[1]))
    #--------------------------------------------------


    #---method for click on the canvas-----------------
    def onClicked(self, event):
        if not self.isActivateSubWin:
            self.messageBox.delete(0, tk.END)
            self.messageBox.insert(tk.END,"message:")
            
            self.coldPresentMousePosition[0] = self.mousePngPosition[0]
            self.coldPresentMousePosition[1] = self.mousePngPosition[1]
            self.coldPresentImageNumber = self.presentImageNumber
            self.coldSpecifyHNumber = self.specifyHNumber
            manualSelectFlag = False
            for i in reversed(range(self.asteroidData.Ndata)):
                if self.asteroidData.astData[i].NImage==self.presentImageNumber and self.sqOnOffFlag and \
                   self.coldPresentMousePosition[0]>self.asteroidData.astData[i].pngPosition[0]-20 and \
                   self.coldPresentMousePosition[0]<self.asteroidData.astData[i].pngPosition[0]+20 and \
                   self.coldPresentMousePosition[1]>self.asteroidData.astData[i].pngPosition[1]-20 and \
                   self.coldPresentMousePosition[1]<self.asteroidData.astData[i].pngPosition[1]+20:
                    if self.COIASMode == "COIAS":
                        self.selectSurviveAsteroidInCOIAS(i)
                    elif self.COIASMode == "RECOIAS":
                        self.messageBox.delete(0, tk.END)
                        self.messageBox.insert(tk.END,"message: This is reconfirm mode; no need to select.")
                    elif self.COIASMode == "MANUAL" and  (not self.asteroidData.astData[i].isManualAst):
                        self.messageBox.delete(0, tk.END)
                        self.messageBox.insert(tk.END,"message: This is already confirmed object.")
                    else:
                        self.delManualAsteroid(i)
                        manualSelectFlag = True

            if self.COIASMode == "MANUAL" and (not manualSelectFlag):
                self.addManualAsteroid(self.coldPresentMousePosition)

            self.drawAsteroidOnly()
    #--------------------------------------------------


    #---select survive asteroid in COIAS mode----------
    def selectSurviveAsteroidInCOIAS(self, index):
        if self.asteroidData.astData[index].isKnownAsteroid:
            self.messageBox.delete(0, tk.END)
            self.messageBox.insert(tk.END,"message: This is known asteroid: " + self.asteroidData.astData[index].astName)
        else:
            thisHN = self.asteroidData.astData[index].astName
            if self.asteroidData.astData[index].isSurvive:
                surviveBool = False
            else:
                surviveBool = True
                
            for i in range(self.asteroidData.Ndata):
                if self.asteroidData.astData[i].astName == thisHN:
                    self.asteroidData.astData[i].isSurvive = surviveBool
    #--------------------------------------------------


    #---del re-selected manual asteroid----------------
    def delManualAsteroid(self, index):
        isYes = messagebox.askyesno("confirmation","Do you really want to delete this manual selected object?")
        if isYes:
            self.asteroidData.delManualAsteroidData(self.asteroidData.astData[index].astName, self.presentImageNumber)
    #--------------------------------------------------


    #---method for output memo--------------------------
    def output(self):
        if self.COIASMode == "COIAS":
            self.asteroidData.outputMemoTxt()
        elif self.COIASMode == "MANUAL":
            self.asteroidData.outputMemoManualTxt()
    #---------------------------------------------------


    ### methods for manual measuring #########################
    #---important attributes: --------------------------------
    #---                      specifiedNH(int)----------------
    #---                      isSameAsPrevious(bool)----------
    #---                      mousePositionSubWin(int list[2])
    #---                      canvasSize(const int)
    #---                      NClick(int)---------------------
    #---                      clickedPositions(int list[3][2])
    #---                      eventPositions(int list[3][2])--
    
    #---add selected manual asteroid via making aparture
    def addManualAsteroid(self, mousePosition):
        #---determine H number
        goFlag = True
        if self.specifyHNumber:
            self.specifiedNH = simpledialog.askinteger("specify H number","Please specify H number of this object in integer.")
            if self.specifiedNH == None:
                goFlag = False
        else:
            self.isSameAsPrevious = messagebox.askyesno("question","Is this object the same as the previous one you chose?")

        if goFlag:
            self.makeSubWindow()
    #---------------------------------------------------


    #---produce sub window------------------------------
    def makeSubWindow(self):
        #--activate sub window
        self.isActivateSubWin = True
        
        #---const attribute
        self.canvasSize = int(500*WINDOWRATIO)
        
        #---local constants
        fontSizeSubWindow = int(16*WINDOWRATIO)
        coordsBoxSize = 22
        promptBoxSize = 30

        #---initialize some attribute
        self.mousePositionSubWin = [0, 0]
        self.NClick = 0
        self.clickedPositions = [ [0, 0], [0, 0], [0, 0] ]
        self.eventPositions   = [ [0, 0], [0, 0], [0, 0] ]
        
        #---prepare clipped png image
        if self.presentMaskOrNonmask==0: pngName = "{0:d}_disp-coias.png".format(self.presentImageNumber+1)
        else:                            pngName = "{0:d}_disp-coias_nonmask.png".format(self.presentImageNumber+1)
        clippedPng = Image.open(pngName).crop((self.coldPresentMousePosition[0]-20, self.coldPresentMousePosition[1]-20, self.coldPresentMousePosition[0]+20, self.coldPresentMousePosition[1]+20))
        clippedPngForCanvas = clippedPng.resize((self.canvasSize, self.canvasSize), resample=0)
        self.clippedPngForCanvasTk = ImageTk.PhotoImage(clippedPngForCanvas)
        
        #---produce sub window itself
        self.sub_win = tk.Toplevel(ROOT)
        self.sub_win.title("manual measure: aparture setting")
        self.sub_win.geometry("+{0:d}+{1:d}".format(int(ROOT.winfo_screenwidth()/2-self.canvasSize/2), int(ROOT.winfo_screenheight()/2-self.canvasSize/2)))
        self.sub_win.protocol("WM_DELETE_WINDOW", self.closeWindow)

        #---set widgets
        self.coordsBoxSubWin = tk.Entry(self.sub_win, font=("", fontSizeSubWindow), width=coordsBoxSize)
        self.coordsBoxSubWin.grid(row=0, column=0, columnspan=2, sticky=tk.W)
        self.coordsBoxSubWin.insert(tk.END, "X pix 0, Y pix 0")
        self.helpButton = tk.Button(self.sub_win, text="Help", font=("", fontSizeSubWindow), command = self.showHelpAparture)
        self.helpButton.grid(row=0, column=2, sticky=tk.E)
        self.canvasSubWin = tk.Canvas(self.sub_win, width=self.canvasSize, height=self.canvasSize)
        self.canvasSubWin.grid(row=1, column=0, columnspan=3, sticky=tk.W+tk.E+tk.N+tk.S)
        self.canvasSubWin.bind("<Motion>", self.getMouseCoordSubWin)
        self.canvasSubWin.bind("<ButtonPress-1>", self.onClickedSubWin)
        self.canvasSubWin.create_image(self.canvasSize/2, self.canvasSize/2, image=self.clippedPngForCanvasTk)
        self.yesButton = tk.Button(self.sub_win, text="Yes", font=("", fontSizeSubWindow), command = self.yesSubWin)
        self.yesButton.grid(row=2, column=0, sticky=tk.W)
        self.promptBox = tk.Entry(self.sub_win, font=("", fontSizeSubWindow), width=promptBoxSize)
        self.promptBox.grid(row=2, column=1, sticky=tk.W+tk.W)
        self.noButton  = tk.Button(self.sub_win, text="Clear", font=("", fontSizeSubWindow), command = self.noSubWin)
        self.noButton.grid(row=2, column=2, sticky=tk.E)
    #---------------------------------------------------


    #---show help for aparture selection----------------
    def showHelpAparture(self):
        messagebox.showinfo("how to select aparture","拡大画像の3点を選んで星像を囲む長方形のアパーチャーを設定します。星像を囲む長方形を想像し、その頂点のうち3点をクリックしてください。必ずしも選んだ3点が長方形の頂点になるとは限りませんが、3点の成す角がなるべく直角になるように選ぶと一致します。最後に長方形アパーチャーが表示されますので、よければYesボタンを押してください。Noボタンを押せばアパーチャーの設定をやり直せます。この星像の測定を中止したければ、拡大画像が表示されているサブウィンドウの左上のバツ印を押してウィンドウを閉じてください。")
    #---------------------------------------------------


    #---get mouse position in sub window----------------
    def getMouseCoordSubWin(self, event):
        canvasLeftUpperPositionX = self.coldPresentMousePosition[0]-20
        canvasLeftUpperPositionY = self.coldPresentMousePosition[1]-20
        canvasXRelPos = float(event.x) / float(self.canvasSize)
        canvasYRelPos = float(event.y) / float(self.canvasSize)
        
        self.mousePositionSubWin[0] = int(canvasLeftUpperPositionX + canvasXRelPos * 40)
        self.mousePositionSubWin[1] = int(canvasLeftUpperPositionY + canvasYRelPos * 40)

        self.coordsBoxSubWin.delete(0, tk.END)
        self.coordsBoxSubWin.insert(tk.END, "X pix "+str(self.mousePositionSubWin[0])+", Y pix "+str(self.mousePositionSubWin[1]))
    #---------------------------------------------------


    #---set aparture------------------------------------
    def onClickedSubWin(self, event):
        if self.NClick < 3:
            self.clickedPositions[self.NClick][0] = self.mousePositionSubWin[0]
            self.clickedPositions[self.NClick][1] = self.mousePositionSubWin[1]
            self.eventPositions[self.NClick][0] = event.x
            self.eventPositions[self.NClick][1] = event.y
            self.canvasSubWin.create_oval( event.x-3, event.y-3, event.x+3, event.y+3, fill="#FF0000", outline="#FF0000", width=0, tag="clickedPos")
            self.NClick += 1
        if self.NClick == 3:
            rect = calcrect.calc_rectangle_parameters([self.eventPositions[0][0], self.eventPositions[0][1]], [self.eventPositions[1][0], self.eventPositions[1][1]], [self.eventPositions[2][0], self.eventPositions[2][1]])
            if rect == None:
                self.NClick=0
                self.clickedPositions = [ [0, 0], [0, 0], [0, 0] ]
                self.eventPositions   = [ [0, 0], [0, 0], [0, 0] ]
                self.canvasSubWin.delete("clickedPos")
                self.promptBox.delete(0, tk.END)
                self.promptBox.insert(tk.END, "same points. Select an aparture again.")
            else:
                self.canvasSubWin.create_polygon(rect["rectPos1"][0], rect["rectPos1"][1], rect["rectPos2"][0], rect["rectPos2"][1], rect["rectPos3"][0], rect["rectPos3"][1], rect["rectPos4"][0], rect["rectPos4"][1], fill='', outline="#FF0000", width=2, tag="clickedPos")
                self.promptBox.delete(0, tk.END)
                self.promptBox.insert(tk.END, "Good aparture?")
    #---------------------------------------------------


    #---yes button--------------------------------------
    def yesSubWin(self):
        if self.NClick == 3:
            if self.specifyHNumber:
                self.asteroidData.addManualAsteroidData(self.isSameAsPrevious, self.coldPresentImageNumber, self.coldPresentMousePosition, self.clickedPositions, self.coldSpecifyHNumber, self.specifiedNH)
            else:
                self.asteroidData.addManualAsteroidData(self.isSameAsPrevious, self.coldPresentImageNumber, self.coldPresentMousePosition, self.clickedPositions)
            self.sub_win.destroy()
            self.drawAsteroidOnly()
            self.isActivateSubWin = False
    #---------------------------------------------------

    
    #---no button---------------------------------------
    def noSubWin(self):
        self.NClick=0 
        self.clickedPositions = [ [0, 0], [0, 0], [0, 0] ]
        self.eventPositions   = [ [0, 0], [0, 0], [0, 0] ]
        self.canvasSubWin.delete("clickedPos")
        self.promptBox.delete(0, tk.END)
        self.promptBox.insert(tk.END, "Please select an aparture again.")
    #---------------------------------------------------


    #---close sub window--------------------------------
    def closeWindow(self):
        self.isActivateSubWin = False
        self.sub_win.destroy()
    #---------------------------------------------------

    ##########################################################
    
######################################################################


### EXECUTION ########################################################
app = COIAS(master=ROOT)
ROOT.mainloop()
######################################################################
