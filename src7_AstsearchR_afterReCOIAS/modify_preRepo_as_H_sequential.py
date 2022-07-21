#!/usr/bin/env python3
# -*- coding: UTF-8 -*
#timestamp: 2022/7/21 11:00 sugiura
import traceback
import os
import re
import subprocess

try:
    completed_process = subprocess.run("sort -n -o pre_repo.txt pre_repo.txt", shell=True)
    if completed_process.returncode!=0: raise Exception

    #---get H conversion list from pre repo-----------------------
    filePreRepo = open("pre_repo.txt","r")
    lines = filePreRepo.readlines()
    filePreRepo.close()

    HOldNameList = []
    HNewNameList = []
    k=1
    for line in lines:
        thisName = line.split()[0]
        if (re.search(r'^H......', thisName)!=None) and (thisName not in HOldNameList):
            if len(HOldNameList)==0:
                kinit = int(thisName.lstrip("H"))
                HOldNameList.append(thisName)
                HNewNameList.append(thisName)
            else:
                HOldNameList.append(thisName)
                HNewNameList.append("H"+str(kinit+k).rjust(6,"0"))
                k += 1
    #-------------------------------------------------------------


    #---add this conversion to H_conversion_list_automanual2.txt--
    fileHConversionList2 = open("H_conversion_list_automanual2.txt","r")
    lines = fileHConversionList2.readlines()
    fileHConversionList2.close()

    fileHConversionList3 = open("H_conversion_list_automanual3.txt","w",newline="\n")
    for line in lines:
        if re.search(r'^H......', line.split()[2])==None:
            fileHConversionList3.write(line.rstrip("\n") + " " + line.split()[2] + "\n")
        elif line.split()[2] not in HOldNameList:
            fileHConversionList3.write(line.rstrip("\n") + " " + "rejected \n")
        else:
            for l in range(len(HOldNameList)):
                if line.split()[2]==HOldNameList[l]:
                    fileHConversionList3.write(line.rstrip("\n") + " " + HNewNameList[l] + "\n")
                    break
    fileHConversionList3.close()
    #-------------------------------------------------------------


    #---modify pre_repo.txt as H numbers become sequential--------
    filePreRepo = open("pre_repo.txt","r")
    lines = filePreRepo.readlines()
    filePreRepo.close()

    filePreRepo2 = open("pre_repo2.txt","w",newline="\n")
    for line in lines:
        isMatch = False
        for l in range(len(HOldNameList)):
            if line.split()[0]==HOldNameList[l]:
                isMatch = True
                filePreRepo2.write(line.replace(HOldNameList[l], HNewNameList[l]))
                break
        if not isMatch:
            filePreRepo2.write(line)
    filePreRepo2.close()
    #-------------------------------------------------------------
    
    
except FileNotFoundError:
    print("Some previous files are not found in modify_preRepo_as_H_sequential!")
    print(traceback.format_exc())
    error = 1
    errorReason = 74

except Exception:
    print("Some errors occur in modify_preRepo_as_H_sequential!")
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
