#!/usr/bin/env python3
# -*- coding: UTF-8 -*
#Timestamp: 2022/11/4 8:30 sugiura
######################################################################################################
# print_progress()関数を記載したスクリプト.
# またシェルスクリプトから直接呼び出せるようにif __name__ == "__main__":
# のラッパー的部分も記載している.
# 進行度をターミナル(オリジナルCOIAS)or画面(webCOIAS)に書き出すために使用.
# 進行度はチェックポイントで管理する. 最初に全チェックポイント数を指定し,
# その後はこの関数を呼び出すごとに通過したチェックポイント数を1ずつ増やして進行度が増えていく.
# 0でないnTotalCheckPoints引数で呼び出された時は各ボタン中で初回呼び出しと見なし,
# 進行度0%を画面に書き出し, 進行度と共にcurrentButtonNameで指定されたボタン名をprogress.txtに書き出す.
# 引数なしで呼び出された時は普通にチェックポイントを通過したと見なし, 通過したチェックポイント数を1増やす.
# 0でないcurrentCheckPoint引数で呼び出された場合は, 実際に通過したチェックポイント数に関わらず
# 進行度をcurrentCheckPointの値で計算する.(精密軌道をすでに取得していた場合など飛ばされるチェックポイントがあるため)
# 0でないnCheckPointsForLoop引数で呼び出された場合は, 1つのfor文の中に複数チェックポイントを設置する場合である.
# この時, for文中でのチェックポイントの数をnCheckPointsForLoopに, 全体のfor文の回る回数をnForLoopに,
# 現在までに回ったfor文の回数をcurrentForLoopに指定する.
#
# このスクリプトが書き出す・読み込むprogress.txtの書式は以下:
#    [ボタン名] [今までに通過したチェックポイント数] [ボタン内の全チェックポイント数] [ユーザーid]
#######################################################################################################
import os
import argparse

def print_progress(nTotalCheckPoints=0, currentButtonName=None, currentCheckPoint=0, nCheckPointsForLoop=0, nForLoop=0, currentForLoop=0):
    progressFileName = "progress.txt"
    
    #---argument check----------------------------------------------------------
    if nTotalCheckPoints<0 or currentCheckPoint<0 or nCheckPointsForLoop<0 or nForLoop<0 or currentForLoop<0:
        raise ValueError(f"invalid arguments! nTotalCheckPoints={nTotalCheckPoints}, currentCheckPoint={currentCheckPoint}, nCheckPointsForLoop={nCheckPointsForLoop}, nForLoop={nForLoop}, currentForLoop={currentForLoop}")

    if currentButtonName!=None:
        if type(currentButtonName) is not str:
            raise ValueError(f"not None currentButtonName should be string: currentButtonName={currentButtonName}")
    
    modeFlagList = [nTotalCheckPoints, currentCheckPoint, nCheckPointsForLoop]
    nNonZeroFlag = sum(flag>=1 for flag in modeFlagList)
    if nNonZeroFlag>=2:
        raise ValueError(f"number of non-zero flag argments should be 0 or 1. nTotalCheckPoints={nTotalCheckPoints}, currentCheckPoint={currentCheckPoint}, nCheckPointsForLoop={nCheckPointsForLoop}")

    if (nTotalCheckPoints!=0 and currentButtonName==None) or (nTotalCheckPoints==0 and currentButtonName!=None):
        raise ValueError(f"For none-zero nTotalCheckPoints, currentButtonName should be specified. nTotalCheckPoints={nTotalCheckPoints}, currentButtonName={currentButtonName}")

    if not os.path.isfile(progressFileName) and nTotalCheckPoints==0:
        raise ValueError("If progress.txt does not exist, i.e., initial done, nTotalCheckPoints should be not zero: nTotalCheckPoints={nTotalCheckPoints}")
    #---------------------------------------------------------------------------
    
    #---mode selection----------------------------------------------------------
    isCheckPointLoop = False
    if nTotalCheckPoints==0 and currentCheckPoint==0 and nCheckPointsForLoop==0:
        mode = "normal"
    elif nTotalCheckPoints!=0:
        mode = "initialize"
    elif currentCheckPoint!=0:
        mode = "specifyCurrentCheckPoint"
    elif nCheckPointsForLoop!=0:
        mode = "forLoop"
        if int(currentForLoop % (nForLoop/nCheckPointsForLoop)) == 0:
            isCheckPointLoop = True
    #---------------------------------------------------------------------------

    ### In forLoop mode, if not isCheckPointLoop, nothing to do
    if mode=="forLoop" and not isCheckPointLoop:
        return

    #---get information in progress.txt-----------------------------------------
    #---if progress.txt does not exist, we only set uid-------------------------
    if not os.path.isfile(progressFileName):
        uid = 0
    else:
        f = open(progressFileName,"r")
        line = f.readline()
        f.close()

        contents = line.split()
        readCurrentButtonName = contents[0]
        readCurrentCheckPoint = int(contents[1])
        readNTotalCheckPoints = int(contents[2])
        uid = int(contents[3])
    #---------------------------------------------------------------------------

    #---modify information------------------------------------------------------
    ### normal or forLoop mode
    if mode == "normal" or mode == "forLoop":
        writeCurrentButtonName = readCurrentButtonName
        writeCurrentCheckPoint = readCurrentCheckPoint + 1
        writeNTotalCheckPoints = readNTotalCheckPoints
    ### initialize mode
    elif mode == "initialize":
        writeCurrentButtonName = currentButtonName
        writeCurrentCheckPoint = 0
        writeNTotalCheckPoints = nTotalCheckPoints
    ### specify current check point mode
    elif mode == "specifyCurrentCheckPoint":
        writeCurrentButtonName = readCurrentButtonName
        writeCurrentCheckPoint = currentCheckPoint
        writeNTotalCheckPoints = readNTotalCheckPoints
    #---------------------------------------------------------------------------

    #---write progress to stdout or GUI-----------------------------------------
    progres_percent = str(int((writeCurrentCheckPoint/writeNTotalCheckPoints)*100.0))
    print(progres_percent + "% ", end="", flush=True)
    if writeCurrentCheckPoint == writeNTotalCheckPoints:
        print()
    #---------------------------------------------------------------------------

    #---write information to progress.txt---------------------------------------
    f = open(progressFileName,"w")
    f.write(f"{writeCurrentButtonName} {writeCurrentCheckPoint} {writeNTotalCheckPoints} {uid}")
    f.close()
    #---------------------------------------------------------------------------



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--currentcheck", type=int, default=0,    help="give a current check point for specify current check point mode")
    parser.add_argument("-t", "--totalchecks",  type=int, default=0,    help="give a number of total check points for initialize mode")
    parser.add_argument("-n", "--name",         type=str, default=None, help="give a current button name for inialize mode")
    args = parser.parse_args()

    print_progress(nTotalCheckPoints=args.totalchecks, currentButtonName=args.name, currentCheckPoint=args.currentcheck)
