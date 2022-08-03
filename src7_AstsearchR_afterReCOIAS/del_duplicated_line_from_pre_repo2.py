#!/usr/bin/env python3
# -*- coding: UTF-8 -*
#timestamp: 2022/8/3 13:30 sugiura
import traceback
import os
import shutil
import glob
from astropy.io import fits
from astropy.time import Time

class NothingToDo(Exception):
    pass

def extract_jd_ra_dec_info_from_MPC_line(MPCOneLine):
    jdStr = MPCOneLine[15:31]

    raHour = float(MPCOneLine.split()[4])
    raMin  = float(MPCOneLine.split()[5])
    raSec  = float(MPCOneLine.split()[6])
    raArcSec = (360.0/24.0) * (raHour * 60 * 60 + raMin * 60 + raSec)

    decDegree = float(MPCOneLine.split()[7])
    if decDegree<0.0: sign=-1.0
    else:             sign= 1.0
    decMin = sign*float(MPCOneLine.split()[8])
    decSec = sign*float(MPCOneLine.split()[9])
    decArcSec = decDegree * 60 * 60 + decMin * 60 + decSec

    return {"jdStr":jdStr, "raArcSec":raArcSec, "decArcSec":decArcSec}

try:
    #---get yyyy-mm-dd of this measurement--------
    scidata = fits.open("warp01_bin.fits")
    jd = scidata[0].header['JD']
    tInTimeObj = Time(jd, format="jd")
    tInIso = tInTimeObj.iso
    yyyy_mm_dd = tInIso.split()[0]
    #---------------------------------------------

    #---check ~/.coias/past_pre_repo_data/yyyy-mm-dd directory exists or not
    dirName = os.path.expanduser("~") + "/.coias/past_pre_repo_data/" + yyyy_mm_dd
    if not os.path.isdir(dirName):
        shutil.copy("pre_repo2.txt","pre_repo3.txt")
        raise NothingToDo
    #-----------------------------------------------------------------------

    #---remove duplicate--------------------------
    preRepoInputFile = open("pre_repo2.txt","r")
    inputLines = preRepoInputFile.readlines()
    preRepoInputFile.close()

    currentDir = os.getcwd()
    compareFileNames = sorted(glob.glob(os.path.expanduser("~") + "/.coias/past_pre_repo_data/" + yyyy_mm_dd + "/pre_repo3_*.txt"))
    for l in reversed(range(len(inputLines))):
        inputLine = inputLines[l]
        inputLineInfo = extract_jd_ra_dec_info_from_MPC_line(inputLine)
        duplicateFlag = False
        
        for fileName in compareFileNames:
            compareFile = open(fileName,"r")
            compareLines = compareFile.readlines()
            compareFile.close()

            if compareLines[0].rstrip("\n")==currentDir:
                ### we skip the data produced from the same working directory
                continue
                
            for lc in range(1, len(compareLines)):
                compareLineInfo = extract_jd_ra_dec_info_from_MPC_line(compareLines[lc])
                ### compare compareLine and inputLine
                ### if jd exactly match, differences of ra and dec are smaller than 1 arcsec
                ### we delete the line and do not output it
                raDiff = abs(inputLineInfo["raArcSec"] - compareLineInfo["raArcSec"])
                decDiff = abs(inputLineInfo["decArcSec"] - compareLineInfo["decArcSec"])
                if inputLineInfo["jdStr"]==compareLineInfo["jdStr"] and raDiff<1.0 and decDiff<1.0:
                    del inputLines[l]
                    duplicateFlag = True
                    break

            if duplicateFlag:
                break
    #---------------------------------------------

    #---output------------------------------------
    preRepoOutputFile = open("pre_repo3.txt","w",newline="\n")
    preRepoOutputFile.writelines(inputLines)
    preRepoOutputFile.close()
    #---------------------------------------------


except NothingToDo:
    error = 0
    errorReason = 74
    
except FileNotFoundError:
    print("Some previous files are not found in del_duplicated_line_from_pre_repo2.py!")
    print(traceback.format_exc())
    error = 1
    errorReason = 74

except Exception:
    print("Some errors occur in del_duplicated_line_from_pre_repo2.py!")
    print(traceback.format_exc())
    error = 1
    errorReason = 75

else:
    error = 0
    errorReason = 74

finally:
    errorFile = open("error.txt","a")
    errorFile.write("{0:d} {1:d} 711 \n".format(error,errorReason))
    errorFile.close()
