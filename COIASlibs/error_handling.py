#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#Timestamp: 2022/08/04 11:45 sugiura
########################################################################
# GUI COIASの各ボタンを押すと走るスクリプトの最後に必ずこのスクリプトが置かれている.
# 各ボタンを押すと走るスクリプト中では各コマンドが走るごとに, エラーの有無に関わらず,
# 以下の3カラムの書式でerror.txtに各コマンドの実行結果を書き出す.
# [正常:0, 異常1] [2桁のエラーコード] [エラーの場所]
# 全ての箇所でエラーが起きず1カラム目が0ならこのスクリプトは0を返却する.
# 最初にエラーが起きた場所が重要なので, どこかでエラーが起き1カラム目が1になったら,
# 初めて1カラム目が1になった行のエラーコードをこのスクリプトは返却する.
# 2桁のエラーコードの詳細は以下を参照:
# COIAS_program_github/COIASdocs/20220623エラーハンドリングメッセージまとめ.docx
# エラーの場所は3桁くらいで場所を示すIDのようなもの.
# このスクリプトが返却したコードは, さらにこのスクリプトを呼び出したシェルスクリプト
# の最後にexit文にて返却され, フロントAPIに通知される.
########################################################################

import sys
import traceback

try:
    errorFile = open("error.txt","r")
    
except FileNotFoundError:
    print("error.txt does not exist!")
    print(traceback.format_exc())
    sys.exit(15)
    
else:
    lines = errorFile.readlines()
    errorFile.close()
    
    errorFlag = 0
    for l in range(len(lines)):
        oneLineList = lines[l].split()
        if errorFlag==0 and int(oneLineList[0])!=0:
            firstErrorReason = int(oneLineList[1])
            firstErrorPlace  = oneLineList[2]
            errorFlag=1

    if errorFlag==0:
        print("no error occurs.")
        sys.exit(0)
    else:
        print("some errors occur! first error place = " + firstErrorPlace)
        sys.exit(firstErrorReason)

