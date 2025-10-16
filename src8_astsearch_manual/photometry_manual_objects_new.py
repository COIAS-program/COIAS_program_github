#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Timestamp: 2022/08/05 22:00 sugiura
# Timestamp: 2023/06/01 22:00 urakawa
# Timestamp: 2025/10/16 18:40 urakawa
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
# 等級誤差をvariance dataから推定する方法に変更。そのため、矩形内外の判定を行う外積を使った長いコードが不要に。S.U 2025/10/16
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
### FUNCTION: PHOTOMETRY AND RADEC ###################
def get_photometry_and_radec(scidata, threeAparturePoints, nbin, zm):
    # FITSファイルに分散情報(HDU[2])が含まれているかチェック
    if len(scidata) < 3:
        print(f"警告: ファイルに分散情報(HDU[2])がありません。この天体の測光をスキップします。")
        return None
    
    # 分散データを読み込み、標準偏差マップを作成
    image_data = scidata[0].data
    variance_data = scidata[2].data.astype(np.float64)
    safe_variance = np.maximum(variance_data, 0)
    error_map = np.sqrt(safe_variance)
    
    # ---calc rect and radec---
    rect = calcrect.calc_rectangle_parameters(
        threeAparturePoints[0], threeAparturePoints[1], threeAparturePoints[2]
    )
    if rect is None:
        return None

    w1 = wcs.WCS(scidata[0].header)
    radec = w1.wcs_pix2world([rect["center"]], 0)

    # ---photometry------------
    ap = RectangularAperture(
        rect["center"], w=rect["width"], h=rect["height"], theta=rect["angle"]
    )
    
    # --- ★★★【最終修正】★★★ ---
    # RectangularAnnulusを使わず、Aperture内のフラックスと誤差のみを計算する
    phot_table = aperture_photometry(
        image_data, ap, error=error_map, method="subpixel", subpixels=5
    )

    # 背景差分は行わず、測定されたフラックスをそのまま使用する
    flux_measured = phot_table['aperture_sum'][0]
    flux_err_measured = phot_table['aperture_sum_err'][0]
    
    # ビニング補正係数 (元のピクセルスケールに戻す)
    bin_factor = nbin * nbin
    
    # 最終的なフラックスと誤差にビニング補正を適用
    final_sum = flux_measured * bin_factor
    final_sum_err = flux_err_measured * bin_factor
    # ------------------------------------

    if final_sum <= 0:
        return None

    mag = round(zm - 2.5 * math.log10(final_sum), 3)
    
    # 等級誤差を計算 (m_err ≈ 1.0857 * (flux_err / flux))
    mage = round(1.0857 * (final_sum_err / final_sum), 3)

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
