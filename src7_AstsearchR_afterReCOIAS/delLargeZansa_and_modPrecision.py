#!/usr/bin/env python3
# -*- coding: UTF-8 -*
#Timestamp: 2022/08/06 20:00 sugiura
###########################################################################################
# findorb.pyによって計算された残差が0.7"より大きいデータ点を削除する.
# result.txtはMPC 80カラムフォーマットの行末にX方向の残差とY方向の残差が付け加えられているだけなので,
# X方向の残差とY方向の残差の両方が0.7"よりも小さいデータのみを残して,
# 80カラム目までを切り出して出力すれば残ったMPC 80カラムフォーマットファイルが出来上がる.
# 削除された結果, ある名前の天体のデータ点が2以下になったらその名前の天体のデータを全て削除する.
# さらに, 第二引数が1の場合はdecのarcsecの精度を小数点以下1桁に修正する.
#
# 入力: result.txt
# 　　    MPC 80カラムフォーマットの行末にfindorbで計算された残差が付け加えられたもの
# 出力: pre_repo.txt
# 　　    残差が0.7"よりも大きいデータを削除し, 天体あたりのデータ行数が2以下になったものを削除し,
# 　　    第二引数が1の場合はdecのarcsecの精度を小数点以下1桁に修正したもの
###########################################################################################
import sys
import traceback
import os
import print_detailed_log

try:
    argc = len(sys.argv)
    if argc != 2:
        print("please input second argument of 1 or 2")
        print("if you need one decimal: 1, if two decimal: 2")
        raise ValueError

    if (sys.argv[1] != "1") and (sys.argv[1] != "2"):
        print("please input second argument of 1 or 2")
        print("if you need one decimal: 1, if two decimal: 2")
        raise ValueError

    inputFileName = "result.txt"
    outputFileName = "pre_repo.txt"
    inputFile = open(inputFileName, "r")
    outputFile = open(outputFileName, "w")

    if os.stat(inputFileName).st_size != 0:
        inputLines = inputFile.readlines()
        outputLines = []

        for i in range(len(inputLines)):
            contents = inputLines[i].split()
            Xres = float(contents[14])
            Yres = float(contents[15])

            if (abs(Xres) < 0.7) and (abs(Yres) < 0.7):
                str_list = list(inputLines[i][0:80]) + list("\n")

                if sys.argv[1] == "1":
                    str_list[55] = ' '

                outputLines.append("".join(str_list))

        #---remove objects with observation numbers smaller than 2-----
        if len(outputLines)!=0:
            prevObsName = outputLines[-1][0:12]
            nObs=0
            for i in reversed(range(len(outputLines))):
                obsName = outputLines[i][0:12]
                if obsName==prevObsName:
                    nObs += 1
                else:
                    if nObs<=2:
                        for n in reversed(range(nObs)):
                            del outputLines[i+n+1]
                    nObs=1

                if i==0 and nObs<=2:
                    for n in reversed(range(nObs)):
                        del outputLines[n]
            
                prevObsName = obsName

            outputFile.writelines(outputLines)
        #--------------------------------------------------------------

    inputFile.close()
    outputFile.close()

except FileNotFoundError:
    print("Some previous files are not found in delLargeZansa_and_modPrecision.py!",flush=True)
    print(traceback.format_exc(),flush=True)
    error = 1
    errorReason = 74

except Exception:
    print("Some errors occur in delLargeZansa_and_modPrecision.py!",flush=True)
    print(traceback.format_exc(),flush=True)
    error = 1
    errorReason = 75

else:
    error = 0
    errorReason = 74

finally:
    errorFile = open("error.txt","a")
    errorFile.write("{0:d} {1:d} 705 \n".format(error,errorReason))
    errorFile.close()

    if error==1:
        print_detailed_log.print_detailed_log(dict(globals()))
