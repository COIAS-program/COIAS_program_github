#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#Timestamp: 2022/08/05 23:00 sugiura
##############################################################################################
# 手動測定によって得られた新天体のH番号を連番にする.
# 手動測定天体の始めのH番号は, ノイズも含めた自動検出天体と被らないようにdisp.txtに記載の
# どのH番号よりも大きく設定してあり, なおかつ連番になることが保証されていない.
# そこで, AstsearchR_between_COIAS_and_ReCOIASで付け替えた自動検出天体の続きの連番となるように
# 手動測定天体のH番号も付け替える. (redisp.txtの続きの連番となるようにする)
#
# 入力: redisp.txt
# 　　    自動検出天体のH番号の最大値を得るために使用
# 出力: H_conversion_list_manual.txt
# 　　    手動測定天体のH番号が今回の付け替えでどのように変化したか記録する
# 　　    書式: 変換前のHから始まる新天体の名前 変換後のHから始まる新天体の名前
# 入力 => 出力 (新天体の番号の付け替えのみ)
# mpc_m.txt => mpc4_m.txt
# all_m.txt => newall_m.txt
# disp_m.txt => redisp_manual.txt
##############################################################################################
import re
import traceback

try:
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


    #---get H conversion list and output it----------
    mpcMFile = open("mpc_m.txt","r")
    lines = mpcMFile.readlines()
    mpcMFile.close()

    oldHList = []
    newHList = []
    k=1
    for line in lines:
        contents = line.split()
        if re.search(r'^H......',contents[0])!=None:
            strH = contents[0]
            if strH not in oldHList:
                oldHList.append(strH)
                newHList.append("H"+str(NHMax+k).rjust(6,'0'))
                k += 1

    HConversionListFile = open("H_conversion_list_manual.txt","w",newline="\n")
    for l in range(len(oldHList)):
        HConversionListFile.write(oldHList[l]+" "+newHList[l]+"\n")
    HConversionListFile.close()
    #------------------------------------------------


    #---make mpc4_m.txt, newall_m.txt, and redisp_manual.txt--------
    inputFile = open("all_m.txt","r")
    mpc4MFile = open("mpc4_m.txt","w",newline="\n")
    redispMFile = open("redisp_manual.txt","w",newline="\n")
    newallMFile = open("newall_m.txt","w",newline="\n")

    lines = inputFile.readlines()
    inputFile.close()
    for line in lines:
        contents = line.split()
        replaceHl=0
        for l in range(len(oldHList)):
            if contents[0]==oldHList[l]:
                replaceHl = l
        if len(oldHList)!=0:
            line = line.replace(oldHList[replaceHl], newHList[replaceHl])
        contents = line.split()

        mpc4MFile.write(line[0:80]+"\n")
        redispMFile.write(contents[0]+" "+contents[13]+" "+contents[16]+" "+contents[17]+"\n")
        newallMFile.write(line)

    mpc4MFile.close()
    redispMFile.close()
    #------------------------------------------------------------------

except FileNotFoundError:
    print("Some previous files are not found in make_mpc4_newall_and_redisp_manual.py!")
    print(traceback.format_exc())
    error = 1
    errorReason = 84

except Exception:
    print("Some errors occur in make_mpc4_newall_and_redisp_manual.py!")
    print(traceback.format_exc())
    error = 1
    errorReason = 85

else:
    error = 0
    errorReason = 84

finally:
    errorFile = open("error.txt","a")
    errorFile.write("{0:d} {1:d} 808 \n".format(error,errorReason))
    errorFile.close()
