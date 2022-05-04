#!/usr/bin/env python3
# -*- coding: UTF-8 -*
import os
import sys
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

#---check all directories have ra_dec_jd_time.txt and search_astB.txt--------
for i in range(Ndata):
    if not os.path.isfile(directoryNames[i]+"/ra_dec_jd_time.txt"):
        print("There is no ra_dec_jd_time.txt in {}".format(directoryNames[i]))
    if not os.path.isfile(directoryNames[i]+"/search_astB.txt"):
        print("There is no search_astB.txt in {}".format(directoryNames[i]))
        """
        本当はファイルがなかった場合は例外などを送出して処理を止めたいが,
        フロントエンドとの協同をどのようにするか決まっていないのでひとまずメッセージを出すだけにする.
        2022.4.12 KS
        """
#----------------------------------------------------------------------------

#---add image number to all data in search_astB.txt in each directory--------
for i in range(Ndata):
    inputFile = open(directoryNames[i]+"/search_astB.txt","r")
    outputFile = open("search_astB_{0:d}.txt".format(i),"w",newline="\n")
    lines = inputFile.read().splitlines()
    for l in range(len(lines)):
        outputFile.write(lines[l]+" {0:d} ".format(i)+"\n")
    inputFile.close()
    outputFile.close()
#----------------------------------------------------------------------------

#---gather all search_astB_*.txt in the currrent directory to search_astB.txt in the current directory while sorting-
command = "cat "
for i in range(Ndata):
    command = command + "search_astB_{0:d}.txt ".format(i)
command = command + "|sort -n > search_astB.txt"
subprocess.run(command, shell=True)
#--------------------------------------------------------------------------------------------------------------------

#---copy asteroid name list stored in ~/.coias/orbit_data to the current directory-----------------------------------
subprocess.run("cp {0}/bright_asteroid_MPC_names_in_the_field.txt ./".format(directoryNames[0]),shell=True)
subprocess.run("cp {0}/name_conversion_list_in_the_field.txt ./".format(directoryNames[0]),shell=True)
#--------------------------------------------------------------------------------------------------------------------
