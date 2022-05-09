#!/usr/bin/env python3
# -*- coding: UTF-8 -*
import subprocess
import traceback

try:
    #---read precise_orbit_directories.txt---------------------------------------
    Ndata = 5
    directoryNames = []
    isCorrectDirectory = []
    preciseOrbitDirectoriesFile = open("precise_orbit_directories.txt","r")
    for i in range(Ndata):
        content = preciseOrbitDirectoriesFile.readline().split()
        directoryNames.append(content[0])
        isCorrectDirectory.append(int(content[1]))
    preciseOrbitDirectoriesFile.close()
    #----------------------------------------------------------------------------

    #---process numbered_new2B.txt and karifugo_new2B.txt in each directory------
    errorList=[]
    for i in range(Ndata):
        if isCorrectDirectory[i]==0:
            completed_process = subprocess.run("grep -E \"^19|^20\" {0}/karifugo_new2B.txt > {0}/karifugo_new2C.txt".format(directoryNames[i]),shell=True)
            errorList.append(completed_process.returncode)
            completed_process = subprocess.run("cat {0}/numbered_new2B.txt {0}/karifugo_new2C.txt |sort -n > {0}/search_astpre.txt".format(directoryNames[i]),shell=True)
            errorList.append(completed_process.returncode)
            completed_process = subprocess.run("sed 's/--/30.0/g;' {0}/search_astpre.txt |sed 's/ (1999 19 //g;' |sed 's/ (1981 2 //g;'|sed 's/ - / /g;'> {0}/search_astB.txt".format(directoryNames[i]),shell=True)
            errorList.append(completed_process.returncode)

    for e in errorList:
        if e!=0:
            raise FileNotFoundError
    #----------------------------------------------------------------------------

except FileNotFoundError:
    print("Some previous files are not found in make_search_astB_in_each_directory.py!")
    print(traceback.format_exc())
    error = 1
    errorReason = 44

except Exception:
    print("Some errors occur in make_search_astB_in_each_directory.py!")
    print(traceback.format_exc())
    error = 1
    errorReason = 45

else:
    error = 0
    errorReason = 44

finally:
    errorFile = open("error.txt","a")
    errorFile.write("{0:d} {1:d} 403 \n".format(error,errorReason))
    errorFile.close()
