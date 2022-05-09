#!/usr/bin/env python3
# -*- coding: UTF-8 -*
import os
import numpy as np
import traceback

try:
    # detect list
    # Revised 2020/2/14
    if os.stat("listb2.txt").st_size == 0:
        empty = []
        np.savetxt('match.txt', empty, fmt='%s')
        np.savetxt('nomatch.txt', empty, fmt='%s')
    else:
        tmp1 = str("listb2.txt")
        data1 = np.loadtxt(tmp1, usecols=[0, 1, 2, 3, 4, 5, 6, 7])
        data1b = np.loadtxt(tmp1, dtype='str')
        # search list
        tmp2 = str("search_astB.txt")
        data2 = np.loadtxt(tmp2, usecols=[1, 2, 3, 4])
        data2b = np.loadtxt(tmp2, dtype='str', usecols=[0, 5])
        # time list
        time_list = np.unique(data1[:, 1])
        # file_list
        file_list = np.unique(data2b[:, 1])

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
                for n in range(len(time_list)):
                    if time_list[n] - 0.00001 < float(data1b[i, 1]) and time_list[n] + 0.00001 > float(data1b[i, 1]):
                        # print(n,file_list[n])
                        tmp5 = np.append(tmp5, data1b[i])
                        tmp5 = np.append(tmp5, file_list[n])

        # print(data1[i],data2b[j,0])
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
    print("Some previous files are not found in match2D.py!")
    print(traceback.format_exc())
    error = 1
    errorReason = 54

except Exception:
    print("Some errors occur in match2D.py!")
    print(traceback.format_exc())
    error = 1
    errorReason = 55

else:
    error = 0
    errorReason = 54

finally:
    errorFile = open("error.txt","a")
    errorFile.write("{0:d} {1:d} 504 \n".format(error,errorReason))
    errorFile.close()
