#!/usr/bin/env python3
# -*- coding: UTF-8 -*
#Timestamp: 2022/08/06 20:00 sugiura
###########################################################################################
# 明るい天体は十分に報告されていて再度MPCに報告する必要はないため,
# bright_asteroid_MPC_names_in_the_field.txtに記載されている15等級よりも明るくなりうる
# 天体は報告データから削除する.
#
# 入力: bright_asteroid_MPC_names_in_the_field.txt
# 　　    視野内かつAstMPC.edbに記載の15等級よりも明るくなりうる既知小惑星の
# 　　    MPCフォーマットでの名前の一覧
# 　　  pre_repo.txt
# 出力: pre_repo.txt (上書き保存)
###########################################################################################
import traceback

try:
    #---get names of bright known asteroids-----------------
    fileBrightKnownAsteroids = open("bright_asteroid_MPC_names_in_the_field.txt","r")
    lines = fileBrightKnownAsteroids.readlines()
    namesOfBrightKnownAsteroids = []
    for l in range(len(lines)):
        namesOfBrightKnownAsteroids.append(lines[l].rstrip("\n"))
    fileBrightKnownAsteroids.close()
    #-------------------------------------------------------

    #---get data in pre_repo.txt----------------------------
    inputfileSendMpc = open("pre_repo.txt","r")
    lines = inputfileSendMpc.readlines()
    inputfileSendMpc.close()
    #-------------------------------------------------------

    #---compare names in pre_repo.txt and reject bright known asteroids---
    outputfileSendMpc = open("pre_repo.txt","w",newline="\n")
    for l in range(len(lines)):
        oneLineList = lines[l].split()
        if oneLineList[0] not in namesOfBrightKnownAsteroids:
            outputfileSendMpc.write(lines[l])
    outputfileSendMpc.close()
    #---------------------------------------------------------------------

except FileNotFoundError:
    print("Some previous files are not found in reject_bright_known_asteroids_from_report.py!")
    print(traceback.format_exc())
    error = 1
    errorReason = 74

except Exception:
    print("Some errors occur in reject_bright_known_asteroids_from_report.py!")
    print(traceback.format_exc())
    error = 1
    errorReason = 75

else:
    error = 0
    errorReason = 74

finally:
    errorFile = open("error.txt","a")
    errorFile.write("{0:d} {1:d} 706 \n".format(error,errorReason))
    errorFile.close()
