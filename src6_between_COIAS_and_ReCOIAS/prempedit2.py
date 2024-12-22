#!/usr/bin/env python3
# -*- coding: UTF-8 -*
#Timestamp: 2024/12/01 12:00 sugiura
##############################################################################################
# 既知天体と, memo.txtに番号が記載されている新天体のデータのみを
# mpc.txtから抜き出してきてmpc2.txtに書き出す.
# 入力: memo.txt COIAS.pyのsearchモードで選んだ新天体の名前からHを除いた番号のリスト
# 　　  mpc.txt  自動検出に引っかかった全天体のMPC 80カラムフォーマットでの情報
# 出力: mpc2.txt mpc.txtから既知天体とmemo.txtに番号が記載されている新天体の情報のみを取り出したもの.
# 　　           番号の付け替えはまだなされていない.
##############################################################################################
import re
import traceback
import print_detailed_log

try:
    # mpc.txt と memo.txt の内容を読み出す #########
    fmpc = open("mpc.txt", "r")
    mpcLines = fmpc.readlines()  # ノイズも含む自動検出天体一覧のMPC80行
    fmpc.close()

    fmemo = open("memo.txt", "r")
    memoLines = fmemo.readlines()  # ユーザが選んだH番号の一覧
    fmemo.close()
    #############################################

    # memo.txtに記載の番号をH番号化する #############
    memoHList = []
    for memoNumber in memoLines:
        Hname = "H" + str(memoNumber.strip()).zfill(6)
        memoHList.append(Hname)

    # 空行と重複を削除する
    memoHList = list(set([x for x in memoHList if x]))
    #############################################

    # memo.txt に記載のH番号のMPC80行のみを mpc.txt から抽出する ###
    selectedHMPC80Lines = []
    for selectedH in memoHList:
        for mpcLine in mpcLines:
            if selectedH in mpcLine:
                selectedHMPC80Lines.append(mpcLine)
    selectedHMPC80Lines.sort()
    ##########################################################

    # 既知天体のMPC80行を mpc.txt から抽出する #######
    knownMPC80Lines = []
    for mpcLine in mpcLines:
        if (
            re.match("\w", mpcLine)
            or re.match("~", mpcLine)
            or re.match("^     K", mpcLine)
            or re.match("^     J", mpcLine)
        ):
            knownMPC80Lines.append(mpcLine)
    knownMPC80Lines.sort()
    #############################################

    # mpc2.txt に選択されたH番号と既知天体のMPC80行を出力 ####
    outputMPC80Lines = knownMPC80Lines + selectedHMPC80Lines
    with open("mpc2.txt", "wt") as f:
        f.writelines(outputMPC80Lines)
    ####################################################S

except FileNotFoundError:
    print("Some previous files are not found in prempedit2.py!", flush=True)
    print(traceback.format_exc(), flush=True)
    error = 1
    errorReason = 64

except Exception:
    print("Some errors occur in prempedit2.py!", flush=True)
    print(traceback.format_exc(), flush=True)
    error = 1
    errorReason = 65

else:
    error = 0
    errorReason = 64

finally:
    errorFile = open("error.txt", "a")
    errorFile.write("{0:d} {1:d} 602 \n".format(error, errorReason))
    errorFile.close()

    if error == 1:
        print_detailed_log.print_detailed_log(dict(globals()))
