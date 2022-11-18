#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#Timestamp: 2022/08/31 11:00 sugiura
##############################################################################################
# manual measureモードで削除した自動測定天体の情報をmpc4.txt, newall.txt, redisp.txtから削除する.
# ただしmanual measureモードを行った後にsearchモードを実行してH番号がつけ変わっている可能性があるので,
# この時点でのH_conversion_list.txtを読み込んでこの時点での付け替え後の名前の情報が消されるようにする.
#
# 入力: H_conversion_list.txt
# 入力 => 出力
# mpc4.txt => mpc4_2.txt
# newall.txt => newall_2.txt
# redisp.txt => redisp_2.txt
##############################################################################################
import traceback
import os
import shutil
import print_detailed_log

try:
    if not os.path.isfile("manual_delete_list2.txt"):
        shutil.copy2("mpc4.txt", "mpc4_2.txt")
        shutil.copy2("newall.txt", "newall_2.txt")
        shutil.copy2("redisp.txt", "redisp_2.txt")
    else:
        #---get present names of objects that we want to delete--------------------------
        f = open("manual_delete_list2.txt","r")
        lines = f.readlines()
        f.close()

        delNames = []
        delImages = []
        for line in lines:
            delNames.append(line.split()[0])
            delImages.append(line.split()[2])

        f = open("H_conversion_list.txt","r")
        HConversionListLines = f.readlines()
        f.close()

        for l in range(len(delNames)):
            for HConversionLine in HConversionListLines:
                if delNames[l]==HConversionLine.split()[0]:
                    delNames[l] = HConversionLine.split()[1]
                    break
        #--------------------------------------------------------------------------------

        #---remove data in manual_delete_list2.txt from redisp.txt-----------------------
        f = open("redisp.txt","r")
        redispLines = f.readlines()
        f.close()

        for lDel in range(len(delNames)):
            for lRedisp in reversed(range(len(redispLines))):
                if delNames[lDel]==redispLines[lRedisp].split()[0] and delImages[lDel]==redispLines[lRedisp].split()[1]:
                    del redispLines[lRedisp]

        f = open("redisp_2.txt","w",newline="\n")
        f.writelines(redispLines)
        f.close()
        #--------------------------------------------------------------------------------

        #---remove data in manual_delete_list2.txt from newall.txt and mpc4.txt----------
        f = open("newall.txt","r")
        newallLines = f.readlines()
        f.close()

        f = open("mpc4.txt","r")
        mpc4Lines = f.readlines()
        f.close()

        for lDel in range(len(delNames)):
            for lNewall in reversed(range(len(newallLines))):
                if delNames[lDel]==newallLines[lNewall].split()[0] and delImages[lDel]==newallLines[lNewall].split()[13]:
                    delNewallLine = newallLines[lNewall]
                    del newallLines[lNewall]
                    
                    for lMpc4 in reversed(range(len(mpc4Lines))):
                        if delNewallLine[0:80]==mpc4Lines[lMpc4][0:80]:
                            del mpc4Lines[lMpc4]

        f = open("newall_2.txt","w",newline="\n")
        f.writelines(newallLines)
        f.close()

        f = open("mpc4_2.txt","w",newline="\n")
        f.writelines(mpc4Lines)
        f.close()
        #--------------------------------------------------------------------------------

except FileNotFoundError:
    print("Some previous files are not found in apply_manual_delete_to_report.py!",flush=True)
    print(traceback.format_exc(),flush=True)
    error = 1
    errorReason = 74

except Exception:
    print("Some errors occur in apply_manual_delete_to_report.py!",flush=True)
    print(traceback.format_exc(),flush=True)
    error = 1
    errorReason = 75

else:
    error = 0
    errorReason = 74

finally:
    errorFile = open("error.txt","a")
    errorFile.write("{0:d} {1:d} 710 \n".format(error,errorReason))
    errorFile.close()

    if error==1:
        print_detailed_log.print_detailed_log(dict(globals()))
