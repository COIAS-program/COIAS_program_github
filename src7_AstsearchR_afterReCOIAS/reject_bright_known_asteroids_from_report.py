#!/usr/bin/env python3
# -*- coding: UTF-8 -*

import traceback

try:
    #---get names of bright known asteroids-----------------
    fileBrightKnownAsteroids = open("bright_asteroid_MPC_names_in_the_field.txt","r")
    lines = fileBrightKnownAsteroids.readlines()
    namesOfBrightKnownAsteroids = []
    for l in range(len(lines)):
        namesOfBrightKnownAsteroids.append(lines[l].rstrip("\n"))
    fileBrightKnownAsteroids.close()
    #-------------------------------------------------------

    #---get data in pre_repo.txt----------------------------
    inputfileSendMpc = open("pre_repo.txt","r")
    lines = inputfileSendMpc.readlines()
    inputfileSendMpc.close()
    #-------------------------------------------------------

    #---compare names in pre_repo.txt and reject bright known asteroids---
    outputfileSendMpc = open("pre_repo.txt","w",newline="\n")
    for l in range(len(lines)):
        oneLineList = lines[l].split()
        flag = 0
        for l2 in range(len(namesOfBrightKnownAsteroids)):
            if oneLineList[0] == namesOfBrightKnownAsteroids[l2]:
                flag = 1
        if flag == 0:
            outputfileSendMpc.write(lines[l])
    outputfileSendMpc.close()
    #---------------------------------------------------------------------

except FileNotFoundError:
    print("Some previous files are not found in reject_bright_known_asteroids_from_report.py!")
    print(traceback.format_exc())
    error = 1
    errorReason = 74

except Exception:
    print("Some errors occur in reject_bright_known_asteroids_from_report.py!")
    print(traceback.format_exc())
    error = 1
    errorReason = 75

else:
    error = 0
    errorReason = 74

finally:
    errorFile = open("error.txt","a")
    errorFile.write("{0:d} {1:d} 706 \n".format(error,errorReason))
    errorFile.close()
