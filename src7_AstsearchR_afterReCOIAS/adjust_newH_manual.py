#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#Timestamp: 2022/08/06 19:00 sugiura
###########################################################################################
# 通常, searchモードで自動検出天体を選んだ後にmanual measureモードにて手動測定を行うと,
# AstsearchR_between_COIAS_and_ReCOIASおよびAstsearchR_after_manualを正常に動作させれば,
# 自動検出天体のH番号から手動測定天体のH番号まで連番になっているはずである.
# ただし, manual_measureモードを終えた後に再びsearchモードにて変更を行い,
# AstsearchR_after_manualを動作させない場合は番号に重複が起きてしまう.
# このスクリプトでは, やり直しを繰り返す過程でそのようなことが起きた場合にも連番になる
# ように手動測定天体のH番号を(必要があれば)振り直す.
#
# 入力: redisp.txt 自動検出天体のH番号の最大値を取得するために使用
# 　　  redisp_manual.txt 手動測定天体のH番号の最小値を取得する
# H番号が連番になっていなかったら, 連番になるように以下のファイルを書き換える
# 　　  H_conversion_list_manual.txt
# 　　  mpc4_m.txt
# 　　  newall_m.txt
# 　　  redisp_manual.txt
###########################################################################################
import re
import os
import traceback

class NothingToDo(Exception):
    pass

try:
    #---assess manual mode is done or not-----------
    if (not os.path.isfile("mpc4_m.txt")) or (not os.path.isfile("H_conversion_list_manual.txt")) or (not os.path.isfile("redisp_manual.txt")) or (not os.path.isfile("newall_m.txt")):
        raise NothingToDo
    #------------------------------------------------
    
    
    #---get maximum H number from redisp.txt---------
    redispFile = open("redisp.txt","r")
    lines = redispFile.readlines()
    redispFile.close()

    NHMax = 0
    for line in lines:
        contents = line.split()
        if re.search(r'^H......',contents[0])!=None:
            NH = int(contents[0].lstrip("H"))
            if NH > NHMax:
                NHMax = NH
    #------------------------------------------------


    #---assess where Hmax in redisp.txt is one smaller than HMin in redisp_manual.txt
    redispManualFile = open("redisp_manual.txt","r")
    lines = redispManualFile.readlines()
    redispManualFile.close()

    NHMin = 100000000 #VERY LARGE VALUE
    for line in lines:
        contents = line.split()
        if re.search(r'^H......',contents[0])!=None:
            NH = int(contents[0].lstrip("H"))
            if NH < NHMin:
                NHMin = NH

    ## if HMax in redisp.txt is one smaller than HMin in redisp_manual.txt,
    ## then H numbers become sequential and it's OK
    if NHMax + 1 == NHMin:
        raise NothingToDo
    #------------------------------------------------


    #---get adjusted new H list----------------------
    newHList = []
    adjustedNewHList = []

    fileHConvListManual = open("H_conversion_list_manual.txt","r")
    lines = fileHConvListManual.readlines()
    fileHConvListManual.close()

    k = 1
    for line in lines:
        newHList.append(line.split()[1])
        adjustedNewHList.append("H"+str(NHMax+k).rjust(6, '0'))
        k += 1
    #------------------------------------------------

    
    #---adjust H_conversion_list_manual.txt, mpc4_m.txt, newall_m.txt, and redisp_manual.txt
    ## H_conversion_list_manual.txt
    fileHConvListManual = open("H_conversion_list_manual.txt","w",newline="\n")
    for line in lines:
        for l in range(len(adjustedNewHList)):
            if line.split()[1] == newHList[l]:
                newline = line.split()[0] + " " + adjustedNewHList[l] + "\n"
                break
        fileHConvListManual.write(newline)
    fileHConvListManual.close()

    ## mpc4_m.txt
    fileMpc4M = open("mpc4_m.txt","r")
    lines = fileMpc4M.readlines()
    fileMpc4M.close()

    fileMpc4M = open("mpc4_m.txt","w",newline="\n")
    for line in lines:
        if len(adjustedNewHList)==0:
            fileMpc4M.write(line)
        else:
            for l in range(len(adjustedNewHList)):
                if line.split()[0] == newHList[l]:
                    break
            fileMpc4M.write(line.replace(newHList[l],adjustedNewHList[l]))
    fileMpc4M.close()

    ## newall_m.txt
    fileNewallM = open("newall_m.txt","r")
    lines = fileNewallM.readlines()
    fileNewallM.close()

    fileNewallM = open("newall_m.txt","w",newline="\n")
    for line in lines:
        if len(adjustedNewHList)==0:
            fileNewallM.write(line)
        else:
            for l in range(len(adjustedNewHList)):
                if line.split()[0] == newHList[l]:
                    break
            fileNewallM.write(line.replace(newHList[l],adjustedNewHList[l]))
    fileNewallM.close()

    ## redisp_manual.txt
    fileRedispM = open("redisp_manual.txt","r")
    lines = fileRedispM.readlines()
    fileRedispM.close()

    fileRedispM = open("redisp_manual.txt","w",newline="\n")
    for line in lines:
        if len(adjustedNewHList)==0:
            fileRedispM.write(line)
        else:
            for l in range(len(adjustedNewHList)):
                if line.split()[0] == newHList[l]:
                    break
            fileRedispM.write(line.replace(newHList[l],adjustedNewHList[l]))
    fileRedispM.close()
    #------------------------------------------------

except NothingToDo:
    error = 0
    errorReason = 74

except FileNotFoundError:
    print("Some previous files are not found in adjust_newH_manual.py!")
    print(traceback.format_exc())
    error = 1
    errorReason = 74

except Exception:
    print("Some errors occur in adjust_newH_manual.py!")
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
