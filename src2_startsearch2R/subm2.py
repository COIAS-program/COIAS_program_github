#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#Timestamp: 2022/12/24 15:30 sugiura
##########################################################
# ビニングされた画像データにマスク処理を施す.
# 元画像のHDUList型データにはリストの2番目の要素(hdu[1])として
# XPIXELxYPIXELの0~255の整数配列のマスク用データが存在する.
# (0は暗く, 大きいほど明るい)
# 各ピクセルのマスク用データの中央値が0でなければずっと明るい,
# すなわち星であると見做して, そのようなピクセルにはマスク処理を施す.
# また, 元画像がNaNである領域とマスクした領域を単に0にすると
# 目に悪いpng画像ができたりするので, スカイで埋めることにしている.
# 表示用のpng画像生成もこのスクリプトで行う.
#
# webCOIASでは, カレントディレクトリに存在する全てのビング済み画像データに対応する
# マスク済み画像データ・マスク済みpngファイル・マスクなしpngファイルが
# selected_warp_files.txtに記載の画像データを保存しているディレクトリに存在しているか見に行く.
# もし全て存在しているならば, 単にそれらをカレントディレクトリに下記出力の名前でコピーする.
#
# 入力: カレントディレクトリに存在する全てのビニング済み画像データ
# 　　  warpbin-HSC-[filter]-[tract]-[patch],[patch]-[visit].fits
# 　　  selected_warp_files.txt (webCOIASの場合)
# 出力: マスク済み画像データ  warp[1から連番の画像番号]_bin.fits
# 　　  マスク済みpngファイル [1から連番の画像番号]_disp-coias.png
# 　　  マスクなしpngファイル [1から連番の画像番号]_disp-coias_nonmask.png
##########################################################
import glob
import re
import os
import shutil
import astropy.stats
import matplotlib.pyplot as plt
import numpy as np
import photutils.datasets
from astropy.io import fits
from astropy.visualization import (ZScaleInterval)
from matplotlib import cm
from PIL import Image
import subprocess
import traceback
import visitsort
import print_progress
import print_detailed_log
import PARAM

#---function---------------------------------------------------------------------
def fits2png(hdu, pngname):
    tmpPngName = "temp.png"
    
    cmap = cm.gray
    vmin, vmax = ZScaleInterval().get_limits(hdu)
    plt.imsave(tmpPngName, hdu, vmin=vmin, vmax=vmax, cmap=cmap, origin="lower")
    plt.close()

    #convert to PNG-8 to reduce png file size
    im = Image.open(tmpPngName)
    im_p = im.convert("P")
    im_p.save(pngname)

    subprocess.run("rm temp.png", shell=True)
#--------------------------------------------------------------------------------

