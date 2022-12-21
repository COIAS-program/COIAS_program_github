#!/usr/bin/env python3
# -*- coding: UTF-8 -*
#Timestamp: 2022/08/06 21:00 sugiura
###########################################################################################
# カレントディレクトリのpre_repo3.txtを~/.coias/past_pre_repo_data/以下にコピーする.
# ただし, ファイル探索の高速化のためにこの画像の観測日のyyyy-mm-ddディレクトリ以下に保存する.
# del_duplicated_line_from_pre_repo2.pyの冒頭にも書いた理由から,
# ~/.coias/past_pre_repo_data/以下にコピーされたpre_repo3_*.txtの1行目には
# このファイルを作成したカレントディレクトリの絶対パスを記載しておく.
# また, pre_repo3_*.txtの重複保存を防ぐため, 同じカレントディレクトリで生成された
# pre_repo3_*.txtがあれば上書きで保存するようにする.
# さらに, 今回の観測で得られた新天体が違う日付の観測でどこにいるのか予測するために,
# ~/.coias/past_pre_repo_data/yyyy-mm-dd/coefficients_for_predict.txtに
# 各新天体のraとdecをjdに対して線形関数でフィットした時の係数を書き出す。
#
# 入力: warp01_bin.fits この画像のyyyy-mm-ddを取得するために使用
# 　　  ./pre_repo3.txt
# 出力: ~/.coias/past_pre_repo_data/yyyy-mm-dd/pre_repo3_*.txt
# 　　    ./pre_repo3.txtと内容は同じコピーだが,
# 　　    1行目にカレントディレクトリの絶対パスが記載されたもの.
# 　　  ~/.coias/past_pre_repo_data/yyyy-mm-dd/coefficients_for_predict.txt
# 　　    各新天体のra,decをjdに対して線形関数でフィットした時の係数を保存したもの.
# 　　    書式: 新天体名 raの勾配 raの切片 decの勾配 decの切片 以下フィットに用いた時刻をjdで表現したもの
###########################################################################################
import traceback
import os
import shutil
import glob
from astropy.io import fits
from astropy.time import Time
import numpy as np
import re
import changempc
import print_detailed_log
import PARAM

