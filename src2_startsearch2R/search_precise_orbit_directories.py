#!/usr/bin/env python3
# -*- coding: UTF-8 -*
#Timestamp: 2022/08/04 13:30 sugiura
#########################################################################
# prempsearchC-beforeとafterで行われる視野内既知天体の精密位置取得は,
# tractとjdが同じであれば1度実行すればよく, patchが違っても適用可能である.
# 過去にJPLに問い合わせて得た視野内の既知天体の精密位置は,
# ~/.coias/orbit_data/観測日yyyy-mm-dd/連番ディレクトリ に保存されている.
# このスクリプトではprempsearchCを実行する前に, 視野が同じかつ同じjdの
# 視野内既知天体の精密位置情報を持ったディレクトリを探す.
# 情報が古すぎる場合は精密位置を取得し直す必要があるので, その判定もする.
# そのようなディレクトリがなかった場合は新たな連番ディレクトリを作成だけする.
# 各ディレクトリの作成時刻及びそのディレクトリが保持する精密位置のjdと視野中心は
# 各ディレクトリ直下のra_dec_jd_time.txtに記載してある. (このファイルの作成はgetinfo_karifugo2D.pyで行う)
#
# 入力: warp*_bin.fits (画像の観測日jdと画像中心のra, decを取得するだけ)
# 出力: precise_orbit_directories.txt
# 　　    書式: n列目はn番目の画像に関する情報で
# 　　    [精密位置を格納したorするディレクトリ] [利用可能な精密位置情報があるか 1ある 0ない]
# 　　  have_all_precise_orbits.txt
# 　　    全ての画像に対して利用可能な精密位置情報があるかどうか
# 　　    全てあるときこのファイルには1とだけ書かれる, どれかなければ0になる
# 　　    このファイルに1が書き込まれているとき, prempsearchCは実行しなくても
# 　　    よいということなので, 1の時はprempsearchCは飛ばされるようになっている.
# 　　  formatted_time_list.txt
# 　　    n列目にwarp[n]_bin.fitsのUTC時刻をyyyy-mm-dd HH:MM:SSの形式で書き出したもの.
#########################################################################
import os
import glob
import time
import shutil
from astropy.io import fits
from astropy.time import Time
import traceback
import print_detailed_log
from def_coias_data_path import *

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

    #---write out yyyy-mm-dd HH:MM:SS of warp files to the file----
    f = open("formatted_time_list.txt","w")
    for i in range(Ndata):
        tInTimeObj = Time(jdList[i], format="jd")
        tInIso = tInTimeObj.iso
        formattedTimeStr = tInIso.split(".")[0]
        f.write(formattedTimeStr + "\n")
    f.close()
    #--------------------------------------------------------------

    #---if directory ~/.coias/orbit_data/yyyy_mm_dd does not exist-
    #---we produce it----------------------------------------------
    dirName = coiasDataPath + "/orbit_data/" + yyyy_mm_dd
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
    print("Some previous files are not found in search_precise_orbit_directories.py!",flush=True)
    print(traceback.format_exc(),flush=True)
    error = 1
    errorReason = 24

except Exception:
    print("Some errors occur in search_precise_orbit_directories.py!",flush=True)
    print(traceback.format_exc(),flush=True)
    error = 1
    errorReason = 25

else:
    error = 0
    errorReason = 24

finally:
    errorFile = open("error.txt","a")
    errorFile.write("{0:d} {1:d} 208 \n".format(error,errorReason))
    errorFile.close()

    if error==1:
        print_detailed_log.print_detailed_log(dict(globals()))
