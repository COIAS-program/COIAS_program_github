#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#Timestamp: 2022/12/24 14:00 sugiura
##########################################################
# 元画像のビニング・0フラックスでの等級・ヘッダの移し替えを行う.
# (元画像が小惑星検出にはオーバースペックなため容量を減らす)
# ビニングは2x2か4x4のどちらかから選べる.
#
# webCOIASの場合は selected_warp_files.txt に記載のwarpファイルを
# サーバ内のその場所に保存してあるので, コピーしてカレントに置く.
# その際すでにビニングしてあるファイル(warpbin2-*.fits or warpbin4-*.fits)
# がサーバ内の同じディレクトリにあった場合, それをwarpbin-*.fitsとしてカレントにコピーする.
# (ビニング後のファイルがサーバにある場合, ビニング前のファイルはカレントにはコピーしない)
#
# 入力: カレントディレクトリに存在する全ての元画像ファイル (オリジナル・デスクトップCOIASの場合)
#       warp-HSC-[filter]-[tract]-[patch],[patch]-[visit].fits
# 　　  selected_warp_files.txt (webCOIASの場合)
# 出力: 元画像ファイルをビニング・ヘッダ書き換えをした画像ファイル
#       warpbin-HSC-[filter]-[tract]-[patch],[patch]-[visit].fits
##########################################################
import glob
import sys
import os
import shutil
import traceback

import numpy as np
from astropy.io import fits
from astropy.time import Time
import visitsort
import print_progress
import print_detailed_log
import PARAM

