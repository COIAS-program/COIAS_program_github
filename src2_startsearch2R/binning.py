#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import glob
import sys
import traceback

import numpy as np
from astropy.io import fits
from astropy.time import Time

try:
    # import lsst.afw.image as afwImage

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

    # search fits files
    img_list = sorted(glob.glob('warp-*.fits'))
    if len(img_list)==0:
        raise FileNotFoundError

    for i in img_list:
        hdu1 = fits.open(i)
        xpix = hdu1[1].header['NAXIS1']
        ypix = hdu1[1].header['NAXIS2']
        scidata = hdu1[1].data  # science-image
        maskdata = hdu1[2].data  # mask-image

        # bining
        # mean(?) ? is axis number.-1 means horizontal. 1 means vertical.
        scidata_bin = scidata.reshape(int(ypix / nbin), nbin, int(xpix / nbin), nbin).mean(-1).mean(1)
        maskdata_bin = maskdata.reshape(int(ypix / nbin), nbin, int(xpix / nbin), nbin).mean(-1).mean(1)

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
            print("Key 'FLUXMAG0' does not exist in the header and calculate it from calibration data.")
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
        else:  ## if header 'FLUXMAG0' exists
            print("Key 'FLUXMAG0' exists in the header and use the header value.")

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

except FileNotFoundError:
    print("Original 5 fits files do not exist in binning.py! Please upload these files.")
    print(traceback.format_exc())
    error = 1
    errorReason = 21

except Exception:
    print("Some errors occur in binning.py!")
    print(traceback.format_exc())
    error = 1
    errorReason = 25

else:
    error = 0
    errorReason = 21

finally:
    errorFile = open("error.txt","a")
    errorFile.write("{0:d} {1:d} 202 \n".format(error,errorReason))
    errorFile.close()
