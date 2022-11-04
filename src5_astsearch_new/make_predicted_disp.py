#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# timestamp: 2022/08/28 15:30 sugiura
###################################################################################
# 過去に測定したデータのうち, 今回の測定の観測日から2日以内のデータを用いて,
# それら過去のデータで検出された新天体が今回の観測画像のどこにいるか予測して座標を書き出す.
# 同じ観測日から予測することもあり得る. またその予測が過去にすでに測定された時刻になされるなら,
# それは予測ではなく「すでに観測した」ということを示すことに使える. その区別もつける.
#
# 入力: ~/.coias/past_pre_repo_data/以下の今回の測定の観測日から2日以内の
# 　　  coefficients_for_predict.txt
# 出力: predicted_disp.txt
# 　　    書式: 新天体名 画像番号 Xpixel Ypixel 0or1(予測なら0, 既観測なら1)
###################################################################################
import sys
import traceback
import os
import glob
from astropy.io import fits
from astropy.wcs import wcs
from astropy.time import Time
from def_coias_data_path import *

try:
    ### suppress warnings #########################################################
    if not sys.warnoptions:
        import warnings
        warnings.simplefilter("ignore")
    
    #---get coefficient file name list----------------------------------------------
    scidata = fits.open("warp01_bin.fits")
    jd0  = scidata[0].header['JD']
    jdDiffList = [0.0, -1.0, 1.0, -2.0, 2.0]
    coefFileNameList = []
    for jdDiff in jdDiffList:
        jd = jd0 + jdDiff
        tInTimeObj = Time(jd, format="jd")
        tInIso = tInTimeObj.iso
        yyyy_mm_dd = tInIso.split()[0]

        coefFileNameList.append( coiasDataPath + "/past_pre_repo_data/" + yyyy_mm_dd + "/coefficients_for_predict.txt")
    #------------------------------------------------------------------------------

    #---get jd list of warp files--------------------------------------------------
    warpFileNameList = sorted(glob.glob("warp*_bin.fits"))
    warpJdList = []
    warpJdStrList = []
    for fileName in warpFileNameList:
        scidata = fits.open(fileName)
        jd = scidata[0].header["JD"]
        warpJdList.append(jd)
        warpJdStrList.append("{0:.4f}".format(jd))
    #------------------------------------------------------------------------------

    #---get range of pixels of png files and set wcs-------------------------------
    scidata = fits.open("warp01_bin.fits")
    XPixelMax = scidata[0].header["NAXIS1"]
    YPixelMax = scidata[0].header["NAXIS2"]

    wcs0 = wcs.WCS(scidata[0].header)
    #------------------------------------------------------------------------------

    #---output---------------------------------------------------------------------
    outputFile = open("predicted_disp.txt", "w", newline="\n")
    outputObjNameList = []
    for coefFileName in coefFileNameList:
        if os.path.isfile(coefFileName):
            f = open(coefFileName, "r")
            coefDataLines = f.readlines()
            f.close()

            for coefLine in coefDataLines:
                contents = coefLine.split()
                if contents[0] not in outputObjNameList:
                    outputObjNameList.append(contents[0])

                    for image in range(len(warpJdList)):
                        raPre  = float(contents[1]) * warpJdList[image] + float(contents[2])
                        decPre = float(contents[3]) * warpJdList[image] + float(contents[4])
                        obsJdStrList = contents[5:len(contents)]
                        xypix = wcs0.wcs_world2pix(raPre, decPre, 1)
                        if xypix[0]>0 and xypix[1]>0 and xypix[0]<XPixelMax and xypix[1]<YPixelMax:
                            if warpJdStrList[image] in obsJdStrList:
                                isMeasured = 1
                            else:
                                isMeasured = 0

                            outputFile.write(contents[0] + " " + "{0:d}".format(image) + " " + "{0:.2f}".format(xypix[0]) + " " + "{0:.2f}".format(xypix[1]) + " " + "{0:d}".format(isMeasured) + "\n")

    outputFile.close()
    #------------------------------------------------------------------------------


except FileNotFoundError:
    print("Some previous files are not found in change_data_to_mpc_format.py!")
    print(traceback.format_exc())
    error = 1
    errorReason = 54

except Exception:
    print("Some errors occur in change_data_to_mpc_format.py!")
    print(traceback.format_exc())
    error = 1
    errorReason = 55

else:
    error = 0
    errorReason = 54

finally:
    errorFile = open("error.txt","a")
    errorFile.write("{0:d} {1:d} 517 \n".format(error,errorReason))
    errorFile.close()
