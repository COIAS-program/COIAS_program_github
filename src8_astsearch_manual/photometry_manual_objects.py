#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: 2022/08/05 22:00 sugiura
# Timestamp: 2023/06/01 22:00 urakawa
###################################################################################################
# memo_manual.txtに記載された手動測定で得られた手動測定天体の長方形アパーチャーの情報を元にして,
# それらのアパーチャー測光を行い, 手動測定天体の等級とその誤差を計算する.
# 入力: memo_manual.txt
# 　　    手動測定の結果を記したファイル
# 　　    書式: 新天体番号(Hなし) 画像番号 手動天体座標[X Y](pixel) アパーチャーを定義する3点[X Y](pixel)x3組
# 　　  "warp*_bin_nonmask.fits
# 　　    ビニングされた元画像ファイル, 測光のカウント値を得るために必要
# 出力: listb3.txt
# 　　    測光の結果および座標をra, decに変換した結果が記入されたファイル
# 　　    書式: 新天体番号(Hなし) jd ra[degree] dec[degree] mag magerr Xpixel Ypixel フィルター 画像番号
# Sky noise are estimated from the sky deviation **2 of local anulus area.
# If sky noise can not be estimated due to the edge of image, sky noise is estimated from a typical sky deviaion of full image. S.U 2023/6/1
####################################################################################################
from astropy.io import fits
from astropy.wcs import wcs
from photutils import RectangularAperture
from photutils import RectangularAnnulus
from photutils import aperture_photometry
import math
import glob
import traceback
import os
import sys
import calcrect
import numpy as np
import print_detailed_log
#S.U modified
from scipy.stats import sigmaclip

### FUNCTION: PHOTOMETRY AND RADEC ###################
def get_photometry_and_radec(scidata, threeAparturePoints, nbin, zm):
    # ---calc rect and radec---
    rect = calcrect.calc_rectangle_parameters(
        threeAparturePoints[0], threeAparturePoints[1], threeAparturePoints[2]
    )
    if rect == None:
        return None

    w1 = wcs.WCS(scidata[0].header)
    radec = w1.wcs_pix2world([rect["center"]], 1)

    # ---photometry------------
    ap = RectangularAperture(
        rect["center"], w=rect["width"], h=rect["height"], theta=rect["angle"]
    )
    sap = RectangularAnnulus(
        rect["center"],
        w_in=rect["width"] + 2,
        w_out=rect["width"] + 4,
        h_in=rect["height"] + 2,
        h_out=rect["height"] + 4,
        theta=rect["angle"],
    )
    # outer rectangle coordinate
    w_in=rect["width"] + 2
    w_out=rect["width"] + 4
    h_in=rect["height"] + 2
    h_out=rect["height"] + 4
    theta=rect["angle"]
    #Estimation of sky deviation from full image
    img_sky  = sigmaclip(scidata[0].data,3,3)
    img_sky2 = np.std(img_sky[0])**2

    size = w_out if w_out > h_out else h_out
    center_x, center_y = int(size*2), int(size*2)
    ax = w_out * math.cos(theta) - h_out * math.sin(theta) + center_x
    ay = w_out * math.sin(theta) + h_out * math.cos(theta) + center_y
    bx = w_out * math.cos(theta) * (-1) - h_out * math.sin(theta) + center_x
    by = w_out * math.sin(theta) * (-1) + h_out * math.cos(theta) + center_y
    cx = w_out * math.cos(theta) * (-1) + h_out * math.sin(theta) + center_x 
    cy = w_out * math.sin(theta) * (-1) - h_out * math.cos(theta) + center_y
    dx = w_out * math.cos(theta) + h_out * math.sin(theta) + center_x 
    dy = w_out * math.sin(theta) - h_out * math.cos(theta) + center_y
    
    # make vector from outer rectangle
    vector_a = np.array([ax,ay])
    vector_b = np.array([bx,by])
    vector_c = np.array([cx,cy])
    vector_d = np.array([dx,dy])
    
    vector_ab = vector_b - vector_a
    vector_bc = vector_c - vector_b
    vector_cd = vector_d - vector_c
    vector_da = vector_a - vector_d
    
    #   inner rectangle coordinate
    fx = w_in * math.cos(theta) - h_in * math.sin(theta) + center_x
    fy = w_in * math.sin(theta) + h_in * math.cos(theta) + center_y
    gx = w_in * np.cos(theta) * (-1) - h_in * np.sin(theta) + center_x
    gy = w_in * np.sin(theta) * (-1) + h_in * np.cos(theta) + center_y
    hx = w_in * np.cos(theta) * (-1) + h_in * np.sin(theta) + center_x
    hy = w_in * np.sin(theta) * (-1) - h_in * np.cos(theta) + center_y
    ix = w_in * np.cos(theta) + h_in * np.sin(theta) + center_x
    iy = w_in * np.sin(theta) - h_in * np.cos(theta) + center_y
     
    # make vector from inner rectangle
    vector_f = np.array([fx,fy])
    vector_g = np.array([gx,gy])
    vector_h = np.array([hx,hy])
    vector_i = np.array([ix,iy])
    
    vector_fg = vector_g - vector_f
    vector_gh = vector_h - vector_g
    vector_hi = vector_i - vector_h
    vector_if = vector_f - vector_i
    
    #select local area
    select = scidata[0].data[int(rect["center"][1]) - int(size*2) : int(rect["center"][1]) + int(size*2),
                             int(rect["center"][0]) - int(size*2) : int(rect["center"][0]) + int(size*2)]
    
    extracted_region = []
    for k in range(len(select)):
        for l in range(len(select[1])):
            element_x, element_y = k,l
            vector_e = np.array([k,l])
