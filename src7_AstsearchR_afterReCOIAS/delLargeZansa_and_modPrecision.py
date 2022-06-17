#!/usr/bin/env python3
# -*- coding: UTF-8 -*
import sys
import traceback

try:
    argc = len(sys.argv)
    if argc != 2:
        print("please input second argument of 1 or 2")
        print("if you need one decimal: 1, if two decimal: 2")
        raise ValueError

    if (sys.argv[1] != "1") and (sys.argv[1] != "2"):
        print("please input second argument of 1 or 2")
        print("if you need one decimal: 1, if two decimal: 2")
        raise ValueError

    inputFileName = "result.txt"
    outputFileName = "pre_repo.txt"
    inputFile = open(inputFileName, "r")
    outputFile = open(outputFileName, "w")

    inputLines = inputFile.readlines()
    outputLines = []

    for i in range(len(inputLines)):
        contents = inputLines[i].split()
        Xres = float(contents[14])
        Yres = float(contents[15])

        if (abs(Xres) < 0.7) and (abs(Yres) < 0.7):
            str_list = list(inputLines[i][0:80]) + list("\n")

            if sys.argv[1] == "1":
                str_list[55] = ' '

            outputLines.append("".join(str_list))

    outputFile.writelines(outputLines)

    inputFile.close()
    outputFile.close()

except FileNotFoundError:
    print("Some previous files are not found in delLargeZansa_and_modPrecision.py!")
    print(traceback.format_exc())
    error = 1
    errorReason = 74

except Exception:
    print("Some errors occur in delLargeZansa_and_modPrecision.py!")
    print(traceback.format_exc())
    error = 1
    errorReason = 75

else:
    error = 0
    errorReason = 74

finally:
    errorFile = open("error.txt","a")
    errorFile.write("{0:d} {1:d} 705 \n".format(error,errorReason))
    errorFile.close()
