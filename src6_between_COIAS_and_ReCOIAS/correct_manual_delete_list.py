#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#Timestamp: 2022/08/31 14:00 sugiura
##############################################################################################
# manual measureモードで自動検出天体のデータを削除した後に, searchモードに戻って変更を加えると,
# 削除する天体の名前が変わってしまう可能性がある.
# そのような場合にもmanual_delete_list2.txtに記載の名前付け替え前の名前と
# 今回の名前付け替えの結果を記したH_conversion_list.txtを用いれば
# manual_delete_list.txtを復元することができる.
#
# 入力: manual_delete_list2.txt
# 　　  H_conversion_list.txt
# 出力: manual_delete_list.txt
##############################################################################################
import traceback
import os
import shutil

try:
    if os.path.isfile("manual_delete_list2.txt"):
        if os.stat("manual_delete_list2.txt").st_size != 0:
            f = open("manual_delete_list2.txt","r")
            manualDeleteList2Lines = f.readlines()
            f.close()

            f = open("H_conversion_list.txt","r")
            HConversionListLines = f.readlines()
            f.close()

            manualDeleteListLines = []
            for manualDeleteLine in manualDeleteList2Lines:
                for HConversionLine in HConversionListLines:
                    if manualDeleteLine.split()[0]==HConversionLine.split()[0]:
                        manualDeleteListLines.append(HConversionLine.split()[1] + " " + manualDeleteLine.split()[2] + "\n")

            f = open("manual_delete_list.txt","w",newline="\n")
            f.writelines(manualDeleteListLines)
            f.close()

except FileNotFoundError:
    print("Some previous files are not found in correct_manual_delete_list.py!")
    print(traceback.format_exc())
    error = 1
    errorReason = 64

except Exception:
    print("Some errors occur in correct_manual_delete_list.py!")
    print(traceback.format_exc())
    error = 1
    errorReason = 65

else:
    error = 0
    errorReason = 64

finally:
    errorFile = open("error.txt","a")
    errorFile.write("{0:d} {1:d} 608 \n".format(error,errorReason))
    errorFile.close()
