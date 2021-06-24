#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import numpy as np
import re
from astropy.io import fits
from astropy.time import Time
import subprocess
import glob

#path_name = subprocess.check_output('pwd')
#file_name = glob.glob('test.fits')
#hdu1 = fits.open("test.fits")
#hdu1 = fits.open(os.path.abspath("test.fits"))
img_list0 = sorted(glob.glob('warp-*.fits'))
#for i in img_list0[1:6]:
for i in img_list0[0:5]:
    hdu1 = fits.open(i)
    xpix = hdu1[1].header['NAXIS1']
    ypix = hdu1[1].header['NAXIS2']
    scidata1 = hdu1[1].data
    scidata2 = hdu1[2].data

#bining
#mean(?) ? is axis number.-1 means horizontal. 1 means vertical.
    scidata1b = scidata1.reshape(int(ypix/2),2,int(xpix/2),2).mean(-1).mean(1)
    scidata2b = scidata2.reshape(int(ypix/2),2,int(xpix/2),2).mean(-1).mean(1)
#make header
#obs time
    t1 = Time(hdu1[0].header['TIME-MID'],format='isot',scale='utc')  
    hdu1[0].header['JD'] = t1.jd
#zero_point = 2.5 *np.log10(Fluxmag0), mag = zero_point - 2.5 * np.log10(flux)
    zerop1 = 2.5 * np.log10(hdu1[0].header['FLUXMAG0'])
    hdu1[0].header['Z_P'] = zerop1
    hdu1[0].header['EQUINOX'] = hdu1[1].header['EQUINOX']
    hdu1[0].header['RADESYS'] = hdu1[1].header['RADESYS']
    hdu1[0].header['CRPIX1'] =  hdu1[1].header['CRPIX1']/2
    hdu1[0].header['CRPIX2'] =  hdu1[1].header['CRPIX2']/2
    hdu1[0].header['CD1_1'] =  hdu1[1].header['CD1_1']*2
    hdu1[0].header['CD1_2'] =  hdu1[1].header['CD1_2']
    hdu1[0].header['CD2_1'] =  hdu1[1].header['CD2_1']
    hdu1[0].header['CD2_2'] =  hdu1[1].header['CD2_2']*2
    hdu1[0].header['CRVAL1'] = hdu1[1].header['CRVAL1']
    hdu1[0].header['CRVAL2'] = hdu1[1].header['CRVAL2']
    hdu1[0].header['CUNIT1'] = hdu1[1].header['CUNIT1']
    hdu1[0].header['CUNIT2'] = hdu1[1].header['CUNIT2']
    hdu1[0].header['CTYPE1'] = hdu1[1].header['CTYPE1']
    hdu1[0].header['CTYPE2'] = hdu1[1].header['CTYPE2']
    hdu1[0].header['LTV1'] = hdu1[1].header['LTV1']
    hdu1[0].header['LTV2'] = hdu1[1].header['LTV2']
    hdu1[0].header['INHERIT'] = hdu1[1].header['INHERIT']
    hdu1[0].header['EXTTYPE'] = hdu1[1].header['EXTTYPE']
    hdu1[0].header['EXTNAME'] = hdu1[1].header['EXTNAME']
    hdu1[0].header['CRVAL1A'] = hdu1[1].header['CRVAL1A']
    hdu1[0].header['CRVAL2A'] = hdu1[1].header['CRVAL2A']
    hdu1[0].header['CRPIX1A'] = hdu1[1].header['CRPIX1A']
    hdu1[0].header['CRPIX2A'] = hdu1[1].header['CRPIX2A']
    hdu1[0].header['CTYPE1A'] = hdu1[1].header['CTYPE1A']
    hdu1[0].header['CTYPE2A'] = hdu1[1].header['CTYPE2A']
    hdu1[0].header['CUNIT1A'] = hdu1[1].header['CUNIT1A']
    hdu1[0].header['CUNIT2A'] = hdu1[1].header['CUNIT2A']


#h1head = hdu1[0].header + hdu1[1].header
    h1head = hdu1[0].header 
    hdunew = fits.PrimaryHDU(scidata1b,h1head)
    hdunew2 = fits.ImageHDU(scidata2b,h1head)
    hdul = fits.HDUList([hdunew,hdunew2]) 
    hdul.writeto(i.replace('.fits','_bin.fits'),overwrite = True)