try:
    ## mode selection ####
    mode = input("Please choose binning mode.\n (2: 2x2 binning, 4: 4x4 binning):")
    if mode == "2":
        print("2x2 binning mode.")
        nbin = 2
    elif mode == "4":
        print("4x4 binning mode.")
        nbin = 4
    else:
        print("ERROR: invarid binning mode. Please input 2 or 4.")
        sys.exit()
    ########################

    #---search fits files---------------------------------------------------------------
    ### for webCOIAS
    if PARAM.IS_WEB_COIAS:
        if not os.path.isfile("selected_warp_files.txt"):
            raise FileNotFoundError("selected_warp_files.txt is not found.")
        f = open("selected_warp_files.txt","r")
        lines = f.readlines()
        f.close()

        if lines[0].startswith("data"):
            dirs = lines[0].split("/")
            dirs.pop(-1)
            ### absolute path for the directory storing images
            thisDataDir = PARAM.WARP_DATA_PATH + "/".join(dirs) + "/"
        else:
            raise Exception(f"Invalid initial line in selected_warp_files.txt. lines[0]={lines[0]}")

        img_list = []
        for line in lines:
            if line.startswith("data"):
                img_list.append(line.split("/").pop(-1).rstrip("\n"))
        img_list = sorted(img_list, key=visitsort.key_func_for_visit_sort)

    ### for original or desktop COIAS
    else:
        img_list = sorted(glob.glob('warp-*.fits'), key=visitsort.key_func_for_visit_sort)
        
    if len(img_list)==0:
        raise FileNotFoundError("Original warp files are not found.")
    #-----------------------------------------------------------------------------------

    #---binning-------------------------------------------------------------------------
    nLoopDone = 0
    needBinning = True
    for i in img_list:
        if PARAM.IS_WEB_COIAS:
            ### check binned fits file exists in the thisDataDir
            imageNameFlagmentList = i.split("-")
            imageNameFlagmentList[0] = f"warpbin{nbin}"
            binnedImageNameWithFullPath = thisDataDir + "-".join(imageNameFlagmentList)

            imageNameFlagmentList[0] = "warpbin"
            binnedImageNameInCurrentDir = "-".join(imageNameFlagmentList)
            ### if exists, copy the binned image to current directory as warpbin-*.fits
            if os.path.isfile(binnedImageNameWithFullPath):
                shutil.copyfile(binnedImageNameWithFullPath, binnedImageNameInCurrentDir)
                needBinning = False
            ### if not exist, copy the original image to current directory
            else:
                originalImageNameWithFullPath = thisDataDir + i
                if not os.path.isfile(originalImageNameWithFullPath):
                    raise FileNotFoundError(f"Original image {originalImageNameWithFullPath} is not found in the server.")
                shutil.copyfile(originalImageNameWithFullPath, i)
                needBinning = True
            
        if not PARAM.IS_WEB_COIAS or needBinning:
            print_progress.print_progress(nCheckPointsForLoop=4, nForLoop=len(img_list), currentForLoop=nLoopDone)
        
            hdu1 = fits.open(i)
            xpix = hdu1[1].header['NAXIS1']
            ypix = hdu1[1].header['NAXIS2']
            scidata = hdu1[1].data  # science-image
            maskdata = hdu1[2].data  # mask-image

            # bining
            # mean(?) ? is axis number.-1 means horizontal. 1 means vertical.
            scidata_bin = scidata.reshape(int(ypix / nbin), nbin, int(xpix / nbin), nbin).mean(-1).mean(1)
            maskdata_bin = maskdata.reshape(int(ypix / nbin), nbin, int(xpix / nbin), nbin).mean(-1).mean(1)
            maskdata_bin = np.array(maskdata_bin, dtype="int16")

            # make header
            # obs time
            # S.U edit
            # Even if images are processed by hscpipe-8, Fluxmag0 can be calculated.
            # S.U modify 2021/10/28 Correspondence both fits header keyword 'TIME-MID' and 'DATE-AVG')
            if 'TIME-MID' in hdu1[0].header:
                t1 = Time(hdu1[0].header['TIME-MID'], format='isot', scale='utc')
            else:
                t1 = Time(hdu1[0].header['DATE-AVG'], format='isot', scale='utc')
            hdu1[0].header['JD'] = t1.jd

            ## Check existence of 'FLUXMAG0' in the header. (2021.12.24 NM)
            try:
                FLUXMAG0 = hdu1[0].header['FLUXMAG0']
            except KeyError as e:  ## if header 'FLUXMAG0' does not exist
                # FLUXMAG0ERR is 10^{-4} mag. Negligible"
                entryHduIndex = hdu1[0].header["AR_HDU"] - 1
                entryHdu = hdu1[entryHduIndex]
                photoCalibId = hdu1[0].header["PHOTOCALIB_ID"]
                photoCalibEntry, = entryHdu.data[entryHdu.data["id"] == photoCalibId]
                photoCalibHdu = hdu1[entryHduIndex + photoCalibEntry["cat.archive"]]
                start = photoCalibEntry["row0"]
                end = start + photoCalibEntry["nrows"]
                photoCalib, = photoCalibHdu.data[start:end]
                calibrationMean = photoCalib["calibrationMean"]
                calibrationErr = photoCalib["calibrationErr"]
                FLUXMAG0 = (1.0e+23 * 10 ** (48.6 / (-2.5)) * 1.0e+9) / calibrationMean
                fluxmag0err = (1.0e+23 * 10 ** (48.6 / (-2.5)) * 1.0e+9) / calibrationMean ** 2 * calibrationErr,

            zerop1 = 2.5 * np.log10(FLUXMAG0)

            hdu1[0].header['Z_P'] = zerop1
            # hdu1[0].header['EQUINOX'] = hdu1[1].header['EQUINOX']
            hdu1[0].header['RADESYS'] = hdu1[1].header['RADESYS']
            hdu1[0].header['CRPIX1'] = hdu1[1].header['CRPIX1'] / nbin
            hdu1[0].header['CRPIX2'] = hdu1[1].header['CRPIX2'] / nbin
            hdu1[0].header['CD1_1'] = hdu1[1].header['CD1_1'] * nbin
            # hdu1[0].header['CD1_2'] =  hdu1[1].header['CD1_2']
            # hdu1[0].header['CD2_1'] =  hdu1[1].header['CD2_1']
            hdu1[0].header['CD2_2'] = hdu1[1].header['CD2_2'] * nbin
            hdu1[0].header['CRVAL1'] = hdu1[1].header['CRVAL1']
            hdu1[0].header['CRVAL2'] = hdu1[1].header['CRVAL2']
            # hdu1[0].header['CUNIT1'] = hdu1[1].header['CUNIT1']
            # hdu1[0].header['CUNIT2'] = hdu1[1].header['CUNIT2']
            hdu1[0].header['CTYPE1'] = hdu1[1].header['CTYPE1']
            hdu1[0].header['CTYPE2'] = hdu1[1].header['CTYPE2']
            hdu1[0].header['LTV1'] = hdu1[1].header['LTV1']
            hdu1[0].header['LTV2'] = hdu1[1].header['LTV2']
            hdu1[0].header['INHERIT'] = hdu1[1].header['INHERIT']
            hdu1[0].header['EXTTYPE'] = hdu1[1].header['EXTTYPE']
            # hdu1[0].header['EXTNAME'] = hdu1[1].header['EXTNAME']
            hdu1[0].header['CRVAL1A'] = hdu1[1].header['CRVAL1A']
            hdu1[0].header['CRVAL2A'] = hdu1[1].header['CRVAL2A']
            hdu1[0].header['CRPIX1A'] = hdu1[1].header['CRPIX1A']
            hdu1[0].header['CRPIX2A'] = hdu1[1].header['CRPIX2A']
            hdu1[0].header['CTYPE1A'] = hdu1[1].header['CTYPE1A']
            hdu1[0].header['CTYPE2A'] = hdu1[1].header['CTYPE2A']
            hdu1[0].header['CUNIT1A'] = hdu1[1].header['CUNIT1A']
            hdu1[0].header['CUNIT2A'] = hdu1[1].header['CUNIT2A']
            hdu1[0].header['NBIN'] = nbin #K.S. added 2022/5/3

            # h1head = hdu1[0].header + hdu1[1].header
            h1head = hdu1[0].header
            hdunew = fits.PrimaryHDU(scidata_bin, h1head)
            hdunew2 = fits.ImageHDU(maskdata_bin, h1head)
            hdul = fits.HDUList([hdunew, hdunew2])
            hdul.writeto(i.replace('warp-', 'warpbin-'), overwrite=True)  # S.U modify 2021/12/9

            nLoopDone += 1
    #-----------------------------------------------------------------------------------

except FileNotFoundError:
    print("Some necessary files do not exist in binning.py! Please upload these files.",flush=True)
    print(traceback.format_exc(),flush=True)
    error = 1
    errorReason = 21

except Exception:
    print("Some errors occur in binning.py!",flush=True)
    print(traceback.format_exc(),flush=True)
    error = 1
    errorReason = 25

else:
    error = 0
    errorReason = 21

finally:
    errorFile = open("error.txt","a")
    errorFile.write("{0:d} {1:d} 202 \n".format(error,errorReason))
    errorFile.close()

    if error==1:
        print_detailed_log.print_detailed_log(dict(globals()))
