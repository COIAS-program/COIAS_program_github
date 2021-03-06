#!/usr/bin/env python3
# -*- coding: UTF-8 -*
import os
import glob
import time
import shutil
from astropy.io import fits
from astropy.time import Time
import traceback

try:
    #---variables--------------------------------
    fitsFileNameList = sorted(glob.glob('warp*_bin.fits'))
    Ndata = len(fitsFileNameList)
    presentTimeStamp = time.time()
    isCorrectDirectory = [0] * Ndata
    directoryNames = ['a'] * Ndata
    preciseOrbitFleshTime = 60*60*24*14
    #--------------------------------------------

    #---read ra dec jd of warp files-------------
    raList = []
    decList = []
    jdList = []
    for i in range(Ndata):
        scidata = fits.open(fitsFileNameList[i])
        raList.append(scidata[0].header['CRVAL1'])
        decList.append(scidata[0].header['CRVAL2'])
        jdList.append(scidata[0].header['JD'])
    #--------------------------------------------

    #---get yyyy-mm-dd of jdList[0]--------------
    tInTimeObj = Time(jdList[0], format="jd")
    tInIso = tInTimeObj.iso
    yyyy_mm_dd = tInIso.split()[0]
    #--------------------------------------------

    #---if directory ~/.coias/orbit_data/yyyy_mm_dd does not exist-
    #---we produce it----------------------------------------------
    dirName = os.path.expanduser("~") + "/.coias/orbit_data/" + yyyy_mm_dd
    if not os.path.isdir(dirName):
        os.mkdir(dirName)
    logFileName = dirName + "/log.txt"
    if not os.path.isfile(logFileName):
        logFile = open(logFileName, "w")
        logFile.write("0")
        logFile.close
    #--------------------------------------------------------------

    #---read ~/.coias/orbit_data/log.txt---------
    logFileName = dirName + "/log.txt"
    logFile = open(logFileName,"r")
    line = logFile.readline()
    maxNumOrbitDirectories = int(line.rstrip("\n"))
    logFile.close()
    #--------------------------------------------
    
    #---check presice orbit directory exists or not-
    filesInOrbitDataDir = glob.glob(dirName + "/*")
    for fileName in filesInOrbitDataDir:
        if os.path.isdir(fileName):
            if (not os.path.isfile(fileName+"/ra_dec_jd_time.txt")) or (not os.path.isfile(fileName+"/numbered_new2B.txt")) or (not os.path.isfile(fileName+"/karifugo_new2B.txt")) or (not os.path.isfile(fileName+"/search_astB.txt")) or (not os.path.isfile(fileName+"/bright_asteroid_MPC_names_in_the_field.txt")) or (not os.path.isfile(fileName+"/name_conversion_list_in_the_field.txt")):
                print("The directory "+fileName+" does not have ra_dec_jd_time.txt, numbered_new2B.txt, karifugo_new2B.txt, search_astB.txt, bright_asteroid_MPC_names_in_the_field.txt, or name_conversion_list_in_the_field.txt")
                print("Remove the directory.")
                shutil.rmtree(fileName)
            else:
                raDecJdTimeFile = open(fileName+"/ra_dec_jd_time.txt","r")
                line = raDecJdTimeFile.readline()
                content = line.split()
                ra = float(content[0])
                dec = float(content[1])
                jd = float(content[2])
                fileTime = float(content[3])
                raDecJdTimeFile.close()

                for i in range(Ndata):
                    if abs(ra-raList[i])<0.01 and abs(dec-decList[i])<0.01 and abs(jd-jdList[i])<0.00001 and abs(fileTime-presentTimeStamp)<preciseOrbitFleshTime:
                        # known objects in this file were already searched recently
                        isCorrectDirectory[i] = 1
                        directoryNames[i] = fileName
                    elif abs(ra-raList[i])<0.01 and abs(dec-decList[i])<0.01 and abs(jd-jdList[i])<0.00001 and abs(fileTime-presentTimeStamp)>preciseOrbitFleshTime:
                        # known objects in this file were searched but long ago
                        isCorrectDirectory[i] = 0
                        directoryNames[i] = fileName
    #-----------------------------------------------

    #---if presice orbit directory does not exist, make it-
    for i in range(Ndata):
        if isCorrectDirectory[i]==0 and directoryNames[i]=='a':
            directory = dirName + "/{0:d}".format(maxNumOrbitDirectories)
            os.mkdir(directory)
            isCorrectDirectory[i] = 0
            directoryNames[i] = directory
            maxNumOrbitDirectories += 1
    logFile = open(logFileName,"w",newline="\n")
    logFile.write(str(maxNumOrbitDirectories))
    logFile.close()
    #------------------------------------------------------

    #---output precise orbit directory information to current directory-
    preciseOrbitDirectoryFile = open("precise_orbit_directories.txt","w",newline="\n")
    haveAllPreciseOrbit = 1
    for i in range(Ndata):
        preciseOrbitDirectoryFile.write(directoryNames[i]+" {0:d}\n".format(isCorrectDirectory[i]))
        if isCorrectDirectory[i]==0:
            haveAllPreciseOrbit = 0
    preciseOrbitDirectoryFile.close()

    haveAllPreciseOrbitFile = open("have_all_precise_orbits.txt","w",newline="\n")
    haveAllPreciseOrbitFile.write(str(haveAllPreciseOrbit))
    haveAllPreciseOrbitFile.close()
    #-------------------------------------------------------------------

except FileNotFoundError:
    print("Some previous files are not found in search_precise_orbit_directories.py!")
    print(traceback.format_exc())
    error = 1
    errorReason = 24

except Exception:
    print("Some errors occur in search_precise_orbit_directories.py!")
    print(traceback.format_exc())
    error = 1
    errorReason = 25

else:
    error = 0
    errorReason = 24

finally:
    errorFile = open("error.txt","a")
    errorFile.write("{0:d} {1:d} 208 \n".format(error,errorReason))
    errorFile.close()
