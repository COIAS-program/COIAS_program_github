#!/usr/bin/env python3
# -*- coding: UTF-8 -*
#Timestamp: 2022/08/05 22:30 sugiura
##################################################################################################
# listb3.txtに記された手動測定天体の位置を, search_astB.txtに記載の既知天体の位置と照合し,
# 一致したらその天体を既知天体と見なして名前を付け替える.
# さらに既知天体はmatch_manual.txt, 新天体はnomatch_manual.txtに振り分ける.
# 入力: listb3.txt
# 　　  search_astB.txt
# 出力: match_manual.txt 既知天体の情報
# 　　    書式: 確定番号or仮符号 jd ra[degree] dec[degree] mag magerr Xpixel Ypixel フィルター 画像番号
# 　　  nomatch_manual.txt 新天体の情報
# 　　    書式: 新天体番号(Hなし) jd ra[degree] dec[degree] mag magerr Xpixel Ypixel フィルター 画像番号
##################################################################################################
import os
import numpy as np
import traceback
import print_detailed_log

try:
    # Revised 2020/2/14
    if os.stat("listb3.txt").st_size == 0:
        empty = []
        np.savetxt('match_manual.txt', empty, fmt='%s')
        np.savetxt('nomatch_manual.txt', empty, fmt='%s')
    else:
        tmp1 = str("listb3.txt")
        data1 = np.loadtxt(tmp1, usecols=[0, 1, 2, 3, 4, 5, 6, 7], ndmin=2)
        data1b = np.loadtxt(tmp1, dtype='str', ndmin=2)

        # search list
        tmp2 = str("search_astB.txt")
        data2 = np.loadtxt(tmp2, usecols=[1, 2, 3, 4], ndmin=2)
        data2b = np.loadtxt(tmp2, dtype='str', usecols=[0, 5], ndmin=2)

        tmp3 = []
        tmp5 = []
        for i in range(len(data1)):
            l = 0
            for j in range(len(data2)):
                if data1[i, 1] - 0.000001 < data2[j, 0] and data1[i, 1] + 0.000001 > data2[j, 0] and \
                   data1[i, 2] - 0.0005 < data2[j, 1] and data1[i, 2] + 0.0005 > data2[j, 1] and \
                   data1[i, 3] - 0.0005 < data2[j, 2] and data1[i, 3] + 0.0005 > data2[j, 2]:
                    tmp3 = np.append(tmp3, data2b[j, 0:1])
                    tmp3 = np.append(tmp3, data1b[i, 1:9])
                    tmp3 = np.append(tmp3, data2b[j, 1:2])
                    l = l + 1
            if l == 0:
                tmp5 = np.append(tmp5, data1b[i])

    
        # Revised 2020.2.13
        if len(tmp3) == 0:
            np.savetxt('match_manual.txt', tmp3, fmt='%s')
        else:
            tmp4 = tmp3.reshape(int(len(tmp3) / 10), 10)
            np.savetxt('match_manual.txt', tmp4, fmt='%s')
        if len(tmp5) == 0:
            np.savetxt('nomatch_manual.txt', tmp5, fmt='%s')
        else:
            tmp6 = tmp5.reshape(int(len(tmp5) / 10), 10)
            np.savetxt('nomatch_manual.txt', tmp6, fmt='%s')

except FileNotFoundError:
    print("Some previous files are not found in match2E.py!",flush=True)
    print(traceback.format_exc(),flush=True)
    error = 1
    errorReason = 84

except Exception:
    print("Some errors occur in match2E.py!",flush=True)
    print(traceback.format_exc(),flush=True)
    error = 1
    errorReason = 85

else:
    error = 0
    errorReason = 84

finally:
    errorFile = open("error.txt","a")
    errorFile.write("{0:d} {1:d} 803 \n".format(error,errorReason))
    errorFile.close()

    if error==1:
        print_detailed_log.print_detailed_log(dict(globals()))
