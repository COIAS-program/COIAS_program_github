#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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