#outer area
            vector_ae = vector_e - vector_a
            vector_be = vector_e - vector_b
            vector_ce = vector_e - vector_c
            vector_de = vector_e - vector_d
#innner area
            vector_fe = vector_e - vector_f
            vector_ge = vector_e - vector_g
            vector_he = vector_e - vector_h
            vector_ie = vector_e - vector_i
           
# out product(gaiseki)
            vector_cross_ab_ae = np.cross(vector_ab,vector_ae)
            vector_cross_bc_be = np.cross(vector_bc,vector_be)
            vector_cross_cd_ce = np.cross(vector_cd,vector_ce)
            vector_cross_da_de = np.cross(vector_da,vector_de)

            vector_cross_fg_fe = np.cross(vector_fg,vector_fe)
            vector_cross_gh_ge = np.cross(vector_gh,vector_ge)
            vector_cross_hi_he = np.cross(vector_hi,vector_he)
            vector_cross_if_ie = np.cross(vector_if,vector_ie)
            if vector_cross_fg_fe > 0 and  vector_cross_gh_ge  > 0 and vector_cross_hi_he > 0 and vector_cross_if_ie > 0:                
                pass
            elif vector_cross_ab_ae > 0 and vector_cross_bc_be > 0 and vector_cross_cd_ce > 0 and vector_cross_da_de > 0:
                extracted_region.append(select[k][l])
                
    new_elements = sigmaclip(extracted_region,3,3)
#   bkg_std2 is estimated from local sky area deviation**2
    bkg_std2 = np.std(new_elements[0])**2
