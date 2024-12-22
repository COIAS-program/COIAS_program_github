#!/usr/bin/env python3
# -*- coding: UTF-8 -*
# Timestamp: 2024/12/01 12:30 sugiura, 2023/08/10 20:00 urakawa
###########################################################################################
# jd, ra, decが一致している行が2行以上あった場合, 2つ目以降をダブりとして削除する.
# さらに, 同一の名前の天体のデータで等級が中央値から0.7以上外れているものも削除し,
# その上で同一の名前の天体のデータ数が2以下になったらその名前の天体のデータを全て削除する.
#
# 入力: mpc4_automanual2.txt
# 出力: mpc7.txt
# 　　    mpc4_automanual2.txtに対して上記のダブり除去, 等級が大きずれているもの除去,
# 　　    データが2行以下になる天体の除去を行った結果を書き出したもの.
# 2023/08/10 20:00 urakawa
# DUPLICATE_THRESH_ARCSEC = 6 を追加
# 2023/11/29 03:00 urakawa
# decがマイナスの場合の数値が間違っていたので修正
###########################################################################################
import itertools
import re

import numpy as np
import pandas as pd
import traceback
import os
import readparam
import print_detailed_log

# Define thresh arcsec
DUPLICATE_THRESH_ARCSEC = 6.0