try:
    #---get yyyy-mm-dd of this measurement--------
    scidata = fits.open("warp01_bin.fits")
    jd = scidata[0].header['JD']
    tInTimeObj = Time(jd, format="jd")
    tInIso = tInTimeObj.iso
    yyyy_mm_dd = tInIso.split()[0]
    #---------------------------------------------

    #---check ~/.coias/past_pre_repo_data/yyyy-mm-dd directory exists or not
    dirName = PARAM.COIAS_DATA_PATH + "/past_pre_repo_data/" + yyyy_mm_dd
    logFileName = dirName + "/log.txt"
    if not os.path.isdir(dirName):
        os.mkdir(dirName)
        logFile = open(logFileName, "w", newline="\n")
        logFile.write("0")
        logFile.close()
    #-----------------------------------------------------------------------

    #---get maximum number of pre_repo3_*.txt-----
    logFile = open(logFileName, "r")
    maxFileN = int(logFile.readline())
    logFile.close
    #---------------------------------------------

    #---check the file produced from the same working directory exists or not
    currentDir = os.getcwd()
    compareFileNames = sorted(glob.glob(dirName + "/pre_repo3_*.txt"))
    duplicateFlag = False
    for fileName in compareFileNames:
        compareFile = open(fileName,"r")
        compareFileOrigin = compareFile.readlines()[0].rstrip("\n")
        compareFile.close()
        if compareFileOrigin==currentDir:
            newFileName = fileName
            duplicateFlag = True
    if not duplicateFlag:
        maxFileN += 1
        newFileName = dirName + "/pre_repo3_{0:d}.txt".format(maxFileN)
    #------------------------------------------------------------------------

    #---output maxFileN to log.txt and copy pre_repo3.txt--------------------
    logFile = open(logFileName, "w", newline="\n")
    logFile.write(str(maxFileN))
    logFile.close()

    preRepoInputFile = open("pre_repo3.txt","r")
    inputLines = preRepoInputFile.readlines()
    preRepoInputFile.close()

    preRepoOutputFile = open(newFileName, "w", newline="\n")
    preRepoOutputFile.write(currentDir+"\n")
    preRepoOutputFile.writelines(inputLines)
    preRepoOutputFile.close()
    #------------------------------------------------------------------------

    #---calculate coefficients for linear fit of jd vs ra and dec------------
    warpFileNames = sorted(glob.glob("warp*_bin.fits"))
    scidata = fits.open(warpFileNames[0])
    jdFirst = scidata[0].header["JD"]
    scidata = fits.open(warpFileNames[len(warpFileNames)-1])
    jdLast  = scidata[0].header["JD"]
    
    coeffFileName = dirName + "/coefficients_for_predict.txt"
    if os.path.isfile(coeffFileName):
        f = open(coeffFileName,"r")
        pastCoeffAndJdList = f.readlines()
        f.close()
    else:
        pastCoeffAndJdList = []

    f = open("pre_repo3.txt","r")
    dataLines = f.readlines()
    f.close()

    ### calculate coefficients ##############################################
    coeffAndJdList = []
    if os.stat("pre_repo3.txt").st_size != 0:
        prevObsName = dataLines[0].split()[0]
        jdList = []
        raList = []
        decList = []
        for l in range(len(dataLines)):
            if dataLines[l].split()[0]!= prevObsName or len(dataLines[l].split())==0 or l==len(dataLines)-1:
                if l==len(dataLines)-1:
                    jdList.append( changempc.change_datetime_in_MPC_to_jd(dataLines[l][14:31]) )
                    raList.append( changempc.change_ra_in_MPC_to_degree(dataLines[l][32:43]) )
                    decList.append( changempc.change_dec_in_MPC_to_degree(dataLines[l][44:55]) )

                raCoef = np.polyfit(jdList, raList, 1)
                decCoef = np.polyfit(jdList, decList, 1)
                outputLine = prevObsName + " " + "{0:.8e}".format(raCoef[0]) + " " + "{0:.8e}".format(raCoef[1]) + " " + "{0:.8e}".format(decCoef[0]) + " " + "{0:.8e} ".format(decCoef[1])
                for j in range(len(jdList)):
                    outputLine = outputLine + "{0:.4f} ".format(jdList[j])
                outputLine = outputLine + "\n"
                if re.search(r"^H......",prevObsName)!=None:
                    coeffAndJdList.append(outputLine)

                jdList = [changempc.change_datetime_in_MPC_to_jd(dataLines[l][14:31])]
                raList = [changempc.change_ra_in_MPC_to_degree(dataLines[l][32:43])]
                decList = [changempc.change_dec_in_MPC_to_degree(dataLines[l][44:55])]

            else:
                jdList.append( changempc.change_datetime_in_MPC_to_jd(dataLines[l][14:31]) )
                raList.append( changempc.change_ra_in_MPC_to_degree(dataLines[l][32:43]) )
                decList.append( changempc.change_dec_in_MPC_to_degree(dataLines[l][44:55]) )

            prevObsName = dataLines[l].split()[0]
    ########################################################################
                
    ### compare coeffAndJdList and pastCoeffAndJdList ###########################
    ### if one data in coeffAndJdList coincides with that in pastCoeffAndJdList #
    ### add jds not in pastCoeffAndJdList and overwrite pastCoeffAndJdList ######
    ### if not, add that data in coeffAndJdList to pastCoeffAndJdList ###########
    for lPresent in range(len(coeffAndJdList)):
        matchFlag = False
        for lPast in range(len(pastCoeffAndJdList)):
            presentFirstRa  = float(coeffAndJdList[lPresent].split()[1]) * jdFirst + float(coeffAndJdList[lPresent].split()[2])
            presentFirstDec = float(coeffAndJdList[lPresent].split()[3]) * jdFirst + float(coeffAndJdList[lPresent].split()[4])
            presentLastRa   = float(coeffAndJdList[lPresent].split()[1]) * jdLast  + float(coeffAndJdList[lPresent].split()[2])
            presentLastDec  = float(coeffAndJdList[lPresent].split()[3]) * jdLast  + float(coeffAndJdList[lPresent].split()[4])
            
            pastFirstRa     = float(pastCoeffAndJdList[lPast].split()[1]) * jdFirst + float(pastCoeffAndJdList[lPast].split()[2])
            pastFirstDec    = float(pastCoeffAndJdList[lPast].split()[3]) * jdFirst + float(pastCoeffAndJdList[lPast].split()[4])
            pastLastRa      = float(pastCoeffAndJdList[lPast].split()[1]) * jdLast  + float(pastCoeffAndJdList[lPast].split()[2])
            pastLastDec     = float(pastCoeffAndJdList[lPast].split()[3]) * jdLast  + float(pastCoeffAndJdList[lPast].split()[4])

            if abs(presentFirstRa  - pastFirstRa) <2.0/3600.0 and \
               abs(presentFirstDec - pastFirstDec)<2.0/3600.0 and \
               abs(presentLastRa   - pastLastRa)  <2.0/3600.0 and \
               abs(presentLastDec  - pastLastDec) <2.0/3600.0:
                ### match
                matchFlag = True
                presentContents = coeffAndJdList[lPresent].split()
                presentJdList   = presentContents[5:len(presentContents)]
                pastContents    = pastCoeffAndJdList[lPast].split()
                pastJdList      = pastContents[5:len(pastContents)]

                pastContents[0] = presentContents[0]
                newPastCoeffAndJdList = " ".join(pastContents)
                for jd in presentJdList:
                    if jd not in pastJdList:
                        newPastCoeffAndJdList = newPastCoeffAndJdList + " " + jd
                newPastCoeffAndJdList = newPastCoeffAndJdList + "\n"
                pastCoeffAndJdList[lPast] = newPastCoeffAndJdList
                break

        if matchFlag==False:
            pastCoeffAndJdList.append( coeffAndJdList[lPresent] )
    ############################################################################

    ### output
    fileOutput = open(coeffFileName,"w",newline="\n")
    fileOutput.writelines(pastCoeffAndJdList)
    fileOutput.close()
    
    #------------------------------------------------------------------------
    
except FileNotFoundError:
    print("Some previous files are not found in del_duplicated_line_from_pre_repo2.py!",flush=True)
    print(traceback.format_exc(),flush=True)
    error = 1
    errorReason = 74

except Exception:
    print("Some errors occur in del_duplicated_line_from_pre_repo2.py!",flush=True)
    print(traceback.format_exc(),flush=True)
    error = 1
    errorReason = 75

else:
    error = 0
    errorReason = 74

finally:
    errorFile = open("error.txt","a")
    errorFile.write("{0:d} {1:d} 712 \n".format(error,errorReason))
    errorFile.close()

    if error==1:
        print_detailed_log.print_detailed_log(dict(globals()))
