#!/usr/bin/env python3
# -*- coding: UTF-8 -*
#Timestamp: 2022/08/04 16:00 sugiura
#############################################################################
# precise_orbit_directories.txtに記載のディレクトリ以下に存在する
# 視野内の確定番号付き小惑星の精密位置情報(numbered_new2B.txt)と
# 仮符号小惑星のそれ(karifugo_new2B.txt)に多少の編集作業を行って,
# マージすることによって各ディレクトリ以下にsearch_astB.txtを作成する.
#
# 入力: precise_orbit_directories.txtに記載のディレクトリ/numbered_new2B.txt
# 　　  precise_orbit_directories.txtに記載のディレクトリ/karifugo_new2B.txt
# 　　　  書式: 確定番号or仮符号 jd ra[degree] dec[degree] mag
# 出力: precise_orbit_directories.txtに記載のディレクトリ/search_astB.txt
# 　　    入力の2つのファイルに多少の編集作業を行ってマージしたもの.
#############################################################################
import subprocess
import traceback
import os

try:
    #---read precise_orbit_directories.txt---------------------------------------
    directoryNames = []
    isCorrectDirectory = []
    preciseOrbitDirectoriesFile = open("precise_orbit_directories.txt","r")
    lines = preciseOrbitDirectoriesFile.readlines()
    Ndata = len(lines)
    for line in lines:
        content = line.split()
        directoryNames.append(content[0])
        isCorrectDirectory.append(int(content[1]))
    preciseOrbitDirectoriesFile.close()
    #----------------------------------------------------------------------------

    #---process numbered_new2B.txt and karifugo_new2B.txt in each directory------
    errorList=[]
    for i in range(Ndata):
        if isCorrectDirectory[i]==0:
            completed_process = subprocess.run("grep -E \"^19|^20\" {0}/karifugo_new2B.txt > {0}/karifugo_new2C.txt".format(directoryNames[i]),shell=True)
            if (not os.path.isfile(directoryNames[i]+"/karifugo_new2B.txt")) or (os.stat(directoryNames[i]+"/karifugo_new2B.txt").st_size!=0):
                errorList.append(completed_process.returncode)
            completed_process = subprocess.run("cat {0}/numbered_new2B.txt {0}/karifugo_new2C.txt |sort -n > {0}/search_astpre.txt".format(directoryNames[i]),shell=True)
            errorList.append(completed_process.returncode)
            completed_process = subprocess.run("sed 's/--/30.0/g;' {0}/search_astpre.txt |sed 's/ (1999 19 //g;' |sed 's/ (1981 2 //g;'|sed 's/ - / /g;'> {0}/search_astB.txt".format(directoryNames[i]),shell=True)
            errorList.append(completed_process.returncode)

    for e in errorList:
        if e!=0:
            raise FileNotFoundError
    #----------------------------------------------------------------------------

except FileNotFoundError:
    print("Some previous files are not found in make_search_astB_in_each_directory.py!")
    print(traceback.format_exc())
    error = 1
    errorReason = 44

except Exception:
    print("Some errors occur in make_search_astB_in_each_directory.py!")
    print(traceback.format_exc())
    error = 1
    errorReason = 45

else:
    error = 0
    errorReason = 44

finally:
    errorFile = open("error.txt","a")
    errorFile.write("{0:d} {1:d} 403 \n".format(error,errorReason))
    errorFile.close()
