#!/usr/bin/env python3
# -*- coding: UTF-8 -*
#Timestamp: 2022/08/06 20:00 sugiura
###########################################################################################
# findorbで計算された残差が0.7"以上のデータ点は削除され, それによってデータ点が2行以下になった
# 天体は報告ファイルから除外される.
# これによって欠番が生じてH番号が連番ではなくなる可能性があるので,
# このスクリプトでは最終的に連番になるようにさらにH番号の付け替えを行う.
# 連番の開始値は, AstsearchR_between_COIAS_and_ReCOIASで第二引数を指定した場合はその数値,
# 指定しなかった場合はこの時点での~/.coias/param/max_H_number.txtに記載の数値になる.
# また, 名前修正モードで過去の測定での新天体とH番号を揃えるように修正した場合はその番号は付け替えたくない.
# 通常そのような番号は今回の測定で指定したH暗号の開始値よりも若いので,
# そのような若い番号は今回の付け替えの対象としない.
#
# 入力: pre_repo2.txt
# 　　  H_conversion_list_automanual2.txt
# 　　  start_H_number.txt 今回の測定で指定されたH番号の開始値と, AstsearchR_between_COIAS_and_ReCOIASの実行時に第二引数が指定されたかどうかを知るために使用.
# 　　  max_H_number.txt 今現在の全ユーザーに測定された新天体のうちH番号の最大値を知るために使用.
# 出力: pre_repo3.txt
# 　　    最終的にH番号が連番になるように名前が付け替えられたもの
# 　　  H_conversion_list_automanual3.txt
# 　　    H_conversion_list_automanual2.txtに記載の3列目までの名前の付け替え履歴に加え,
# 　　    4列目にこのスクリプトでの名前の付け替えの結果が追加される.
# 　　    残差が大きいなどの理由で消えてしまった天体は4列目に rejected と記載される.
###########################################################################################
import traceback
import os
import re
import subprocess
from def_coias_data_path import *

try:
    completed_process = subprocess.run("sort -n -o pre_repo2.txt pre_repo2.txt", shell=True)
    if completed_process.returncode!=0: raise Exception

    #---get H conversion list from pre repo-----------------------
    filePreRepo = open("pre_repo2.txt","r")
    lines = filePreRepo.readlines()
    filePreRepo.close()

    ### set kinit #########################
    f = open("start_H_number.txt","r")
    line = f.readline()
    f.close()
    startHNumberThisTime = int(line.split()[0])
    isManual = int(line.split()[1])

    maxHFileName = coiasDataPath + "/param/max_H_number.txt"
    f = open(maxHFileName,"r")
    line = f.readline()
    f.close()
    maxHNumber = int(line.split()[0])
    maxHDir = line.split()[1]

    if isManual or maxHDir==os.getcwd():
        kinit = startHNumberThisTime
    else:
        kinit = maxHNumber
    #######################################

    HOldNameList = []
    HNewNameList = []
    k=0
    for line in lines:
        thisName = line.split()[0]
        if (re.search(r'^H......', thisName)!=None) and (thisName not in HOldNameList):
            if int(thisName.lstrip("H")) < startHNumberThisTime:
                newName = thisName
                newFlag = False
            else:
                newName = "H"+str(kinit+k).rjust(6,"0")
                newFlag = True
            
            HOldNameList.append(thisName)
            HNewNameList.append(newName)
            if newFlag:
                k += 1
    #-------------------------------------------------------------


    #---add this conversion to H_conversion_list_automanual2.txt--
    fileHConversionList2 = open("H_conversion_list_automanual2.txt","r")
    lines = fileHConversionList2.readlines()
    fileHConversionList2.close()

    fileHConversionList3 = open("H_conversion_list_automanual3.txt","w",newline="\n")
    for line in lines:
        if re.search(r'^H......', line.split()[2])==None:
            fileHConversionList3.write(line.rstrip("\n") + " " + line.split()[2] + "\n")
        elif line.split()[2] not in HOldNameList:
            fileHConversionList3.write(line.rstrip("\n") + " " + "rejected \n")
        else:
            for l in range(len(HOldNameList)):
                if line.split()[2]==HOldNameList[l]:
                    fileHConversionList3.write(line.rstrip("\n") + " " + HNewNameList[l] + "\n")
                    break
    fileHConversionList3.close()
    #-------------------------------------------------------------


    #---modify pre_repo.txt as H numbers become sequential--------
    filePreRepo = open("pre_repo2.txt","r")
    lines = filePreRepo.readlines()
    filePreRepo.close()

    filePreRepo2 = open("pre_repo3.txt","w",newline="\n")
    for line in lines:
        isMatch = False
        for l in range(len(HOldNameList)):
            if line.split()[0]==HOldNameList[l]:
                isMatch = True
                filePreRepo2.write(line.replace(HOldNameList[l], HNewNameList[l]))
                break
        if not isMatch:
            filePreRepo2.write(line)
    filePreRepo2.close()
    #-------------------------------------------------------------
    
    
except FileNotFoundError:
    print("Some previous files are not found in modify_preRepo_as_H_sequential!")
    print(traceback.format_exc())
    error = 1
    errorReason = 74

except Exception:
    print("Some errors occur in modify_preRepo_as_H_sequential!")
    print(traceback.format_exc())
    error = 1
    errorReason = 75

else:
    error = 0
    errorReason = 74

finally:
    errorFile = open("error.txt","a")
    errorFile.write("{0:d} {1:d} 710 \n".format(error,errorReason))
    errorFile.close()
