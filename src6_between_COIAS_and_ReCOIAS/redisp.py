#!/usr/bin/env python3
# -*- coding: UTF-8 -*
#Timestamp: 2024/12/01 12:00 sugiura
############################################################################################
# mpc2.txtのある行の15-80カラム目(つまり観測日, ra, dec, 等級, フィルター, 観測所まで)と
# all.txtのある行の15-80カラム目と完全に一致するような行を見つけ出し,
# mpc2.txtのその行の0-14カラム目(名前部分)とall.txtのその行の15カラム目以降(その他情報)を結合させ,
# newall.txtに書き出す.
# 要は, mpc2.txtに記載の天体のみの情報をall.txtから抽出してnewall.txtに書き出す.
# また, newall.txtのうち 天体名 画像番号 等級 等級誤差 Xpixel Ypixel のみをpredisp.txtに書き出す.
# 入力: mpc2.txt
# 　　  all.txt
# 出力: newall.txt
# 　　  predisp.txt
#
# その後, AstsearchR_between_COIAS_and_ReCOIASで
# predisp.txtの1, 2, 5, 6カラム目 (天体名 画像番号 Xpixel Ypixel)のみを取り出し, redisp.txtに書き出す.
############################################################################################
import traceback
import os
import numpy as np
import print_detailed_log

try:
    # ファイル名定義
    allFileName = "all.txt"
    mpc2FileName = "mpc2.txt"
    newallFileName = "newall.txt"
    predispFileName = "predisp.txt"

    if os.stat("mpc2.txt").st_size == 0:
        empty = []
        np.savetxt(newallFileName, empty, fmt="%s")
        np.savetxt(predispFileName, empty, fmt="%s")

    else:
        # データ読み出し ########################
        fAll = open(allFileName, "r")
        allLines = fAll.readlines()
        fAll.close()

        fmpc2 = open(mpc2FileName, "r")
        mpc2Lines = fmpc2.readlines()
        fmpc2.close()
        #######################################

        # mpc2.txt に記載の行に該当する all.txt の行のみを残す #####
        remainAllLines = []
        for allLine in allLines:
            allLineDataPart = allLine[15:80]
            for mpc2Line in mpc2Lines:
                mpc2LineDataPart = mpc2Line[15:80]
                if allLineDataPart == mpc2LineDataPart:
                    remainAllLines.append(allLine)
        ######################################################

        # ソートした上で, データ行が全く同じ隣り合う行が存在した場合, #
        # 前者の行を残さない ####################################
        remainAllLines = sorted(remainAllLines)
        newAllLines = []
        predispLines = []
        for i in range(len(remainAllLines) - 1):
            stock1 = remainAllLines[i][15:80]
            stock2 = remainAllLines[i + 1][15:80]
            if not stock1 == stock2:
                newAllLine = remainAllLines[i]
                newAllLines.append(newAllLine)
                predispLine = remainAllLines[i][0:14] + remainAllLines[i][81:124]
                predispLines.append(predispLine)
        newAllLines.append(remainAllLines[len(remainAllLines) - 1])
        predispLines.append(
            remainAllLines[len(remainAllLines) - 1][0:14]
            + remainAllLines[len(remainAllLines) - 1][81:124]
        )
        ######################################################

        # データ書き出し ########################
        fNewAll = open(newallFileName, "w")
        fNewAll.writelines(newAllLines)
        fNewAll.close()

        fPredisp = open(predispFileName, "w")
        fPredisp.writelines(predispLines)
        fPredisp.close()
        #######################################

except FileNotFoundError:
    print("Some previous files are not found in redisp.py!", flush=True)
    print(traceback.format_exc(), flush=True)
    error = 1
    errorReason = 64

except Exception:
    print("Some errors occur in redisp.py!", flush=True)
    print(traceback.format_exc(), flush=True)
    error = 1
    errorReason = 65

else:
    error = 0
    errorReason = 64

finally:
    errorFile = open("error.txt", "a")
    errorFile.write("{0:d} {1:d} 606 \n".format(error, errorReason))
    errorFile.close()

    if error == 1:
        print_detailed_log.print_detailed_log(dict(globals()))
