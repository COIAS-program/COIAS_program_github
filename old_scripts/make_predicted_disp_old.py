#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# timestamp: 2023/12/29 8:00 sugiura
###################################################################################
# 過去に測定したデータのうち, 今回の測定の観測日から2日以内のデータを用いて,
# それら過去のデータで検出された新天体が今回の観測画像のどこにいるか予測して座標を書き出す.
# 同じ観測日から予測することもあり得る. またその予測が過去にすでに測定された時刻になされるなら,
# それは予測ではなく「すでに観測した」ということを示すことに使える. その区別もつける.
#
# 2023/12/29 UTC => 2023年11月の修正時, coefficients_for_predict.txtファイルは修正していない.
#                   「すでに観測した」という判定は, 今測定している画像のjdがこのファイルに厳密一致で含まれているかどうかで判定するため,
#                   TAI => UTCの変換によりjdがずれるとその判定ができなくなる. (=全て予測になってしまう)
#                   これを避けるため, jdの厳密一致ではなく40秒までの差なら一致していると見做すようにする.
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
import print_detailed_log
import PARAM

# Define thresh jd (40秒に対応する時間をjd単位で設定する)
DUPLICATE_THRESH_JD = 40.0 / (24 * 60 * 60)

# 第一引数のjd(str)が, 第2引数のjd(str)のリストに含まれているかどうかを判定する
# ここで含まれているとは, 差が DUPLICATE_THRESH_JD 以下であることを言う
def isJdIncluded(thisJdStr, compareJdStrList):
    isIncluded = False
    for compareJdStr in compareJdStrList:
        diffJd = abs(float(thisJdStr) - float(compareJdStr))
        if diffJd < DUPLICATE_THRESH_JD:
            isIncluded = True

    return isIncluded

try:
    ### suppress warnings #########################################################
    if not sys.warnoptions:
        import warnings

        warnings.simplefilter("ignore")

    # ---get coefficient file name list----------------------------------------------
    scidata = fits.open("warp01_bin.fits")
    jd0 = scidata[0].header["JD"]
    jdDiffList = [0.0, -1.0, 1.0, -2.0, 2.0]
    coefFileNameList = []
    for jdDiff in jdDiffList:
        jd = jd0 + jdDiff
        tInTimeObj = Time(jd, format="jd")
        tInIso = tInTimeObj.iso
        yyyy_mm_dd = tInIso.split()[0]

        coefFileNameList.append(
            PARAM.COIAS_DATA_PATH
            + "/past_pre_repo_data/"
            + yyyy_mm_dd
            + "/coefficients_for_predict.txt"
        )
    # ------------------------------------------------------------------------------

    # ---get jd list of warp files--------------------------------------------------
    warpFileNameList = sorted(glob.glob("warp*_bin.fits"))
    warpJdList = []
    warpJdStrList = []
    for fileName in warpFileNameList:
        scidata = fits.open(fileName)
        jd = scidata[0].header["JD"]
        warpJdList.append(jd)
        warpJdStrList.append("{0:.4f}".format(jd))
    # ------------------------------------------------------------------------------

    # ---get range of pixels of png files and set wcs-------------------------------
    scidata = fits.open("warp01_bin.fits")
    XPixelMax = scidata[0].header["NAXIS1"]
    YPixelMax = scidata[0].header["NAXIS2"]

    wcs0 = wcs.WCS(scidata[0].header)
    # ------------------------------------------------------------------------------

    # ---output---------------------------------------------------------------------
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
                        raPre = float(contents[1]) * warpJdList[image] + float(
                            contents[2]
                        )
                        decPre = float(contents[3]) * warpJdList[image] + float(
                            contents[4]
                        )
                        obsJdStrList = contents[5 : len(contents)]
                        xypix = wcs0.wcs_world2pix(raPre, decPre, 0)
                        if (
                            xypix[0] > 0
                            and xypix[1] > 0
                            and xypix[0] < XPixelMax
                            and xypix[1] < YPixelMax
                        ):
                            if isJdIncluded(warpJdStrList[image], obsJdStrList):
                                isMeasured = 1
                            else:
                                isMeasured = 0

                            outputFile.write(
                                contents[0]
                                + " "
                                + "{0:d}".format(image)
                                + " "
                                + "{0:.2f}".format(xypix[0])
                                + " "
                                + "{0:.2f}".format(xypix[1])
                                + " "
                                + "{0:d}".format(isMeasured)
                                + "\n"
                            )

    outputFile.close()
    # ------------------------------------------------------------------------------

except FileNotFoundError:
    print("Some previous files are not found in make_predicted_disp.py!", flush=True)
    print(traceback.format_exc(), flush=True)
    error = 1
    errorReason = 54

except Exception:
    print("Some errors occur in make_predicted_disp.py!", flush=True)
    print(traceback.format_exc(), flush=True)
    error = 1
    errorReason = 55

else:
    error = 0
    errorReason = 54

finally:
    errorFile = open("error.txt", "a")
    errorFile.write("{0:d} {1:d} 517 \n".format(error, errorReason))
    errorFile.close()

    if error == 1:
        print_detailed_log.print_detailed_log(dict(globals()))
