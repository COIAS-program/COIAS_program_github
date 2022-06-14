#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# timestamp: 2022/6/7 10:00 sugiura

from astropy.io import fits
from astropy.wcs import wcs
from photutils import RectangularAperture
from photutils import RectangularAnnulus
from photutils import aperture_photometry
import math
import glob
import traceback
import calcrect

### FUNCTION: PHOTOMETRY AND RADEC ###################
def get_photometry_and_radec(scidata, threeAparturePoints, nbin, zm):
    #---calc rect and radec---
    rect = calcrect.calc_rectangle_parameters(threeAparturePoints[0], threeAparturePoints[1], threeAparturePoints[2])
    w1 = wcs.WCS(scidata[0].header)
    radec = w1.wcs_pix2world([rect["center"]],1)

    #---photometry------------
    ap = RectangularAperture(rect["center"], w=rect["width"], h=rect["height"], theta=rect["angle"])
    sap = RectangularAnnulus(rect["center"], w_in=rect["width"]+2, w_out=rect["width"]+8, h_in=rect["height"]+2, h_out=rect["height"]+8, theta=rect["angle"])

    rawflux_table = aperture_photometry(scidata[0].data, ap, method='subpixel', subpixels=5)
    bkgflux_table = aperture_photometry(scidata[0].data, sap, method='subpixel', subpixels=5)
    bkg_mean = bkgflux_table['aperture_sum'] / sap.area
    bkg_sum = bkg_mean * ap.area
    final_sum = nbin*nbin*(rawflux_table['aperture_sum'] - bkg_sum)
    if final_sum <= 0:
        final_sum = 1
    mag = round(zm - 2.5*math.log10(final_sum), 3)
    sigma_ron =  4.5*nbin*nbin #read out noise of HSC with 2X2 binning: nobinning 4.5 e-
    gain = 3.0 / nbin # gain of HSC with 2X2 binning :nobinning 3.0e/ADU
    S_star = gain * final_sum
    SNR = math.sqrt(S_star)
    # error in magnitude m_err = 1.0857/SNR
    # Noise in ADU
    mage = round(1.0857 / SNR, 3)

    return {"ra":radec[0,0], "dec":radec[0,1], "mag":mag, "mage":mage}
######################################################

try:
    #---open and store input data-------------------------
    fInput = open("memo_manual.txt","r")
    linesInput = fInput.readlines()
    fInput.close()
    #-----------------------------------------------------


    #---open output file----------------------------------
    fOutput = open("listb3.txt","w",newline="\n")
    #-----------------------------------------------------


    #---read scidata--------------------------------------
    scidataNames = sorted(glob.glob("warp*_bin.fits"))
    #-----------------------------------------------------


    #---main loop-----------------------------------------
    for i in range(len(linesInput)):
        contents = linesInput[i].split()
        name = contents[0]
        NImage = int(contents[1])
        clickedPosition = [int(contents[2]), int(contents[3])]
        threeAparturePoints = [ [int(contents[4]), int(contents[5])],
                                [int(contents[6]), int(contents[7])],
                                [int(contents[8]), int(contents[9])] ]
    
        #---read fits and related information
        scidata = fits.open(scidataNames[NImage])
        fil = scidata[0].header["FILTER"]
        jd  = scidata[0].header["JD"]
        zm  = scidata[0].header["Z_P"]
        nbin = scidata[0].header["NBIN"]
        photRaDecDict = get_photometry_and_radec(scidata, threeAparturePoints, nbin, zm)
    
        fOutput.write(name + " {0:.9f} {1:.7f} {2:.7f} {3:.3f} {4:.3f} {5:.2f} {6:.2f} ".format(jd, photRaDecDict["ra"], photRaDecDict["dec"], photRaDecDict["mag"], photRaDecDict["mage"], clickedPosition[0], clickedPosition[1])+fil+" "+str(NImage)+"\n")
    #-----------------------------------------------------


except FileNotFoundError:
    print("Some previous files are not found in photometry_manual_objects.py!")
    print(traceback.format_exc())
    error = 1
    errorReason = 84

except Exception:
    print("Some errors occur in photometry_manual_objects.py!")
    print(traceback.format_exc())
    error = 1
    errorReason = 85

else:
    error = 0
    errorReason = 84

finally:
    errorFile = open("error.txt","a")
    errorFile.write("{0:d} {1:d} 802 \n".format(error,errorReason))
    errorFile.close()
