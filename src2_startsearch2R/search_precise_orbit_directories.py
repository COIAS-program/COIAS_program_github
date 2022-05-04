#!/usr/bin/env python3
# -*- coding: UTF-8 -*
import os
import sys
import glob
import time
import shutil
from astropy.io import fits

#---variables--------------------------------
Ndata = 5
presentTimeStamp = time.time()
isCorrectDirectory = [0] * Ndata
directoryNames = ['a'] * Ndata
filesInOrbitDataDir = glob.glob(os.path.expanduser("~")+"/.coias/orbit_data/*")
preciseOrbitFleshTime = 60*60*24*14
#--------------------------------------------

#---read ra dec jd of warp files-------------
raList = []
decList = []
jdList = []
for i in range(Ndata):
    dataFileName = "warp{0:d}_bin.fits".format(i+1)
    scidata = fits.open(dataFileName)
    raList.append(scidata[0].header['CRVAL1'])
    decList.append(scidata[0].header['CRVAL2'])
    jdList.append(scidata[0].header['JD'])
#--------------------------------------------

#---read ~/.coias/orbit_data/log.txt---------
logFileName = os.path.expanduser("~")+"/.coias/orbit_data/log.txt"
logFile = open(logFileName,"r")
line = logFile.readline()
maxNumOrbitDirectories = int(line.rstrip("\n"))
logFile.close()
#--------------------------------------------

#---check presice orbit directory exists or not-
for fileName in filesInOrbitDataDir:
    if os.path.isdir(fileName):
        try:
            raDecJdTimeFile = open(fileName+"/ra_dec_jd_time.txt","r")
        except FileNotFoundError:
            print("The directory "+fileName+" does not have ra_dec_jd_time.txt")
            print("Remove the directory.")
            shutil.rmtree(fileName)
        else:
            line = raDecJdTimeFile.readline()
            content = line.split()
            ra = float(content[0])
            dec = float(content[1])
            jd = float(content[2])
            fileTime = float(content[3])
            raDecJdTimeFile.close()

            for i in range(Ndata):
                if abs(ra-raList[i])<0.01 and abs(dec-decList[i])<0.01 and abs(jd-jdList[i])<0.00001 and abs(fileTime-presentTimeStamp)<preciseOrbitFleshTime:
                    #known objects in this file were already searched recently
                    isCorrectDirectory[i] = 1
                    directoryNames[i] = fileName
                elif abs(ra-raList[i])<0.01 and abs(dec-decList[i])<0.01 and abs(jd-jdList[i])<0.00001 and abs(fileTime-presentTimeStamp)>preciseOrbitFleshTime:
                    #known objects in this file were searched but long ago
                    isCorrectDirectory[i] = 0
                    directoryNames[i] = fileName
#-----------------------------------------------

#---if presice orbit directory does not exist, make it-
for i in range(Ndata):
    if isCorrectDirectory[i]==0 and directoryNames[i]=='a':
        directory = os.path.expanduser("~")+"/.coias/orbit_data/{0:d}".format(maxNumOrbitDirectories)
        os.mkdir(directory)
        isCorrectDirectory[i] = 0
        directoryNames[i] = directory
        maxNumOrbitDirectories += 1
logFile = open(logFileName,"w",newline="\n")
logFile.write(str(maxNumOrbitDirectories))
logFile.close()
#------------------------------------------------------

#---output precise orbit directory information to current directory-
preciseOrbitDirectoryFile = open("precise_orbit_directories.txt","w",newline="\n")
haveAllPreciseOrbit = 1
for i in range(Ndata):
    preciseOrbitDirectoryFile.write(directoryNames[i]+" {0:d}\n".format(isCorrectDirectory[i]))
    if isCorrectDirectory[i]==0:
        haveAllPreciseOrbit = 0
preciseOrbitDirectoryFile.close()

haveAllPreciseOrbitFile = open("have_all_precise_orbits.txt","w",newline="\n")
haveAllPreciseOrbitFile.write(str(haveAllPreciseOrbit))
haveAllPreciseOrbitFile.close()
#-------------------------------------------------------------------
