#!/usr/bin/env python3
# -*- coding: UTF-8 -*
# Timestamp: 2024/12/01 13:30 sugiura
###########################################################################################
# 様々な理由により天体が削除されることにより欠番が生じてH番号が連番ではなくなる可能性があるので,
# このスクリプトでは最終的に連番になるようにさらにH番号の付け替えを行う.
# ~/.coias/param/max_H_number.txtに記載の数値+1を連番の開始値とした連番にH番号を付け替える.
# 付け替え後のH番号の最大値を~/.coias/param/max_H_number.txtに書き出す.
# 消されたかどうかも含めて, H番号の付け替えの結果はH_conversion_list_simple.txtに書き出す.
#
# 入力: pre_repo2_2.txt
# 　　  max_H_number.txt 今現在の全ユーザーに測定された新天体のうちH番号の最大値を知るために使用.
#      redisp_automanual2.txt 様々な理由により測定が削除される前のH番号の一覧を得るために使用.
# 出力: pre_repo3.txt
# 　　    最終的にH番号が連番になるように名前が付け替えられたもの
# 　　  H_conversion_list_simple.txt
# 　　    H番号の付け替えの結果. 1列名: 付け替え前のH番号, 2列目: 付け替え後のH番号
# 　　    残差が大きいなどの理由で消えてしまった天体は2列目に rejected と記載される.
#      max_H_number.txt
#        名前付け替え後のH番号の最大値を書き出す
###########################################################################################
import traceback
import re
import subprocess
import print_detailed_log
import PARAM

try:
    completed_process = subprocess.run(
        "sort -n -o pre_repo2_2.txt pre_repo2_2.txt", shell=True
    )
    if completed_process.returncode != 0:
        raise Exception

    # ---get H conversion list from pre repo-----------------------
    ### set kinit #########################
    maxHFileName = PARAM.COIAS_DATA_PATH + "/param/max_H_number.txt"
    f = open(maxHFileName, "r")
    maxHFileLine = f.readline()
    f.close()
    kinit = int(maxHFileLine.split()[0]) + 1
    #######################################

    filePreRepo = open("pre_repo2_2.txt", "r")
    lines = filePreRepo.readlines()
    filePreRepo.close()

    HOldNameList = []
    HNewNameList = []
    k = 0
    for line in lines:
        thisName = line.split()[0]
        if (re.search(r"^H......", thisName) != None) and (
            thisName not in HOldNameList
        ):
            newName = "H" + str(kinit + k).rjust(6, "0")
            HOldNameList.append(thisName)
            HNewNameList.append(newName)
            k += 1
    newMaxHNumber = kinit + k - 1
    # -------------------------------------------------------------

    # ---新たなH番号の最大値をmax_H_number.txtに書き出す----------------
    f = open(maxHFileName, "w")
    f.write(f"{newMaxHNumber}\n")
    f.close()
    # -------------------------------------------------------------

    # ---名前付け替え結果をH_conversion_list_simple.txtに書き出す ------
    with open("redisp_automanual2.txt", "r") as f:
        redispLines = f.readlines()
        originalHList = []
        for line in redispLines:
            objectName = line.split()[0]
            if (re.search(r"^H......", objectName) != None) and (
                objectName not in originalHList
            ):
                originalHList.append(objectName)

    with open("H_conversion_list_simple.txt", "r") as f:
        for originalHName in originalHList:
            newName = "rejected"
            for l in range(len(HOldNameList)):
                if originalHName == HOldNameList[l]:
                    newName = HNewNameList[l]
        f.write(originalHName + " " + newName + "\n")
    # -------------------------------------------------------------

    # ---modify pre_repo.txt as H numbers become sequential--------
    filePreRepo = open("pre_repo2_2.txt", "r")
    lines = filePreRepo.readlines()
    filePreRepo.close()

    filePreRepo2 = open("pre_repo3.txt", "w", newline="\n")
    for line in lines:
        isMatch = False
        for l in range(len(HOldNameList)):
            if line.split()[0] == HOldNameList[l]:
                isMatch = True
                filePreRepo2.write(line.replace(HOldNameList[l], HNewNameList[l]))
                break
        if not isMatch:
            filePreRepo2.write(line)
    filePreRepo2.close()
    # -------------------------------------------------------------

except FileNotFoundError:
    print(
        "Some previous files are not found in modify_preRepo_as_H_sequential!",
        flush=True,
    )
    print(traceback.format_exc(), flush=True)
    error = 1
    errorReason = 74

except Exception:
    print("Some errors occur in modify_preRepo_as_H_sequential!", flush=True)
    print(traceback.format_exc(), flush=True)
    error = 1
    errorReason = 75

else:
    error = 0
    errorReason = 74

finally:
    errorFile = open("error.txt", "a")
    errorFile.write("{0:d} {1:d} 710 \n".format(error, errorReason))
    errorFile.close()

    if error == 1:
        print_detailed_log.print_detailed_log(dict(globals()))
