#!/usr/bin/env python3
# -*- coding: UTF-8 -*
# timestamp: 2022/08/04 17:30 sugiura
###################################################################################
# listb2.txtに記載の各点が, search_astB.txtに記載の既知天体の精密位置と
# 一致するかどうか照合し, 一致したら既知天体と見なす.
#
# 入力: listb2.txt 移動天体候補のリスト
# 　　  search_astB.txt 視野内の既知天体の精密位置のリスト
# 出力: match.txt
# 　　    listb2.txtのうちsearch_astB.txtのどれかと一致し既知天体と見なされた点のリスト
# 　　    書式: 確定番号or仮符号 jd ra[degree] dec[degree] mag magerr Xpixel Ypixel フィルター 画像番号
# 　　  nomatch.txt
# 　　    listb2.txtのうちsearch_astB.txtのどれとも一致しなかった点のリスト
# 　　    書式: trackletID jd ra[degree] dec[degree] mag magerr Xpixel Ypixel フィルター 画像番号
###################################################################################
import os
import numpy as np
import traceback
import glob
import print_progress
import print_detailed_log

try:
    # detect list
    # Revised 2020/2/14
    if os.stat("listb2.txt").st_size == 0:
        empty = []
        np.savetxt('match.txt', empty, fmt='%s')
        np.savetxt('nomatch.txt', empty, fmt='%s')
    else:
        tmp1 = str("listb2.txt")
        data1 = np.loadtxt(tmp1, usecols=[0, 1, 2, 3, 4, 5, 6, 7], ndmin=2)
        data1ImageNum = np.loadtxt(tmp1, usecols=[9], dtype='int')
        data1b = np.loadtxt(tmp1, dtype='str', ndmin=2)
        # search list
        tmp2List = sorted(glob.glob("search_astB_*.txt"))
        data2  = []
        data2b = []
        for tmp2 in tmp2List:
            data2.append(np.loadtxt(tmp2, usecols=[1, 2, 3, 4], ndmin=2))
            data2b.append(np.loadtxt(tmp2, dtype='str', usecols=[0, 5], ndmin=2))

        tmp3 = []
        tmp5 = []
        for i in range(len(data1)):
            print_progress.print_progress(nCheckPointsForLoop=4, nForLoop=len(data1), currentForLoop=i)
            
            l = 0
            for j in range(len(data2[data1ImageNum[i]])):
                if data1[i, 2] - 0.0005 < data2[data1ImageNum[i]][j, 1] and data1[i, 2] + 0.0005 > data2[data1ImageNum[i]][j, 1] and \
                   data1[i, 3] - 0.0005 < data2[data1ImageNum[i]][j, 2] and data1[i, 3] + 0.0005 > data2[data1ImageNum[i]][j, 2]:
                    tmp3 = np.append(tmp3, data2b[data1ImageNum[i]][j, 0:1])
                    tmp3 = np.append(tmp3, data1b[i, 1:9])
                    tmp3 = np.append(tmp3, data2b[data1ImageNum[i]][j, 1:2])
                    l = l + 1
            if l == 0:
                tmp5 = np.append(tmp5, data1b[i])

        # Revised 2020.2.13
        if len(tmp3) == 0:
            np.savetxt('match.txt', tmp3, fmt='%s')
        else:
            tmp4 = tmp3.reshape(int(len(tmp3) / 10), 10)
            np.savetxt('match.txt', tmp4, fmt='%s')
        if len(tmp5) == 0:
            np.savetxt('nomatch.txt', tmp5, fmt='%s')
        else:
            tmp6 = tmp5.reshape(int(len(tmp5) / 10), 10)
            np.savetxt('nomatch.txt', tmp6, fmt='%s')

except FileNotFoundError:
    print("Some previous files are not found in match2D.py!",flush=True)
    print(traceback.format_exc(),flush=True)
    error = 1
    errorReason = 54

except Exception:
    print("Some errors occur in match2D.py!",flush=True)
    print(traceback.format_exc(),flush=True)
    error = 1
    errorReason = 55

else:
    error = 0
    errorReason = 54

finally:
    errorFile = open("error.txt","a")
    errorFile.write("{0:d} {1:d} 504 \n".format(error,errorReason))
    errorFile.close()

    if error==1:
        print_detailed_log.print_detailed_log(dict(globals()))