try:
    # 2点許可モードかどうか取得
    params = readparam.readparam()
    TWO_MEASUREMENT_PERMIT_MODE = params["tp"] == 1

    # detect list
    inputMpc4FileName = "mpc4_automanual2.txt"
    if os.stat(inputMpc4FileName).st_size == 0:
        empty = []
        np.savetxt("mpc7.txt", empty, fmt="%s")

    else:
        ### mpc4_automanual2.txtを読み込み, near duplicatesに当たる行の組を抽出する ####################
        data = np.loadtxt(inputMpc4FileName, usecols=[3, 4, 5, 6, 7, 8, 9], ndmin=2)
        ra = data[:, 1] * 15 + data[:, 2] * 15 / 60 + data[:, 3] * 15 / 3600
        dec = np.abs(data[:, 4]) + data[:, 5] / 60 + data[:, 6] / 3600
        if "-" in str(data[:, 4]):
            dec = -1.0 * dec
        else:
            pass
        ra2 = ra.reshape(len(ra), 1)
        dec2 = dec.reshape(len(dec), 1)
        data2 = np.hstack((data, ra2, dec2))
        list1 = []
        for i in range(len(data2)):
            # condition
            time = data2[i, 0]
            lra = data2[i, 7] - DUPLICATE_THRESH_ARCSEC / 3600.0
            hra = data2[i, 7] + DUPLICATE_THRESH_ARCSEC / 3600.0
            ldec = data2[i, 8] - DUPLICATE_THRESH_ARCSEC / 3600.0
            hdec = data2[i, 8] + DUPLICATE_THRESH_ARCSEC / 3600.0
            tmp = np.where(
                (data2[:, 0] == time)
                & (data2[:, 7] > lra)
                & (data2[:, 7] < hra)
                & (data2[:, 8] > ldec)
                & (data2[:, 8] < hdec)
            )
            if len(tmp[0]) >= 2:
                tmp2 = tmp[0].tolist()
                list1.append(tmp2)

        # convert to tuple and then convert to list due to delete duplicate
        # 注: mpc4_automanual2.txtに記載のデータ列のうち, 重複していると見做せるほど近い列のindexの組の配列がlist1になる.
        # 　  例えば, 3列目と5列目, 4列目と6列目がそれぞれ近い場合, list1 = [[3,5], [4,6], [3,5], [4,6]] となる. (np.whereは条件に合致する要素のindexを返す)
        # 　  ここで, 上記の走査方法では同じ組み合わせが少なくとも2回ずつ現れてしまうことに注意. arrはそのような同じ組を消された後の配列になる.
        # 　  上記の例では arr = [[3,5], [4,6]] となる.
        arr = list(map(list, set(map(tuple, list1))))
        arr.sort()
        list2 = []
        for i in range(len(arr)):
            list2.append(arr[i][1:])
        # duplication index number
        # 注: duplicateIndexNumberListは, 重複している列の組みのうち最もindexが若いものを残すとして, 消すべきindexのリストになる
        # 　  上記の例ではduplicateIndexNumberList = [5, 6] となる.
        duplicateIndexNumberList = list(itertools.chain.from_iterable(list2))
        ########################################################################################

        ### mpc4_automanual2.txtをpanda dataFrameとして読み込み, #################################
        ### 上記重複の削除と光度が中央値から0.7以上外れたものの削除を行う ###############################
        df = pd.read_csv(
            inputMpc4FileName,
            header=None,
            sep="\s+",
            names=[
                "name",
                "year",
                "month",
                "day",
                "rah",
                "ram",
                "ras",
                "decd",
                "decm",
                "decs",
                "mag",
                "fil",
                "code",
            ],
            dtype={"decd": "object"},
        )
        # delete duplicate
        df1 = df.drop(df.index[duplicateIndexNumberList])
        # median value
        df3 = df1.groupby("name", as_index=False)["mag"].transform(np.median)
        # plus minus 0.7 mag
        df4 = df1[(df1["mag"] - df3["mag"] < 0.7) & (df1["mag"] - df3["mag"] > -0.7)]
        # ---K.S. modifies 2021/2/1---------------------
        dfCount = df4.groupby("name").count()["year"]
        df4WithCount = df4.assign(count=0)
        for index, row in df4WithCount.iterrows():
            df4WithCount.at[index, "count"] = dfCount[df4WithCount["name"][index]]
        if TWO_MEASUREMENT_PERMIT_MODE:
            df5 = df4
        else:
            df5 = df4[df4WithCount["count"] >= 3]
        # ----------------------------------------------
        nonFormattedMpcLines = df5.values.tolist()
        ########################################################################################

        ### フォーマット #########################################################################
        formattedMpcLines = []
        for i in range(len(nonFormattedMpcLines)):
            if (
                re.search(r"^H......", str(nonFormattedMpcLines[i][0]))
                or re.search(r"^K......", str(nonFormattedMpcLines[i][0]))
                or re.search(r"^J......", str(nonFormattedMpcLines[i][0]))
            ):
                # 仮符号天体 or 未知天体
                part1 = (
                    "     "
                    + str(nonFormattedMpcLines[i][0])
                    + "  "
                    + nonFormattedMpcLines[i][1]
                    + " "
                    + str(nonFormattedMpcLines[i][2]).zfill(2)
                )
                part2 = (
                    "{:.5f}".format(nonFormattedMpcLines[i][3]).zfill(8)
                    + " "
                    + str(nonFormattedMpcLines[i][4]).zfill(2)
                    + " "
                    + str(nonFormattedMpcLines[i][5]).zfill(2)
                )
                part3 = (
                    "{:.2f}".format(nonFormattedMpcLines[i][6]).zfill(5)
                    + " "
                    + str(nonFormattedMpcLines[i][7])
                    + " "
                    + str(nonFormattedMpcLines[i][8]).zfill(2)
                )
                part4 = (
                    "{:.2f}".format(nonFormattedMpcLines[i][9]).zfill(5)
                    + "         "
                    + "{:.1f}".format(nonFormattedMpcLines[i][10])
                )
                part5 = (
                    str(nonFormattedMpcLines[i][11])
                    + "      "
                    + str(nonFormattedMpcLines[i][12])
                )
                formattedMpcLines.append(
                    part1 + " " + part2 + " " + part3 + " " + part4 + " " + part5
                )
            else:
                # 確定番号天体
                part1 = (
                    str(nonFormattedMpcLines[i][0]).zfill(5)
                    + "         "
                    + nonFormattedMpcLines[i][1]
                    + " "
                    + str(nonFormattedMpcLines[i][2]).zfill(2)
                )
                part2 = (
                    "{:.5f}".format(nonFormattedMpcLines[i][3]).zfill(8)
                    + " "
                    + str(nonFormattedMpcLines[i][4]).zfill(2)
                    + " "
                    + str(nonFormattedMpcLines[i][5]).zfill(2)
                )
                part3 = (
                    "{:.2f}".format(nonFormattedMpcLines[i][6]).zfill(5)
                    + " "
                    + str(nonFormattedMpcLines[i][7])
                    + " "
                    + str(nonFormattedMpcLines[i][8]).zfill(2)
                )
                part4 = (
                    "{:.2f}".format(nonFormattedMpcLines[i][9]).zfill(5)
                    + "         "
                    + "{:.1f}".format(nonFormattedMpcLines[i][10])
                )
                part5 = (
                    str(nonFormattedMpcLines[i][11])
                    + "      "
                    + str(nonFormattedMpcLines[i][12])
                )
                formattedMpcLines.append(
                    part1 + " " + part2 + " " + part3 + " " + part4 + " " + part5
                )
        ########################################################################################

        np.savetxt("mpc7.txt", formattedMpcLines, fmt="%s")

except FileNotFoundError:
    print("Some previous files are not found in deldaburi4.py!", flush=True)
    print(traceback.format_exc(), flush=True)
    error = 1
    errorReason = 74

except Exception:
    print("Some errors occur in deldaburi4.py!", flush=True)
    print(traceback.format_exc(), flush=True)
    error = 1
    errorReason = 75

else:
    error = 0
    errorReason = 74

finally:
    errorFile = open("error.txt", "a")
    errorFile.write("{0:d} {1:d} 703 \n".format(error, errorReason))
    errorFile.close()

    if error == 1:
        print_detailed_log.print_detailed_log(dict(globals()))