try:
    ## warp image list to read ##
    img_list = sorted(glob.glob('warpbin-*.fits'), key=visitsort.key_func_for_visit_sort)  # K.S. modify 2021/7/20
    if len(img_list)==0:
        raise FileNotFoundError

    ## check all masked-binned warp files, masked png files, and nonmasked png files corresponding to img_list exist in the server
    if not PARAM.IS_WEB_COIAS:
        needMask = True
    else:
        needMask = False
        #---get nbin-------------------------------
        hdu = fits.open(img_list[0])
        nbin = hdu[0].header['NBIN']
        hdu.close()
        #------------------------------------------
        
        #---get the directory name for images------
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
        #------------------------------------------

        #---check----------------------------------
        maskedWarpFileNameWithFullPath   = []
        maskedPngFileNameWithFullPath    = []
        nonMaskedPngFileNameWithFullPath = []
        for img_name in img_list:
            fileNameFlagmentList = re.split('[-.]',img_name)
            fileNameFlagmentList.pop(-1)
            fileNameFlagmentList[0] = f"warpmaskbin{nbin}"
            thisMaskedWarpFileNameWithFullPath = thisDataDir + "-".join(fileNameFlagmentList) + ".fits"
            maskedWarpFileNameWithFullPath.append( thisMaskedWarpFileNameWithFullPath )

            fileNameFlagmentList[0] = f"maskbin{nbin}"
            thisMaskedPngFileNameWithFullPath = thisDataDir + "-".join(fileNameFlagmentList) + ".png"
            maskedPngFileNameWithFullPath.append( thisMaskedPngFileNameWithFullPath )

            fileNameFlagmentList[0] = f"nonmaskbin{nbin}"
            thisNonMaskedPngFileNameWithFullPath = thisDataDir + "-".join(fileNameFlagmentList) + ".png"
            nonMaskedPngFileNameWithFullPath.append( thisNonMaskedPngFileNameWithFullPath )

            if ( not os.path.isfile(thisMaskedWarpFileNameWithFullPath) or
                 not os.path.isfile(thisMaskedPngFileNameWithFullPath)  or
                 not os.path.isfile(thisNonMaskedPngFileNameWithFullPath)):
                needMask = True
        #------------------------------------------

    ## if all necessary files exist in the server, just copy then to the current directory
    if not needMask:
        for i in range(len(img_list)):
            shutil.copyfile(maskedWarpFileNameWithFullPath[i], 'warp{0:02d}_bin'.format(i + 1) + ".fits")
            shutil.copyfile(maskedPngFileNameWithFullPath[i], '{0:02d}_disp-coias'.format(i + 1) + ".png")
            shutil.copyfile(nonMaskedPngFileNameWithFullPath[i], '{0:02d}_disp-coias_nonmask'.format(i + 1) + ".png")

    ## if not exist, we produce then from binned warp files
    else:
        ## produce median mask #######
        maskdata = []
        for i in range(len(img_list)):
            hdu = fits.open(img_list[i])
            maskdata.append(hdu[1].data)
            hdu.close()

        ## median for mask
        median_maskdata = np.median(maskdata, axis=0)

        ## hanten 
        tmp_hanten = np.where(median_maskdata == 0, 1, median_maskdata)
        hanten_image = np.where(tmp_hanten > 1, 0, tmp_hanten)

        ## clear
        del maskdata
        del median_maskdata
        del tmp_hanten
        ##############################

        ## load, masking, and output ##
        for i in range(len(img_list)):
            print_progress.print_progress(nCheckPointsForLoop=5, nForLoop=len(img_list), currentForLoop=i)
        
            ## load
            hdu = fits.open(img_list[i])
            scidata = hdu[0].data
            header = hdu[0].header
            hdu.close()

            ## Make sky background image to replace NaN region #####
            # masking NaN
            nanmask = np.isnan(scidata)
            scidata_maskednan = np.ma.array(scidata, mask=nanmask)

            # sigma-clipping and measuring statistics to make sky
            rejection = 3.0  # threshold sigma value of sky 
            sky_mean, sky_median, sky_stddev = astropy.stats.sigma_clipped_stats(scidata_maskednan, sigma=rejection)

            # make sky background image
            image_sky = photutils.datasets.make_noise_image((np.shape(scidata)), distribution='gaussian', mean=sky_mean, stddev=sky_stddev)

            # replace nan -> sky background
            scidata[nanmask] = 0  # replace nan =>0 temporaly        

            ## make sky masked (K.S. 2022/6/14) 
            image_sky_nan_mask  = np.where( (nanmask) | (hanten_image == 0), image_sky, 0)
            image_sky_nan  = np.where(nanmask, image_sky, 0)

            ## masking and output to fits images ##
            ## masked scidata 
            ## masking : image * hanten median
            output_scidata_masked = scidata * hanten_image + image_sky_nan_mask
            hdunew = fits.PrimaryHDU(output_scidata_masked, header)
            ## output 
            fitsname = 'warp{0:02d}_bin'.format(i + 1)
            pngname = '{0:02d}_disp-coias'.format(i + 1)  # NM added 2021-08-10
            hdunew.writeto(fitsname + ".fits", overwrite=True)  # output as fits image
            fits2png(output_scidata_masked, pngname + ".png")  # output as png image

            print_progress.print_progress(nCheckPointsForLoop=5, nForLoop=len(img_list), currentForLoop=i)

            ## non-masked scidata
            ## masking : image * hanten median
            output_scidata = scidata + image_sky_nan
            ## output 
            pngname = '{0:02d}_disp-coias_nonmask'.format(i + 1)  # NM added 2021-08-10
            fits2png(output_scidata, pngname + ".png")  # output as png image

except FileNotFoundError:
    print("Some previous files are not found in subm2.py!",flush=True)
    print(traceback.format_exc(),flush=True)
    error = 1
    errorReason = 24

except Exception:
    print("Some errors occur in subm2.py!",flush=True)
    print(traceback.format_exc(),flush=True)
    error = 1
    errorReason = 25

else:
    error = 0
    errorReason = 24

finally:
    errorFile = open("error.txt","a")
    errorFile.write("{0:d} {1:d} 203 \n".format(error,errorReason))
    errorFile.close()

    if error==1:
        print_detailed_log.print_detailed_log(dict(globals()))
