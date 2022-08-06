#!/usr/bin/env python3
# -*- coding: UTF-8 -*
#Timestamp: 2022/08/06 19:30 sugiura
###########################################################################################
# jd, ra, decが一致している行が2行以上あった場合, 2つ目以降をダブりとして削除する.
# さらに, 同一の名前の天体のデータで等級が中央値から0.7以上外れているものも削除し,
# その上で同一の名前の天体のデータ数が2以下になったらその名前の天体のデータを全て削除する.
#
# 入力: mpc4_automanual2.txt
# 出力: mpc7.txt
# 　　    mpc4_automanual2.txtに対して上記のダブり除去, 等級が大きずれているもの除去,
# 　　    データが2行以下になる天体の除去を行った結果を書き出したもの.
###########################################################################################
import itertools
import re

import numpy as np
import pandas as pd
import traceback
import os

try:
    # detect list
    tmp1 = "mpc4_automanual2.txt"
    if os.stat(tmp1).st_size == 0:
        empty = []
        np.savetxt('mpc7.txt', empty, fmt="%s")

    else:
        df = pd.read_csv(tmp1, header=None, sep="\s+",
                         names=["name", "year", "month", "day", "rah", "ram", "ras", "decd", "decm", "decs", "mag", "fil","code"],
                         dtype={'decd': 'object'})

        # print(df[df.duplicated(subset=["year","month","day","rah","ram","ras","decd","decm","decs","mag","fil","code"])])

        # tmp2 = path_name+str("/memo.txt")
        # tmp3 = path_name+str("/mpc2.txt")
        data1 = open(tmp1, "r")
        # data2 = open(tmp2,"r")
        data = np.loadtxt(tmp1, usecols=[3, 4, 5, 6, 7, 8, 9])
        ra = data[:, 1] * 15 + data[:, 2] * 15 / 60 + data[:, 3] * 15 / 3600
        dec = data[:, 4] + data[:, 5] / 60 + data[:, 6] / 3600
        ra2 = ra.reshape(len(ra), 1)
        dec2 = dec.reshape(len(dec), 1)
        data2 = np.hstack((data, ra2, dec2))
        list1 = []
        for i in range(len(data2)):
            # np.where((data2[:,0]== data2[i,0]))
    
            # condition
            time = data2[i, 0]
            lra = data2[i, 7] - 0.0005
            hra = data2[i, 7] + 0.0005
            ldec = data2[i, 8] - 0.0005
            hdec = data2[i, 8] + 0.0005
            # print(np.where((data2[:,0] == time) & (data2[:,7] > lra) & (data2[:,7] < hra)& (data2[:,8] > ldec) & (data2[:,8] < hdec))
            tmp = np.where((data2[:, 0] == time) & (data2[:, 7] > lra) & (data2[:, 7] < hra) & (data2[:, 8] > ldec) & (data2[:, 8] < hdec))
            if len(tmp[0]) >= 2:
                tmp2 = tmp[0].tolist()
                list1.append(tmp2)
        
        # convert to tuple and then convert to list due to delete duplicate
        arr = list(map(list, set(map(tuple, list1))))
        arr.sort()
        list2 = []
        for i in range(len(arr)):
            list2.append(arr[i][1:])
        # duplication index number
        list5 = list(itertools.chain.from_iterable(list2))

        # delete duplicate
        df1 = df.drop(df.index[list5])
        # df1.to_csv('./test.txt',header=False,index = False)
        # median value
        df3 = df1.groupby('name', as_index=False)["mag"].transform(np.median)
        # plus minus 0.5 mag
        df4 = df1[(df1["mag"] - df3["mag"] < 0.7) & (df1["mag"] - df3["mag"] > -0.7)]

        # ---K.S. modifies 2021/2/1---------------------
        dfCount = df4.groupby('name').count()["year"]
        df4WithCount = df4.assign(count=0)
        for index, row in df4WithCount.iterrows():
            df4WithCount.at[index, "count"] = dfCount[df4WithCount["name"][index]]
        df5 = df4[df4WithCount["count"] >= 3]
        # ----------------------------------------------
        # df4.groupby('name').count()['year'] >=3
        # def keepindex(d):
        #    return pd.DataFrame({
        #    df4.groupby('name').count()['year'] >=3 


        list3 = df5.values.tolist()

        list4 = []
        for i in range(len(list3)):
            # K. S. modify 2022/6/26
            if (re.search(r'^H......', str(list3[i][0])) or re.search(r'^K......', str(list3[i][0])) or re.search(r'^J......', str(list3[i][0]))):
                part1 = '     ' + str(list3[i][0]) + '  ' + list3[i][1] + ' ' + str(list3[i][2]).zfill(2)
                part2 = "{:.5f}".format(list3[i][3]).zfill(8) + ' ' + str(list3[i][4]).zfill(2) + ' ' + str(list3[i][5]).zfill(2)
                part3 = "{:.2f}".format(list3[i][6]).zfill(5) + ' ' + str(list3[i][7]) + ' ' + str(list3[i][8]).zfill(2)
                part4 = "{:.2f}".format(list3[i][9]).zfill(5) + '         ' + "{:.1f}".format(list3[i][10])
                part5 = str(list3[i][11]) + '      ' + str(list3[i][12])
                # print(part1+ ' ' + part2 + ' ' + part3 + ' ' + part4 + ' ' + part5)
                list4.append(part1 + ' ' + part2 + ' ' + part3 + ' ' + part4 + ' ' + part5)
            else:
                part1 = str(list3[i][0]).zfill(5) + '         ' + list3[i][1] + ' ' + str(list3[i][2]).zfill(2)
                part2 = "{:.5f}".format(list3[i][3]).zfill(8) + ' ' + str(list3[i][4]).zfill(2) + ' ' + str(list3[i][5]).zfill(2)
                part3 = "{:.2f}".format(list3[i][6]).zfill(5) + ' ' + str(list3[i][7]) + ' ' + str(list3[i][8]).zfill(2)
                part4 = "{:.2f}".format(list3[i][9]).zfill(5) + '         ' + "{:.1f}".format(list3[i][10])
                part5 = str(list3[i][11]) + '      ' + str(list3[i][12])
                list4.append(part1 + ' ' + part2 + ' ' + part3 + ' ' + part4 + ' ' + part5)

        np.savetxt('mpc7.txt', list4, fmt="%s")

except FileNotFoundError:
    print("Some previous files are not found in deldaburi4.py!")
    print(traceback.format_exc())
    error = 1
    errorReason = 74

except Exception:
    print("Some errors occur in deldaburi4.py!")
    print(traceback.format_exc())
    error = 1
    errorReason = 75

else:
    error = 0
    errorReason = 74

finally:
    errorFile = open("error.txt","a")
    errorFile.write("{0:d} {1:d} 703 \n".format(error,errorReason))
    errorFile.close()
