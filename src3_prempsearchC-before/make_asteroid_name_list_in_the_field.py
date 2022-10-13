#!/usr/bin/env python3
# -*- coding: UTF-8 -*
#Timestamp: 2022/08/04 14:30 sugiura
#################################################################################
# 明るい(15等級以上になりうる)小惑星は軌道が十分に分かっているため報告の必要はない.
# レポート前処理で明るい天体を弾くために, そのリストを作成しておく.
# また将来的にGUIで小惑星の名前をMPCフォーマットではなく生の名前で見たくなったときのために,
# 視野内の既知天体の名前(フルネームとMPCフォーマットの名前)の一覧を作っておく.
#
# 入力: bright_asteroid_raw_names_in_the_field.txt
# 　　    視野内の明るい既知小惑星の名前を縦に並べたもの
# 　　  cand2b.txt
# 　　    視野内の全ての既知小惑星の大雑把な情報
# 出力: precise_orbit_directories.txtに記載のディレクトリ/bright_asteroid_MPC_names_in_the_field.txt
# 　　    視野内の明るい既知小惑星のMPC形式の名前を縦に並べたもの
# 　　  precise_orbit_directories.txtに記載のディレクトリ/name_conversion_list_in_the_field.txt
# 　　    視野内の全ての既知小惑星の名前の一覧
# 　　    書式: フルネーム, 確定番号or仮符号, MPC形式の名前
#################################################################################
import subprocess
import re
import numpy as np
import traceback
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
    completed_process = subprocess.run("awk -F' ' '( $1 ~ /^[1-9]/ && $2 ~ /^[A-Z]/ && $2 !~ /[A-Z][A-Z][0-9]*/ && $2 != 'P-L' && $2 != 'T-1' && $2 != 'T-2' && $2 != 'T-3' ) || $2 ~ /[A-Z][A-Z][A-Z]/ {print $1}' bright_asteroid_raw_names_in_the_field2.txt > bright_asteroid_raw_names_in_the_field3.txt",shell=True)
    errorList.append(completed_process.returncode)
    completed_process = subprocess.run("awk -F' ' '$1 ~ /^[1-9]/ && $2 ~ /^[1-2]/ || $3 == 'P-L' || $3 == 'T-1' || $3 == 'T-2' || $3 == 'T-3' {print $1}' bright_asteroid_raw_names_in_the_field2.txt >> bright_asteroid_raw_names_in_the_field3.txt",shell=True)
    errorList.append(completed_process.returncode)
    completed_process = subprocess.run("awk -F' ' '( $1 ~ /^[1-2]/ && $2 ~ /[A-Z][A-Z][0-9]*/ || $2 == 'P-L' || $2 == 'T-1' || $2 == 'T-2' || $2 == 'T-3' ) && $2 !~ /[A-Z][A-Z][A-Z]/  {print $1,$2}' bright_asteroid_raw_names_in_the_field2.txt >> bright_asteroid_raw_names_in_the_field3.txt",shell=True)
    errorList.append(completed_process.returncode)
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

    #---make name conversion list of all known asteroids in the field in each directory---------
    ## subtract number and name from numbered and karifugo asteroids
    completed_process = subprocess.run("awk -F' ' '( $2 ~ /^[1-9]/ && $3 ~ /^[A-Z]/ && $3 !~ /[A-Z][A-Z][0-9]*/ && $3 != 'P-L' && $3 != 'T-1' && $3 != 'T-2' && $3 != 'T-3' ) || $3 ~ /[A-Z][A-Z][A-Z]/ {print $2,$3}' cand2b.txt > candNameList_numbered_named.txt",shell=True)
    errorList.append(completed_process.returncode)
    completed_process = subprocess.run("awk -F' ' '$2 ~ /^[1-9]/ && $3 ~ /^[1-2]/ || $4 == 'P-L' || $4 == 'T-1' || $4 == 'T-2' || $4 == 'T-3' {print $2,$3,$4}' cand2b.txt > candNameList_numbered_unnamed.txt",shell=True)
    errorList.append(completed_process.returncode)
    completed_process = subprocess.run("awk -F' ' '( $2 ~ /^[1-2]/ && $3 ~ /[A-Z][A-Z][0-9]*/ || $3 == 'P-L' || $3 == 'T-1' || $3 == 'T-2' || $3 == 'T-3' ) && $3 !~ /[A-Z][A-Z][A-Z]/ {print $2,$3}' cand2b.txt > candNameList_karifugo.txt",shell=True)
    errorList.append(completed_process.returncode)

    for e in errorList:
        if e!=0:
            raise FileNotFoundError

    ## for numbered and named asteroids
    numberedNamedFullName = np.loadtxt("candNameList_numbered_named.txt",dtype='str',ndmin=2)
    numberedNamedShortName = []
    numberedNamedMPCName = []
    for l in range(len(numberedNamedFullName)):
        numberedNamedShortName.append(numberedNamedFullName[l][0])
        numberedNamedMPCName.append(get_MPC_format_name_for_numbered_asteroids(numberedNamedFullName[l][0]))

    ## for numbered and unnamed asteroids
    numberedUnnamedFullName = np.loadtxt("candNameList_numbered_unnamed.txt",dtype='str',ndmin=2)
    numberedUnnamedShortName = []
    numberedUnnamedMPCName = []
    for l in range(len(numberedUnnamedFullName)):
        numberedUnnamedShortName.append(numberedUnnamedFullName[l][0])
        numberedUnnamedMPCName.append(get_MPC_format_name_for_numbered_asteroids(numberedUnnamedFullName[l][0]))

    ## for karifugo asteroids
    karifugoFullName = np.loadtxt("candNameList_karifugo.txt",dtype='str',ndmin=2)
    karifugoShortName = []
    karifugoMPCName = []
    for l in range(len(karifugoFullName)):
        karifugoShortName.append(karifugoFullName[l][0]+karifugoFullName[l][1])
        karifugoMPCName.append(get_MPC_format_name_for_karifugo_asteroids(karifugoShortName[l]))

    ## output to each directory
    for n in range(Ndata):
        outputFile = open(directoryNames[n]+"/name_conversion_list_in_the_field.txt","w",newline="\n")
        for l in range(len(numberedNamedFullName)):
            outputFile.write(numberedNamedFullName[l][0]+" "+numberedNamedFullName[l][1]+","+numberedNamedShortName[l]+","+numberedNamedMPCName[l]+"\n")
        for l in range(len(numberedUnnamedFullName)):
            outputFile.write(numberedUnnamedFullName[l][0]+" "+numberedUnnamedFullName[l][1]+" "+numberedUnnamedFullName[l][2]+","+numberedUnnamedShortName[l]+","+numberedUnnamedMPCName[l]+"\n")
        for l in range(len(karifugoFullName)):
            outputFile.write(karifugoFullName[l][0]+" "+karifugoFullName[l][1]+","+karifugoShortName[l]+","+karifugoMPCName[l]+"\n")
        outputFile.close()
    #-------------------------------------------------------------------------------------------

except FileNotFoundError:
    print("Some previous files are not found in make_asteroid_name_list_in_the_field.py!")
    print(traceback.format_exc())
    error = 1
    errorReason = 34

except Exception:
    print("Some errors occur in make_asteroid_name_list_in_the_field.py!")
    print(traceback.format_exc())
    error = 1
    errorReason = 35

else:
    error = 0
    errorReason = 34

finally:
    errorFile = open("error.txt","a")
    errorFile.write("{0:d} {1:d} 313 \n".format(error,errorReason))
    errorFile.close()
