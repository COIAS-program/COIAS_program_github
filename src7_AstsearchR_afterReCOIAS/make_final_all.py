#!/usr/bin/env python3
# -*- coding: UTF-8 -*
#timestamp: 2022/6/26 17:30 sugiura

import glob
import os
import traceback
import re

try:
    #---open output file and write header-----------------------
    outputFile = open("final_all.txt","w",newline="\n")
    originalImgNames = sorted(glob.glob('warp-*.fits'))
    for i in range(len(originalImgNames)):
        outputFile.write("{:d}: ".format(i)+originalImgNames[i]+"\n")
    #-----------------------------------------------------------

    #---get H conversion list-----------------------------------
    HConversionListFile = open("H_conversion_list_automanual.txt","r")
    lines = HConversionListFile.readlines()
    HOld = []
    HNew = []
    for l in range(len(lines)):
        lineList = lines[l].split()
        HOld.append(lineList[0])
        HNew.append(lineList[1])
    HConversionListFile.close()
    #-----------------------------------------------------------

    #---output all.txt only in pre_repo.txt---------------------
    preRepoFile = open("pre_repo.txt","r")
    preRepoLines = preRepoFile.readlines()
    HPreRepoOld="NoMeaning"
    for l in range(len(preRepoLines)):
        preRepoOneLine = preRepoLines[l]
        preRepoOneLineList = preRepoOneLine.split()
        
        # search H old name########################
        HPreRepo = preRepoOneLineList[0]
        flag=0
        for l2 in range(len(HNew)):
            if HNew[l2]==HPreRepo:
                HPreRepoOld = HOld[l2]
                flag=1
        # search the same line in all.txt##########
        if flag==1:
            preRepoOneLine = preRepoOneLine.replace(HPreRepo,HPreRepoOld)
        allFile = open("all_automanual.txt","r")
        lines = allFile.readlines()
        for l3 in range(len(lines)):
            if preRepoOneLine[0:31]==lines[l3][0:31]:
                outputFile.write(lines[l3].replace(HPreRepoOld,HPreRepo))
                break
        allFile.close()

        # output contents of orbital_element_summary_web.txt###
        if (l==len(preRepoLines)-1 or len(preRepoLines[l+1].split())==0 or preRepoLines[l+1].split()[0]!=preRepoOneLineList[0]) and os.path.isfile("orbital_elements_summary_web.txt"):
            if len(preRepoOneLineList[0])==7:
                headSpace="     "
            elif len(preRepoOneLineList[0])==5:
                headSpace=""
            
            orbElemFile = open("orbital_elements_summary_web.txt","r")
            orbElemLines = orbElemFile.readlines()
            orbElemFile.close()

            for l2 in range(len(orbElemLines)):
                if orbElemLines[l2].split()[0].rstrip(":")==preRepoOneLineList[0]:
                    outputFile.write(headSpace + orbElemLines[l2])
                    outputFile.write(headSpace + orbElemLines[l2+1])
                    outputFile.write(headSpace + orbElemLines[l2+2])
                    outputFile.write("\n")
                    break

    preRepoFile.close()
    outputFile.close()
    #-----------------------------------------------------------

except FileNotFoundError:
    print("Some previous files are not found in make_final_all.py!")
    print(traceback.format_exc())
    error = 1
    errorReason = 74

except Exception:
    print("Some errors occur in make_final_all.py!")
    print(traceback.format_exc())
    error = 1
    errorReason = 75

else:
    error = 0
    errorReason = 74

finally:
    errorFile = open("error.txt","a")
    errorFile.write("{0:d} {1:d} 707 \n".format(error,errorReason))
    errorFile.close()
