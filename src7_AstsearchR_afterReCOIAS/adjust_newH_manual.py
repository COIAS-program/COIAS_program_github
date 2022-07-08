#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#timestamp: 2022/7/8 8:30 sugiura

import re
import os
import traceback

class NothingToDo(Exception):
    pass

try:
    #---assess manual mode is done or not-----------
    if (not os.path.isfile("mpc4_m.txt")) or (not os.path.isfile("H_conversion_list_manual.txt")) or (not os.path.isfile("redisp_manual.txt")):
        raise NothingToDo
    #------------------------------------------------
    
    
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


    #---assess where Hmax in redisp.txt is one smaller than HMin in redisp_manual.txt
    redispManualFile = open("redisp_manual.txt","r")
    lines = redispManualFile.readlines()
    redispManualFile.close()

    NHMin = 100000000 #VERY LARGE VALUE
    for line in lines:
        contents = line.split()
        if re.search(r'^H......',contents[0])!=None:
            NH = int(contents[0].lstrip("H"))
            if NH < NHMin:
                NHMin = NH

    ## if HMax in redisp.txt is one smaller than HMin in redisp_manual.txt,
    ## then H numbers become sequential and it's OK
    if NHMax + 1 == NHMin:
        raise NothingToDo
    #------------------------------------------------


    #---get adjusted new H list----------------------
    newHList = []
    adjustedNewHList = []

    fileHConvListManual = open("H_conversion_list_manual.txt","r")
    lines = fileHConvListManual.readlines()
    fileHConvListManual.close()

    k = 1
    for line in lines:
        newHList.append(line.split()[1])
        adjustedNewHList.append("H"+str(NHMax+k).rjust(6, '0'))
        k += 1
    #------------------------------------------------


    #---adjust H_conversion_list_manual.txt and mpc4_m.txt
    fileHConvListManual = open("H_conversion_list_manual.txt","w",newline="\n")
    for line in lines:
        for l in range(len(adjustedNewHList)):
            if line.split()[1] == newHList[l]:
                newline = line.replace(newHList[l],adjustedNewHList[l])
                break
        fileHConvListManual.write(newline)
    fileHConvListManual.close()

    fileMpc4M = open("mpc4_m.txt","r")
    lines = fileMpc4M.readlines()
    fileMpc4M.close()

    fileMpc4M = open("mpc4_m.txt","w")
    for line in lines:
        for l in range(len(adjustedNewHList)):
            if line.split()[0] == newHList[l]:
                break
        fileMpc4M.write(line.replace(newHList[l],adjustedNewHList[l]))
    fileMpc4M.close()
    #------------------------------------------------

except NothingToDo:
    error = 0
    errorReason = 74

except FileNotFoundError:
    print("Some previous files are not found in adjust_newH_manual.py!")
    print(traceback.format_exc())
    error = 1
    errorReason = 74

except Exception:
    print("Some errors occur in adjust_newH_manual.py!")
    print(traceback.format_exc())
    error = 1
    errorReason = 75

else:
    error = 0
    errorReason = 74

finally:
    errorFile = open("error.txt","a")
    errorFile.write("{0:d} {1:d} 710 \n".format(error,errorReason))
    errorFile.close()
