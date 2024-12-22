#!/usr/bin/env python3
# -*- coding: UTF-8 -*
# Timestamp: 2022/2/23 12:30 sugiura
################################################################################################################
# 今回の測定で新たに測定した新発見候補天体数を数え, 今までに測定した新発見候補天体数の合計数を記載した
# /home/COIASusers/coias/param/N_new_objects.txtを更新する.
# ここで今回の測定で新たに測定した新発見候補天体数は, send_mpc.txtに記載されたH〇〇〇〇〇〇の天体を名前の重複がないように数えた数である.
#
# N_new_objects.txtから今回の測定前の新発見候補天体数を読み出し, 今回の測定で得られた新発見候補天体数を足しあげ,
# その数をすぐにN_new_objects.txtに書き込む.
################################################################################################################

import os
import re
import sys
import traceback
import PARAM
import print_detailed_log

try:
    # --- count number of new objects obtained from this measurement ----------
    if not os.path.isfile("send_mpc.txt"):
        raise FileNotFoundError("send_mpc.txt is not found!")
    f = open("send_mpc.txt")
    lines = f.readlines()
    f.close()

    newObjectNames = []
    for line in lines:
        thisName = line.split()[0].rstrip("*")
        if re.fullmatch(r"H......", thisName):
            thisHNumber = int(thisName.lstrip("H"))
            if thisName not in newObjectNames:
                newObjectNames.append(thisName)

    NNewObjects = len(newObjectNames)
    # -------------------------------------------------------------------------

    # --- update N_new_objects.txt --------------------------------------------
    NNewObjectsFilePath = PARAM.COIAS_DATA_PATH + "/param/N_new_objects.txt"
    if not os.path.isfile(NNewObjectsFilePath):
        NNewObjectsPrevious = 0
    else:
        f = open(NNewObjectsFilePath, "r")
        line = f.readline()
        NNewObjectsPrevious = int(line.rstrip("\n"))
        f.close()

    NNewObjects += NNewObjectsPrevious
    f = open(NNewObjectsFilePath, "w")
    f.write(str(NNewObjects))
    f.close()
    # -------------------------------------------------------------------------


except FileNotFoundError:
    print("Some previous files are not found in update_N_new_objects.py!", flush=True)
    print(traceback.format_exc(), flush=True)
    error = 1
    errorReason = 74

except Exception:
    print("Some errors occur in send_mail_to_MPC.py", flush=True)
    print(traceback.format_exc(), flush=True)
    error = 1
    errorReason = 75

else:
    error = 0
    errorReason = 74

finally:
    errorFile = open("error.txt", "a")
    errorFile.write("{0:d} {1:d} 905 \n".format(error, errorReason))
    errorFile.close()

    if error == 1:
        print_detailed_log.print_detailed_log(dict(globals()))

