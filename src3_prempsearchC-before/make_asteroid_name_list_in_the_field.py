#!/usr/bin/env python3
# -*- coding: UTF-8 -*
import subprocess
import re
import numpy as np
from changempc import *


#---read precise_orbit_directories.txt------------------------------------------------------
Ndata = 5
directoryNames = []
isCorrectDirectory = []
preciseOrbitDirectoriesFile = open("precise_orbit_directories.txt","r")
for i in range(Ndata):
    content = preciseOrbitDirectoriesFile.readline().split()
    directoryNames.append(content[0])
    isCorrectDirectory.append(int(content[1]))
preciseOrbitDirectoriesFile.close()
#-------------------------------------------------------------------------------------------

#---make bright asteroid MPC name list in each directory------------------------------------
## remove a character "\"
subprocess.run(r"sed -e 's/\\//g' bright_asteroid_raw_names_in_the_field.txt > bright_asteroid_raw_names_in_the_field2.txt",shell=True)
## subtract number from numbered asteroids and karifugo from karifugo asteroids
subprocess.run("awk -F' ' '$1 ~ /^[1-9]/ && $2 ~ /^[A-Z]/ && $2 !~ /[A-Z][A-Z][0-9]*/ && $2 != 'P-L' && $2 != 'T-1' && $2 != 'T-2' && $2 != 'T-3' {print $1}' bright_asteroid_raw_names_in_the_field2.txt > bright_asteroid_raw_names_in_the_field3.txt",shell=True)
subprocess.run("awk -F' ' '$1 ~ /^[1-9]/ && $2 ~ /^[1-2]/ || $3 == 'P-L' || $3 == 'T-1' || $3 == 'T-2' || $3 == 'T-3' {print $1}' bright_asteroid_raw_names_in_the_field2.txt >> bright_asteroid_raw_names_in_the_field3.txt",shell=True)
subprocess.run("awk -F' ' '$1 ~ /^[1-2]/ && $2 ~ /[A-Z][A-Z][0-9]*/ || $2 == 'P-L' || $2 == 'T-1' || $2 == 'T-2' || $2 == 'T-3' {print $1,$2}' bright_asteroid_raw_names_in_the_field2.txt >> bright_asteroid_raw_names_in_the_field3.txt",shell=True)
## remove space between karifugo
subprocess.run("sed 's/ //g' bright_asteroid_raw_names_in_the_field3.txt > bright_asteroid_raw_names_in_the_field4.txt",shell=True)

## transform to MPC format name
inputFile = open("bright_asteroid_raw_names_in_the_field4.txt","r")
lines = inputFile.readlines()
inputFile.close()
brightAsteroidsMPCNames = []
for l in range(len(lines)):
    if re.search(r'[a-zA-Z]',lines[l]):
        brightAsteroidsMPCNames.append(get_MPC_format_name_for_karifugo_asteroids(lines[l].rstrip("\n")))
    else:
        brightAsteroidsMPCNames.append(get_MPC_format_name_for_numbered_asteroids(lines[l].rstrip("\n")))

## output to each directory
for n in range(Ndata):
    outputFile = open(directoryNames[n]+"/bright_asteroid_MPC_names_in_the_field.txt","w",newline="\n")
    for l in range(len(brightAsteroidsMPCNames)):
        outputFile.write(brightAsteroidsMPCNames[l]+"\n")
    outputFile.close()
#-------------------------------------------------------------------------------------------

#---make name conversion list of all known asteroids in the field in each directory---------
## subtract number and name from numbered and karifugo asteroids
subprocess.run("awk -F' ' '$2 ~ /^[1-9]/ && $3 ~ /^[A-Z]/ && $3 !~ /[A-Z][A-Z][0-9]*/ && $3 != 'P-L' && $3 != 'T-1' && $3 != 'T-2' && $3 != 'T-3' {print $2,$3}' cand2b.txt > candNameList_numbered_named.txt",shell=True)
subprocess.run("awk -F' ' '$2 ~ /^[1-9]/ && $3 ~ /^[1-2]/ || $4 == 'P-L' || $4 == 'T-1' || $4 == 'T-2' || $4 == 'T-3' {print $2,$3,$4}' cand2b.txt > candNameList_numbered_unnamed.txt",shell=True)
subprocess.run("awk -F' ' '$2 ~ /^[1-2]/ && $3 ~ /[A-Z][A-Z][0-9]*/ || $3 == 'P-L' || $3 == 'T-1' || $3 == 'T-2' || $3 == 'T-3' {print $2,$3}' cand2b.txt > candNameList_karifugo.txt",shell=True)

## for numbered and named asteroids
numberedNamedFullName = np.loadtxt("candNameList_numbered_named.txt",dtype='str')
numberedNamedShortName = []
numberedNamedMPCName = []
for l in range(len(numberedNamedFullName)):
    numberedNamedShortName.append(numberedNamedFullName[l][0])
    numberedNamedMPCName.append(get_MPC_format_name_for_numbered_asteroids(numberedNamedFullName[l][0]))

## for numbered and unnamed asteroids
numberedUnnamedFullName = np.loadtxt("candNameList_numbered_unnamed.txt",dtype='str')
numberedUnnamedShortName = []
numberedUnnamedMPCName = []
for l in range(len(numberedUnnamedFullName)):
    numberedUnnamedShortName.append(numberedUnnamedFullName[l][0])
    numberedUnnamedMPCName.append(get_MPC_format_name_for_numbered_asteroids(numberedUnnamedFullName[l][0]))

## for karifugo asteroids
karifugoFullName = np.loadtxt("candNameList_karifugo.txt",dtype='str')
karifugoShortName = []
karifugoMPCName = []
for l in range(len(karifugoFullName)):
    karifugoShortName.append(karifugoFullName[l][0]+karifugoFullName[l][1])
    karifugoMPCName.append(get_MPC_format_name_for_karifugo_asteroids(karifugoShortName[l]))

## output to each directory
for n in range(Ndata):
    outputFile = open(directoryNames[n]+"/name_conversion_list_in_the_field.txt","w",newline="\n")
    for l in range(len(numberedNamedFullName)):
        outputFile.write(numberedNamedFullName[l][0]+" "+numberedNamedFullName[l][1]+","+numberedNamedShortName[l]+","+numberedNamedMPCName[l]+"\n")
    for l in range(len(numberedUnnamedFullName)):
        outputFile.write(numberedUnnamedFullName[l][0]+" "+numberedUnnamedFullName[l][1]+" "+numberedUnnamedFullName[l][2]+","+numberedUnnamedShortName[l]+","+numberedUnnamedMPCName[l]+"\n")
    for l in range(len(karifugoFullName)):
        outputFile.write(karifugoFullName[l][0]+" "+karifugoFullName[l][1]+","+karifugoShortName[l]+","+karifugoMPCName[l]+"\n")
    outputFile.close()
#-------------------------------------------------------------------------------------------
