#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#timestamp: 2022/6/8 16:30 sugiura

import re
import traceback

try:
    #---get maximum H number from redisp.txt---------
    redispFile = open("redisp.txt","r")
    lines = redispFile.readlines()
    redispFile.close()

    NHMax = 0
    for line in lines:
        contents = line.split()
        if re.search(r'^H......',contents[0])!=None:
            NH = int(contents[0].lstrip("H"))
            if NH > NHMax:
                NHMax = NH
    #------------------------------------------------


    #---get H conversion list and output it----------
    mpcMFile = open("mpc_m.txt","r")
    lines = mpcMFile.readlines()
    mpcMFile.close()

    oldHList = []
    newHList = []
    k=1
    for line in lines:
        contents = line.split()
        if re.search(r'^H......',contents[0])!=None:
            strH = contents[0]
            findFlag = False
            for oldH in oldHList:
                if oldH == strH:
                    findFlag = True
            if not findFlag:
                oldHList.append(strH)
                newHList.append("H"+str(NHMax+k).rjust(6,'0'))
                k += 1

    HConversionListFile = open("H_conversion_list_manual.txt","w",newline="\n")
    for l in range(len(oldHList)):
        HConversionListFile.write(oldHList[l]+" "+newHList[l]+"\n")
    HConversionListFile.close()
    #------------------------------------------------


    #---make mpc4_m.txt and redisp_manual.txt--------
    inputFile = open("all_m.txt","r")
    mpc4MFile = open("mpc4_m.txt","w",newline="\n")
    redispMFile = open("redisp_manual.txt","w",newline="\n")

    lines = inputFile.readlines()
    inputFile.close()
    for line in lines:
        contents = line.split()
        replaceHl=0
        for l in range(len(oldHList)):
            if contents[0]==oldHList[l]:
                replaceHl = l
        if len(oldHList)!=0:
            line = line.replace(oldHList[replaceHl], newHList[replaceHl])
        contents = line.split()

        mpc4MFile.write(line[0:80]+"\n")
        redispMFile.write(contents[0]+" "+contents[13]+" "+contents[16]+" "+contents[17]+"\n")

    mpc4MFile.close()
    redispMFile.close()
    #------------------------------------------------

except FileNotFoundError:
    print("Some previous files are not found in make_mpc4_and_redisp_manual.py!")
    print(traceback.format_exc())
    error = 1
    errorReason = 84

except Exception:
    print("Some errors occur in make_mpc4_and_redisp_manual.py!")
    print(traceback.format_exc())
    error = 1
    errorReason = 85

else:
    error = 0
    errorReason = 84

finally:
    errorFile = open("error.txt","a")
    errorFile.write("{0:d} {1:d} 808 \n".format(error,errorReason))
    errorFile.close()
