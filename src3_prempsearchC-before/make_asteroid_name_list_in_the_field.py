#!/usr/bin/env python3
# -*- coding: UTF-8 -*
#Timestamp: 2022/08/04 14:30 sugiura
#################################################################################
# 明るい(15等級以上になりうる)小惑星は軌道が十分に分かっているため報告の必要はない.
# レポート前処理で明るい天体を弾くために, そのリストを作成しておく.
#
# 入力: bright_asteroid_raw_names_in_the_field.txt
# 　　    視野内の明るい既知小惑星の名前を縦に並べたもの
# 出力: precise_orbit_directories.txtに記載のディレクトリ/bright_asteroid_MPC_names_in_the_field.txt
# 　　    視野内の明るい既知小惑星のMPC形式の名前を縦に並べたもの
#################################################################################
import subprocess
import re
import numpy as np
import traceback
import print_detailed_log
from changempc import *


try:
    #---read precise_orbit_directories.txt------------------------------------------------------
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
    #-------------------------------------------------------------------------------------------

    #---make bright asteroid MPC name list in each directory------------------------------------
    errorList=[]
    ## remove a character "\"
    completed_process = subprocess.run(r"sed -e 's/\\//g' bright_asteroid_raw_names_in_the_field.txt > bright_asteroid_raw_names_in_the_field2.txt",shell=True)
    errorList.append(completed_process.returncode)
    ## subtract number from numbered asteroids and karifugo from karifugo asteroids
    completed_process = subprocess.run("awk -F' ' '{if( ( ($1 ~ /^18[0-9][0-9]$/ || $1 ~ /^19[0-9][0-9]$/ || $1 ~ /^20[0-9][0-9]$/) && $2 ~ /^[A-Z][A-Z][0-9]*$/ ) || $2 == 'P-L' || $2 == 'T-1' || $2 == 'T-2' || $2 == 'T-3' ){print $1,$2}else{print $1}}' bright_asteroid_raw_names_in_the_field2.txt > bright_asteroid_raw_names_in_the_field3.txt",shell=True)
    errorList.append(completed_process.returncode)
    ## remove space between karifugo
    completed_process = subprocess.run("sed 's/ //g' bright_asteroid_raw_names_in_the_field3.txt > bright_asteroid_raw_names_in_the_field4.txt",shell=True)
    errorList.append(completed_process.returncode)

    for e in errorList:
        if e!=0:
            raise FileNotFoundError

    ## transform to MPC format name
    inputFile = open("bright_asteroid_raw_names_in_the_field4.txt","r")
    lines = inputFile.readlines()
    inputFile.close()
    brightAsteroidsMPCNames = []
    for l in range(len(lines)):
        if re.search(r'[a-zA-Z]',lines[l]):
            brightAsteroidsMPCNames.append(get_MPC_format_name_for_karifugo_asteroids(lines[l].rstrip("\n")))
        else:
            brightAsteroidsMPCNames.append(get_MPC_format_name_for_numbered_asteroids(lines[l].rstrip("\n")))

    ## output to each directory
    for n in range(Ndata):
        outputFile = open(directoryNames[n]+"/bright_asteroid_MPC_names_in_the_field.txt","w",newline="\n")
        for l in range(len(brightAsteroidsMPCNames)):
            outputFile.write(brightAsteroidsMPCNames[l]+"\n")
        outputFile.close()
    #-------------------------------------------------------------------------------------------


except FileNotFoundError:
    print("Some previous files are not found in make_asteroid_name_list_in_the_field.py!",flush=True)
    print(traceback.format_exc(),flush=True)
    error = 1
    errorReason = 34

except Exception:
    print("Some errors occur in make_asteroid_name_list_in_the_field.py!",flush=True)
    print(traceback.format_exc(),flush=True)
    error = 1
    errorReason = 35

else:
    error = 0
    errorReason = 34

finally:
    errorFile = open("error.txt","a")
    errorFile.write("{0:d} {1:d} 313 \n".format(error,errorReason))
    errorFile.close()

    if error==1:
        print_detailed_log.print_detailed_log(dict(globals()))
