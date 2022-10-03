#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#Timestamp: 2022/08/31 10:00 sugiura
##############################################################################################
# manual measureモードで削除した自動測定天体の情報をredisp.txtから削除する.
# また, manual measureモードとsearchモードはあくまでも独立したモードであって欲しく,
# manual measureモードの後にsearchモードで変更があっても問題のないようにしておきたい.
# そのため, H_conversion_list.txtを利用して, 削除する天体の1度目の名前付け替えの前の名前を
# manual_delete_list.txtに併記したファイルも作成する.
#
# 入力: manual_delete_list.txt
# 　　    manual measureモードで削除した自動検出天体の情報
# 　　    書式: manualMeasureモードでの自動検出天体名 画像番号
# 　　  redisp.txt
# 　　    manual_delete_list.txtに記載の情報を消したいファイル
# 　　  H_conversion_list.txt
# 　　    manual_delete_list.txtに記載の天体の1度目の名前付け替え前の名前を知るために使用.
# 出力: redisp2.txt
# 　　    redisp.txtからmanual_delete_list.txtに記載の自動検出天体の情報を削除したもの
# 　　  manual_delete_list2.txt
# 　　    manual_delete_list.txtに1度目の名前付け替え前の名前を追記したもの
# 　　    書式: 1度目の名前付け替え前の自動検出天体名 manualMeasureモードでの自動検出天体名 画像番号
##############################################################################################
import traceback
import os
import shutil

try:
    if not os.path.isfile("manual_delete_list.txt"):
        shutil.copy2("redisp.txt", "redisp2.txt")
    else:
        #---remove data in manual_delete_list.txt from redisp.txt and produce redisp2.txt------
        f = open("redisp.txt","r")
        redispLines = f.readlines()
        f.close()

        f = open("manual_delete_list.txt","r")
        manualDeleteLines = f.readlines()
        f.close()

        for manualLine in manualDeleteLines:
            for l in reversed(range(len(redispLines))):
                if manualLine.split()[0]==redispLines[l].split()[0] and manualLine.split()[1]==redispLines[l].split()[1]:
                    del redispLines[l]

        f = open("redisp2.txt","w",newline="\n")
        f.writelines(redispLines)
        f.close()
        #--------------------------------------------------------------------------------------

        #---add name before 1st alteration to manual_delete_list.txt and produce manual_delete_list2.txt--
        f = open("H_conversion_list.txt","r")
        HConversionListLines = f.readlines()
        f.close()

        newManualLines = []
        for manualLine in manualDeleteLines:
            for HConversionLine in HConversionListLines:
                if manualLine.split()[0] == HConversionLine.split()[1]:
                    newManualLines.append(HConversionLine.split()[0] + " " + manualLine)

        f = open("manual_delete_list2.txt","w",newline="\n")
        f.writelines(newManualLines)
        f.close()
        #-------------------------------------------------------------------------------------------------

except FileNotFoundError:
    print("Some previous files are not found in apply_manual_delete_to_redisp.py!")
    print(traceback.format_exc())
    error = 1
    errorReason = 84

except Exception:
    print("Some errors occur in apply_manual_delete_to_redisp.py!")
    print(traceback.format_exc())
    error = 1
    errorReason = 85

else:
    error = 0
    errorReason = 84

finally:
    errorFile = open("error.txt","a")
    errorFile.write("{0:d} {1:d} 812 \n".format(error,errorReason))
    errorFile.close()
