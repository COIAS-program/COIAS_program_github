#!/usr/bin/env python3
# -*- coding: UTF-8 -*
import subprocess

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
for i in range(Ndata):
    if isCorrectDirectory[i]==0:
        subprocess.run("grep -E \"^19|^20\" {0}/karifugo_new2B.txt > {0}/karifugo_new2C.txt".format(directoryNames[i]),shell=True)
        subprocess.run("cat {0}/numbered_new2B.txt {0}/karifugo_new2C.txt |sort -n > {0}/search_astpre.txt".format(directoryNames[i]),shell=True)
        subprocess.run("sed 's/--/30.0/g;' {0}/search_astpre.txt |sed 's/ (1999 19 //g;' |sed 's/ (1981 2 //g;'|sed 's/ - / /g;'> {0}/search_astB.txt".format(directoryNames[i]),shell=True)
#----------------------------------------------------------------------------
