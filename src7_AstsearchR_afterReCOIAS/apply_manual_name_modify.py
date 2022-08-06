#!/usr/bin/env python3
# -*- coding: UTF-8 -*
#Timestamp: 2022/08/06 19:30 sugiura
###########################################################################################
# COIAS.pyのmodify nameモードで設定した名前の付け替えを適用する.
# manual_name_modify_list.txtには, 全ての自動検出天体と手動測定天体に対して,
# modify nameモードで付け替えられる前の名前(1列目)と付け替えられた後の名前(2列目)が列挙されている.
# (付け替えが起きない場合は1列目と2列目に同じ名前が記載される, このファイルが存在しない場合も付け替えなし)
# このスクリプトではmanual_name_modify_list.txtに記載された名前の付け替えを必要なファイルに適用する.
#
# 入力: manual_name_modify_list.txt
# 入力 => 出力 (名前変更リストの3列目に今回の変更後の名前を追記)
# H_conversion_list_automanual.txt => H_conversion_list_automanual2.txt
# 入力 => 出力 (名前の付け替えを実行する)
# mpc4_automanual.txt => mpc4_automanual2.txt
# newall_automanual.txt => newall_automanual2.txt
# redisp_automanual.txt => redisp_automanual2.txt
###########################################################################################
import traceback
import os
import re
import subprocess

class NothingToDo(Exception):
    pass

try:
    #---assess manual_name_modify_list.txt exists or not-----------
    if (not os.path.isfile("manual_name_modify_list.txt")) or (os.stat("manual_name_modify_list.txt").st_size==0):
        ## if not, we just copy them
        f = open("H_conversion_list_automanual.txt","r")
        lines = f.readlines()
        f.close()
        f = open("H_conversion_list_automanual2.txt","w",newline="\n")
        for line in lines:
            f.write(line.rstrip("\n") + " " + line.split()[1] + "\n")
        f.close()

        completed_process = subprocess.run("cp mpc4_automanual.txt mpc4_automanual2.txt", shell=True)
        if completed_process.returncode!=0: raise FileNotFoundError
        completed_process = subprocess.run("cp newall_automanual.txt newall_automanual2.txt", shell=True)
        if completed_process.returncode!=0: raise FileNotFoundError
        completed_process = subprocess.run("cp redisp_automanual.txt redisp_automanual2.txt", shell=True)
        if completed_process.returncode!=0: raise FileNotFoundError

        raise NothingToDo
    #--------------------------------------------------------------

    #---get name modify list---------------------------------------
    fileManualNameModifyList = open("manual_name_modify_list.txt", "r")
    lines = fileManualNameModifyList.readlines()
    fileManualNameModifyList.close()

    beforeNameList = []
    afterNameList  = []
    for line in lines:
        if len(line.split())!=0:
            if re.search(r'^H......', line.split()[0])!=None:
                beforeNameList.append(line.split()[0])
                afterNameList.append(line.split()[1])
    #--------------------------------------------------------------


    #---modify H conversion list-----------------------------------
    fileHConversionList = open("H_conversion_list_automanual.txt","r")
    lines = fileHConversionList.readlines()
    fileHConversionList.close()

    fileHConversionList2 = open("H_conversion_list_automanual2.txt","w",newline="\n")
    for line in lines:
        for l in range(len(beforeNameList)):
            if line.split()[1] == beforeNameList[l]:
                fileHConversionList2.write(line.rstrip("\n") + " " + afterNameList[l] + "\n")
                break
    fileHConversionList2.close()
    #--------------------------------------------------------------


    #---modify mpc4_automanual.txt, newall_automanual.txt, and redisp_automanual.txt
    ## modify mpc4_automanual.txt
    fileMpc4Automanual = open("mpc4_automanual.txt","r")
    lines = fileMpc4Automanual.readlines()
    fileMpc4Automanual.close()

    fileMpc4Automanual2 = open("mpc4_automanual2.txt","w",newline="\n")
    for line in lines:
        isMatch = False
        for l in range(len(beforeNameList)):
            if line.split()[0] == beforeNameList[l]:
                isMatch = True
                if len(afterNameList[l])==5:
                    fileMpc4Automanual2.write(afterNameList[l] + "       " + line[12:])
                else:
                    fileMpc4Automanual2.write(line.replace(beforeNameList[l], afterNameList[l]))
        if not isMatch:
            fileMpc4Automanual2.write(line)
    fileMpc4Automanual2.close()
    completed_process = subprocess.run("sort -n -o mpc4_automanual2.txt mpc4_automanual2.txt", shell=True)
    if completed_process.returncode!=0: raise Exception

    ## modify newall_automanual.txt
    fileNewallAutomanual = open("newall_automanual.txt","r")
    lines = fileNewallAutomanual.readlines()
    fileNewallAutomanual.close()

    fileNewallAutomanual2 = open("newall_automanual2.txt","w",newline="\n")
    for line in lines:
        isMatch = False
        for l in range(len(beforeNameList)):
            if line.split()[0] == beforeNameList[l]:
                isMatch = True
                if len(afterNameList[l])==5:
                    fileNewallAutomanual2.write(afterNameList[l] + "       " + line[12:])
                else:
                    fileNewallAutomanual2.write(line.replace(beforeNameList[l], afterNameList[l]))
        if not isMatch:
            fileNewallAutomanual2.write(line)
    fileNewallAutomanual2.close()
    completed_process = subprocess.run("sort -n -o newall_automanual2.txt newall_automanual2.txt", shell=True)
    if completed_process.returncode!=0: raise Exception

    ## modify redisp_automanual.txt
    fileRedispAutomanual = open("redisp_automanual.txt","r")
    lines = fileRedispAutomanual.readlines()
    fileRedispAutomanual.close()

    fileRedispAutomanual2 = open("redisp_automanual2.txt","w",newline="\n")
    for line in lines:
        isMatch = False
        for l in range(len(beforeNameList)):
            if line.split()[0] == beforeNameList[l]:
                isMatch = True
                fileRedispAutomanual2.write(line.replace(beforeNameList[l], afterNameList[l]))
        if not isMatch:
            fileRedispAutomanual2.write(line)
    fileRedispAutomanual2.close()
    completed_process = subprocess.run("sort -k 1,1 -k 2n,2 -o redisp_automanual2.txt redisp_automanual2.txt", shell=True)
    if completed_process.returncode!=0: raise Exception
    #-------------------------------------------------------------------------------


except NothingToDo:
    error = 0
    errorReason = 74
    
except FileNotFoundError:
    print("Some previous files are not found in aplly_manual_name_modify.py!")
    print(traceback.format_exc())
    error = 1
    errorReason = 74

except Exception:
    print("Some errors occur in aplly_manual_name_modify.py!")
    print(traceback.format_exc())
    error = 1
    errorReason = 75

else:
    error = 0
    errorReason = 74

finally:
    errorFile = open("error.txt","a")
    errorFile.write("{0:d} {1:d} 709 \n".format(error,errorReason))
    errorFile.close()