#If local sky can not be estimated due to the edge of image,img_sky2 (typical skynoise) is used. S.U 2023/6/1    
    if np.isnan(bkg_std2):
        bkg_std2 = img_sky2  
    rawflux_table = aperture_photometry(
        scidata[0].data, ap, method="subpixel", subpixels=5
    )
    bkgflux_table = aperture_photometry(
        scidata[0].data, sap, method="subpixel", subpixels=5
    )
    bkg_mean = bkgflux_table["aperture_sum"][0] / sap.area
    bkg_sum = bkg_mean * ap.area
    final_sum = nbin * nbin * (rawflux_table["aperture_sum"][0] - bkg_sum)
    if final_sum <= 0:
        return None
    mag = round(zm - 2.5 * math.log10(final_sum), 3)
    sigma_ron = (
        4.5 * nbin * nbin
    )  # read out noise of HSC with 2X2 binning: nobinning 4.5 e-
    gain = 3.0 / nbin  # gain of HSC with 2X2 binning :nobinning 3.0e/ADU
    S_star = gain * final_sum
    #    Noise = np.sqrt(S_star + ap.area * (gain * bkg_mean + sigma_ron * sigma_ron))  # S.U modified 2022/7/16
    Noise = np.sqrt(S_star + ap.area * (gain * bkg_std2 + sigma_ron * sigma_ron))
    SNR = S_star / Noise  # S.U modified 2023/5/31
#    print(SNR)
    # error in magnitude m_err = 1.0857/SNR
    mage = round(1.0857 / SNR, 3)

    return {"ra": radec[0, 0], "dec": radec[0, 1], "mag": mag, "mage": mage}


######################################################

try:
    ### suppress warnings ################################
    if not sys.warnoptions:
        import warnings

        warnings.simplefilter("ignore")

    if not os.path.isfile("memo_manual.txt"):
        empty = []
        np.savetxt("listb3.txt", empty, fmt="%s")
    else:
        # ---open and store input data-------------------------
        fInput = open("memo_manual.txt", "r")
        linesInput = fInput.readlines()
        fInput.close()
        # -----------------------------------------------------

        # ---open output file----------------------------------
        fOutput = open("listb3.txt", "w", newline="\n")
        # -----------------------------------------------------

        # ---read scidata--------------------------------------
        scidataNames = sorted(glob.glob("warp*_bin_nonmask.fits"))
        # -----------------------------------------------------

        # ---main loop-----------------------------------------
        for i in range(len(linesInput)):
            contents = linesInput[i].split()
            name = contents[0]
            NImage = int(contents[1])
            clickedPosition = [int(contents[2]), int(contents[3])]
            threeAparturePoints = [
                [int(contents[4]), int(contents[5])],
                [int(contents[6]), int(contents[7])],
                [int(contents[8]), int(contents[9])],
            ]

            # ---read fits and related information
            scidata = fits.open(scidataNames[NImage])
            fil = scidata[0].header["FILTER"]
            jd = scidata[0].header["JD"]
            zm = scidata[0].header["Z_P"]
            nbin = scidata[0].header["NBIN"]
            photRaDecDict = get_photometry_and_radec(
                scidata, threeAparturePoints, nbin, zm
            )
            if photRaDecDict == None:
                continue

            fOutput.write(
                name
                + " {0:.9f} {1:.7f} {2:.7f} {3:.3f} {4:.3f} {5:.2f} {6:.2f} ".format(
                    jd,
                    photRaDecDict["ra"],
                    photRaDecDict["dec"],
                    photRaDecDict["mag"],
                    photRaDecDict["mage"],
                    clickedPosition[0],
                    clickedPosition[1],
                )
                + fil
                + " "
                + str(NImage)
                + "\n"
            )
            # -----------------------------------------------------

except FileNotFoundError:
    print(
        "Some previous files are not found in photometry_manual_objects.py!", flush=True
    )
    print(traceback.format_exc(), flush=True)
    error = 1
    errorReason = 84

except Exception:

    print("Some errors occur in photometry_manual_objects.py!", flush=True)
    print(traceback.format_exc(), flush=True)
    error = 1
    errorReason = 85

else:
    error = 0
    errorReason = 84

finally:
    errorFile = open("error.txt", "a")
    errorFile.write("{0:d} {1:d} 802 \n".format(error, errorReason))
    errorFile.close()

    if error == 1:
        print_detailed_log.print_detailed_log(dict(globals()))
