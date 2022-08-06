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
#
# 入力: warp01_bin.fits この画像のyyyy-mm-ddを取得するために使用
# 　　  ./pre_repo3.txt
# 出力: ~/.coias/past_pre_repo_data/yyyy-mm-dd/pre_repo3_*.txt
# 　　    ./pre_repo3.txtと内容は同じコピーだが,
# 　　    1行目にカレントディレクトリの絶対パスが記載されたもの.
###########################################################################################
import traceback
import os
import shutil
import glob
from astropy.io import fits
from astropy.time import Time

try:
    #---get yyyy-mm-dd of this measurement--------
    scidata = fits.open("warp01_bin.fits")
    jd = scidata[0].header['JD']
    tInTimeObj = Time(jd, format="jd")
    tInIso = tInTimeObj.iso
    yyyy_mm_dd = tInIso.split()[0]
    #---------------------------------------------

    #---check ~/.coias/past_pre_repo_data/yyyy-mm-dd directory exists or not
    dirName = os.path.expanduser("~") + "/.coias/past_pre_repo_data/" + yyyy_mm_dd
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

    
except FileNotFoundError:
    print("Some previous files are not found in del_duplicated_line_from_pre_repo2.py!")
    print(traceback.format_exc())
    error = 1
    errorReason = 74

except Exception:
    print("Some errors occur in del_duplicated_line_from_pre_repo2.py!")
    print(traceback.format_exc())
    error = 1
    errorReason = 75

else:
    error = 0
    errorReason = 74

finally:
    errorFile = open("error.txt","a")
    errorFile.write("{0:d} {1:d} 712 \n".format(error,errorReason))
    errorFile.close()
