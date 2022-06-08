#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 26 00:38:58 2020
@author: urakawa
 Time-stamp: <2022/06/8 8:20:00 (JST) sugiura>
"""

import glob
import astropy.stats
import matplotlib.pyplot as plt
import numpy as np
import photutils.datasets
from astropy.io import fits
from astropy.visualization import (ZScaleInterval)
from matplotlib import cm
from PIL import Image
import traceback

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
#--------------------------------------------------------------------------------

try:
    ## warp image list to read ##
    img_list = sorted(glob.glob('warpbin-*.fits'))  # K.S. modify 2021/7/20
    if len(img_list)==0:
        raise FileNotFoundError

    ## make arrays to store output images
    hdutmp = fits.open(img_list[0])
    head_list = []
    scidata = np.empty((len(img_list), np.shape(hdutmp[0].data)[0], np.shape(hdutmp[0].data)[1]))
    maskdata = np.empty((len(img_list), np.shape(hdutmp[0].data)[0], np.shape(hdutmp[0].data)[1]))
    image_sky_nan_mask = np.empty_like(scidata)
    image_sky_nan = np.empty_like(scidata)
    del hdutmp

    ## Loading original fits images
    nanmaskList = []
    for i in range(len(img_list)):
        hdu = fits.open(img_list[i])
        scidata[i] = hdu[0].data

        ## Make sky background image to replace NaN region #####
        # masking NaN
        nanmask = np.isnan(scidata[i])
        nanmaskList.append(nanmask)
        scidata_maskednan = np.ma.array(scidata[i], mask=nanmask)

        # sigma-clipping and measuring statistics to make sky
        rejection = 3.0  # threshold sigma value of sky 
        sky_mean, sky_median, sky_stddev = astropy.stats.sigma_clipped_stats(scidata_maskednan, sigma=rejection)

        # make sky background image
        image_sky = photutils.datasets.make_noise_image((np.shape(scidata[i])), distribution='gaussian', mean=sky_mean, stddev=sky_stddev)

        # replace nan -> sky background
        scidata[i][nanmask] = 0  # replace nan =>0 temporaly
        ###########################################################

        ## Mask image of HSC
        maskdata[i] = hdu[1].data
        # maskdatalist.append ( maskdata[i] )

        ## make header with wcs info
        head_list.append(hdu[0].header)

    ## make mask images ##
    ## median for mask
    stacked_maskdata = np.stack(maskdata)
    median_maskdata = np.median(stacked_maskdata, axis=0)

    ## hanten 
    tmp_hanten = np.where(median_maskdata == 0, 1, median_maskdata)
    hanten_image = np.where(tmp_hanten > 1, 0, tmp_hanten)

    ## make sky masked (K.S. 2022/5/20) ###
    for i in range(len(img_list)):
        image_sky_nan_mask[i]  = np.where( (nanmaskList[i]) | (hanten_image == 0), image_sky, 0)
        image_sky_nan[i]  = np.where(nanmaskList[i], image_sky, 0)
    #######################################

    ## masking and output to fits images ##
    for i in range(len(img_list)):
        ## masked scidata 
        ## masking : image * hanten median
        output_scidata_masked = scidata[i] * hanten_image + image_sky_nan_mask[i]
        hdunew = fits.PrimaryHDU(output_scidata_masked, head_list[i])
        ## output 
        fitsname = 'warp%s_bin' % str(i + 1)
        pngname = '%s_disp-coias' % str(i + 1)  # NM added 2021-08-10
        hdunew.writeto(fitsname + ".fits", overwrite=True)  # output as fits image
        fits2png(output_scidata_masked, pngname + ".png")  # output as png image

        ## non-masked scidata
        ## masking : image * hanten median
        output_scidata = scidata[i] + image_sky_nan[i]
        # hdunew = fits.PrimaryHDU( output_scidata, head_list[i] )  ## comment-out: non-mask image is not needed to fits format
        ## output 
        pngname = '%s_disp-coias_nonmask' % str(i + 1)  # NM added 2021-08-10
        # hdunew.writeto( outfilename+".fits", overwrite = True) # output as fits image ## comment-out:non-mask image is not needed to fits format
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
