#!/usr/bin/env python3
# -*- coding: UTF-8 -*

import glob

#---open output file and write header-----------------------
outputFile = open("final_all.txt","w",newline="\n")
originalImgNames = sorted(glob.glob('warp-*.fits'))
for i in range(len(originalImgNames)):
    outputFile.write("{:d}: ".format(i)+originalImgNames[i]+"\n")
#-----------------------------------------------------------

#---get H conversion list-----------------------------------
HConversionListFile = open("H_conversion_list.txt","r")
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
for l in range(len(preRepoLines)):
    preRepoOneLine = preRepoLines[l]
    preRepoOneLineList = preRepoOneLine.split()
    #search H old name########################
    HPreRepo = preRepoOneLineList[0]
    flag=0
    for l2 in range(len(HNew)):
        if HNew[l2]==HPreRepo:
            HPreRepoOld = HOld[l2]
            flag=1
    #search the same line in all.txt##########
    if flag==1:
        preRepoOneLine = preRepoOneLine.replace(HPreRepo,HPreRepoOld)
    allFile = open("all.txt","r")
    lines = allFile.readlines()
    for l3 in range(len(lines)):
        if preRepoOneLine[0:31]==lines[l3][0:31]:
            outputFile.write(lines[l3].replace(HPreRepoOld,HPreRepo))
    allFile.close()

preRepoFile.close()
outputFile.close()
#-----------------------------------------------------------
