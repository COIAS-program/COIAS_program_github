#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#Timestamp: 2022/08/19 8:30 sugiura
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
# 入力: カレントディレクトリに存在する全てのビニング済み画像データ
# 　　  warpbin-HSC-[filter]-[tract]-[patch],[patch]-[visit].fits
# 出力: マスク済み画像データ  warp[1から連番の画像番号]_bin.fits
# 　　  マスク済みpngファイル [1から連番の画像番号]_disp-coias.png
# 　　  マスクなしpngファイル [1から連番の画像番号]_disp-coias_nonmask.png
##########################################################
import glob
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

        ## non-masked scidata
        ## masking : image * hanten median
        output_scidata = scidata + image_sky_nan
        ## output 
        pngname = '{0:02d}_disp-coias_nonmask'.format(i + 1)  # NM added 2021-08-10
        fits2png(output_scidata, pngname + ".png")  # output as png image

except FileNotFoundError:
    print("Some previous files are not found in subm2.py!")
    print(traceback.format_exc())
    error = 1
    errorReason = 24

except Exception:
    print("Some errors occur in subm2.py!")
    print(traceback.format_exc())
    error = 1
    errorReason = 25

else:
    error = 0
    errorReason = 24

finally:
    errorFile = open("error.txt","a")
    errorFile.write("{0:d} {1:d} 203 \n".format(error,errorReason))
    errorFile.close()
