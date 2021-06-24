#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 26 00:38:58 2020

@author: urakawa
"""

import numpy as np
import pylab
import matplotlib.pyplot as plt
from astropy.visualization import astropy_mpl_style
from astropy.wcs import WCS
from astropy.io import fits
from astropy.visualization import (ZScaleInterval,ImageNormalize)
from astropy.time import Time
import glob
import os
import subprocess

img_list0 = sorted(glob.glob('warp-*bin.fits'))
img_list = img_list0
#open warp image

hdu1 = fits.open(img_list[0])
scidata1 = hdu1[0].data
#replace nan =>0
scidata1[np.isnan(scidata1)]=0
#b is mask image
scidata1b = hdu1[1].data


#make header with wcs info
h1head = hdu1[0].header      


hdu2 = fits.open(img_list[1])
scidata2 = hdu2[0].data
scidata2[np.isnan(scidata2)]=0
scidata2b = hdu2[1].data

h2head = hdu2[0].header     
#wcs2 = WCS(hdu2[1].header).celestial

hdu3 = fits.open(img_list[2])
scidata3 = hdu3[0].data
scidata3[np.isnan(scidata3)]=0
scidata3b = hdu3[1].data


h3head = hdu3[0].header  

hdu4 = fits.open(img_list[3])
scidata4 = hdu4[0].data
scidata4[np.isnan(scidata4)]=0
scidata4b = hdu4[1].data
h4head = hdu4[0].header     

hdu5 = fits.open(img_list[4])
scidata5 = hdu5[0].data
scidata5[np.isnan(scidata5)]=0
scidata5b = hdu5[1].data
h5head = hdu5[0].header     

#median for mask
tmp = np.stack((scidata1b,scidata2b,scidata3b,scidata4b,scidata5b))
tmp2 = np.median(tmp,axis=0)

#hanten 
tmp3 = np.where(tmp2==0,1,tmp2) 
tmp4 = np.where(tmp3>1,0,tmp3)


#image * hanten median
scidata1c = scidata1 * tmp4
hdunew = fits.PrimaryHDU(scidata1c,h1head)
hdunew.writeto('warp1_bin.fits',overwrite = True)

scidata2c = scidata2 * tmp4
hdunew = fits.PrimaryHDU(scidata2c,h2head)
hdunew.writeto('warp2_bin.fits',overwrite = True)

scidata3c = scidata3 * tmp4
hdunew = fits.PrimaryHDU(scidata3c,h3head)
hdunew.writeto('warp3_bin.fits',overwrite = True)

scidata4c = scidata4 * tmp4
hdunew = fits.PrimaryHDU(scidata4c,h4head)
hdunew.writeto('warp4_bin.fits',overwrite = True)

scidata5c = scidata5 * tmp4
hdunew = fits.PrimaryHDU(scidata5c,h5head)
hdunew.writeto('warp5_bin.fits',overwrite = True)




