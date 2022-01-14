#!/usr/bin/env python3
# -*- coding: UTF-8 -*
import sys

argc = len(sys.argv)
if argc != 2:
    print("please input second argument of 1 or 2")
    print("if you need one decimal: 1, if two decimal: 2")
    sys.exit()

if (sys.argv[1] != "1") and (sys.argv[1] != "2"):
    print("please input second argument of 1 or 2")
    print("if you need one decimal: 1, if two decimal: 2")
    sys.exit()

inputFileName = "result.txt"
outputFileName = "pre_repo.txt"
inputFile = open(inputFileName, "r")
outputFile = open(outputFileName, "w")

inputLines = inputFile.readlines()
outputLines = []

for i in range(len(inputLines)):
    Xres = float(inputLines[i][88:93])
    Yres = float(inputLines[i][99:103])

    if (abs(Xres) < 0.7) and (abs(Yres) < 0.7):
        str_list = list(inputLines[i][1:81]) + list("\n")

        if sys.argv[1] == "1":
            str_list[55] = ' '

        outputLines.append("".join(str_list))

outputFile.writelines(outputLines)

inputFile.close()
outputFile.close()