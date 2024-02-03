#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# timestamp: 2024/1/29 19:00 sugiura
###################################################################################
# 過去に測定したデータのうち, 今回の測定の観測日と時間的に近いデータを用いて,
# それら過去のデータで検出された天体が今回の観測画像のどこにいるか予測して座標を書き出す.
# ただの線形補間で予測をするため精度は低いが, 移動速度が遅い天体なら時間的に離れていても誤差は小さいと考えられる.
# 概ね数patch移動する時間以内なら予測の対象にしても良いだろう.
# 過去に測定されたある天体が, 今回選んだ画像の時刻における測定を持っていた場合, それは予測ではなく測定済みということになる.
# 予測点なのか測定済みの点なのか, その区別もつける.
#
# 入力: MySQLのmeasure_resultテーブル
# 出力: predicted_disp.txt
# 　　    書式: 天体名 画像番号 Xpixel Ypixel 0or1(予測なら0, 既観測なら1)
###################################################################################
import sys
import glob
import math
import numpy as np
from astropy.io import fits
from astropy.wcs import wcs
import traceback
import PARAM
import COIAS_MySQL
import print_detailed_log

# 大雑把なpatchサイズ(degree)
PATCH_SIZE_ROUGH_DEGREE = 0.2
# DBから何patch先の測定まで検索してくるか
N_SEARCH_PATCHES = 5
# 線形補間が信用できるのは何patch先までか
N_INTERPOLATION_VALID_PATCHES = 3
# Define thresh jd (40秒に対応する時間をjd単位で設定する)
DUPLICATE_THRESH_JD = 40.0 / (24 * 60 * 60)
# 何日先のデータまでなら問答無用で予測円に使用するか
ABSOLUTE_PREDICT_LIMIT_DAY = 2.5


class NothingToDo(Exception):
    pass


# --- functions -------------------------------------------------------------------
# AとBという2つのjdの範囲(線分)があるとする
# この線分Aと線分Bのそれぞれの末端同士のうち最も近いものの間隔を返す
# ただし, 2つの線分が重なっていた場合は0を返す
def calcWarpAndObjectJdDiff(AJdMin, AJdMax, BJdMin, BJdMax):
    crossDiff1 = AJdMax - BJdMin
    crossDiff2 = AJdMin - BJdMax

    if crossDiff1 * crossDiff2 <= 0.0:
        return 0.0
    else:
        return min(abs(crossDiff1), abs(crossDiff2))


# 第一引数のjdが, 第2引数のjdのリストに含まれているかどうかを判定する
# ここで含まれているとは, 差が DUPLICATE_THRESH_JD 以下であることを言う
# 含まれていたら1を, 含まれていないなら0を返す
def isJdIncluded(thisJd, compareJdList):
    isIncluded = 0
    for compareJd in compareJdList:
        diffJd = abs(thisJd - compareJd)
        if diffJd < DUPLICATE_THRESH_JD:
            isIncluded = 1

    return isIncluded


# ---------------------------------------------------------------------------------

try:
    ### suppress warnings #########################################################
    if not sys.warnoptions:
        import warnings

        warnings.simplefilter("ignore")

    ### MySQL DBのmeasure_resultテーブルが必須なため, web COIASでない場合は何もしない ####
    if not PARAM.IS_WEB_COIAS:
        raise NothingToDo
    ##############################################################################

    ### 選択画像のピクセルの範囲・WCS情報・中心のradec・時刻の一覧を取得 ###################
    # ピクセル最大値取得
    scidata = fits.open("warp01_bin.fits")
    XPixelMax = scidata[0].header["NAXIS1"]
    YPixelMax = scidata[0].header["NAXIS2"]

    # WCS情報取得
    wcs0 = wcs.WCS(scidata[0].header)

    # 画像中央のra・dec取得
    raDecCenter = wcs0.wcs_pix2world(XPixelMax / 2.0, YPixelMax / 2.0, 0)
    raCenterDeg = raDecCenter[0]
    decCenterDeg = raDecCenter[1]

    # 画像の時刻の一覧を取得
    warpFileNameList = sorted(glob.glob("warp*_bin.fits"))
    warpJdList = []
    for fileName in warpFileNameList:
        scidata = fits.open(fileName)
        jd = scidata[0].header["JD"]
        warpJdList.append(jd)
    ##############################################################################

    ### DB接続及びこの画像の中心から数patch以内のデータを取得 #############################
    raMax = raCenterDeg + N_SEARCH_PATCHES * PATCH_SIZE_ROUGH_DEGREE
    raMin = raCenterDeg - N_SEARCH_PATCHES * PATCH_SIZE_ROUGH_DEGREE
    decMax = decCenterDeg + N_SEARCH_PATCHES * PATCH_SIZE_ROUGH_DEGREE
    decMin = decCenterDeg - N_SEARCH_PATCHES * PATCH_SIZE_ROUGH_DEGREE

    connection, cursor = COIAS_MySQL.connect_to_COIAS_database()
    cursor.execute(
        f"SELECT object_name, jd, ra_deg, dec_deg FROM measure_result WHERE ra_deg > {raMin} AND ra_deg < {raMax} AND dec_deg > {decMin} AND dec_deg < {decMax}"
    )
    queryResult = cursor.fetchall()
    ##############################################################################

    ### データを天体ごとに整理する #####################################################
    objectInfo = {}
    for aResult in queryResult:
        if aResult["object_name"] not in objectInfo:
            objectInfo[aResult["object_name"]] = []
        jd = aResult["jd"]
        ra = aResult["ra_deg"]
        dec = aResult["dec_deg"]
        objectInfo[aResult["object_name"]].append({"jd": jd, "ra": ra, "dec": dec})
    ##############################################################################

    ### 1データしか引っかからなかった天体は無視する #######################################
    ### また天体ごとに移動速度を見積もり,
    ### 概ね 速度 x |選択画像時刻 - その天体の測定時刻| < 数patch な天体を残す
    ### ただし時刻が概ね2日よりも近い天体は速度に関係なく残す
    warpJdMin = min(warpJdList)
    warpJdMax = max(warpJdList)

    deleteObjectNames = []
    for objectName in objectInfo:
        # 1データの天体は削除
        if len(objectInfo[objectName]) == 1:
            deleteObjectNames.append(objectName)
            continue

        # その天体の移動速度見積もり
        objectJdMinInfo = min(objectInfo[objectName], key=lambda info: info["jd"])
        objectJdMaxInfo = max(objectInfo[objectName], key=lambda info: info["jd"])
        raDiff = objectJdMaxInfo["ra"] - objectJdMinInfo["ra"]
        decDiff = objectJdMaxInfo["dec"] - objectJdMinInfo["dec"]
        jdDiff = objectJdMaxInfo["jd"] - objectJdMinInfo["jd"]
        speed = math.sqrt(raDiff * raDiff + decDiff * decDiff) / jdDiff

        # 画像と天体の測定時刻が概ね2日以内のものは問答無用で残す
        warpAndObjectJdDiff = calcWarpAndObjectJdDiff(
            warpJdMin, warpJdMax, objectJdMinInfo["jd"], objectJdMaxInfo["jd"]
        )
        if warpAndObjectJdDiff < ABSOLUTE_PREDICT_LIMIT_DAY:
            continue

        # 概ね 速度 x |選択画像時刻 - その天体の測定時刻| > 数patch な天体は消す
        if speed * warpAndObjectJdDiff > N_INTERPOLATION_VALID_PATCHES * PATCH_SIZE_ROUGH_DEGREE:
            deleteObjectNames.append(objectName)

    # 実際の削除処理
    for deleteObjectName in deleteObjectNames:
        del objectInfo[deleteObjectName]
    ##############################################################################

    ### メインの処理と出力. 各天体に対して ###############################################
    ### - 線形補間にてjd vs ra, dec の係数を計算
    ### - 係数を用いて各画像の時刻にその天体がどこにいるのか予測
    ### - その画像の時刻と測定点の時刻一覧を照合し, その測定点が測定済みか予測か区別する
    ### - ra・decをピクセル座標に変換し, 測定画像の範囲内に収まっている場合は書き出す
    outputFile = open("predicted_disp.txt", "w", newline="\n")
    for objectName in objectInfo:
        # raとdecの係数計算
        jdList = [info["jd"] for info in objectInfo[objectName]]
        raList = [info["ra"] for info in objectInfo[objectName]]
        decList = [info["dec"] for info in objectInfo[objectName]]

        raCoef = np.polyfit(jdList, raList, 1)
        decCoef = np.polyfit(jdList, decList, 1)

        for imageNum in range(len(warpJdList)):
            # この天体がこの画像においてどの位置座標にいるのか計算
            raPre = raCoef[0] * warpJdList[imageNum] + raCoef[1]
            decPre = decCoef[0] * warpJdList[imageNum] + decCoef[1]
            xyPixPre = wcs0.wcs_world2pix(raPre, decPre, 0)

            # この点が画像内にあるなら出力対象
            if (
                xyPixPre[0] > 0
                and xyPixPre[1] > 0
                and xyPixPre[0] < XPixelMax
                and xyPixPre[1] < YPixelMax
            ):
                # 測定済みか否かを判断する
                isMeasured = isJdIncluded(warpJdList[imageNum], jdList)
                # 書き出し
                outputFile.write(
                    f"{objectName} {imageNum} {xyPixPre[0]:.2f} {xyPixPre[1]:.2f} {isMeasured}\n"
                )

    outputFile.close()
    ##############################################################################


except NothingToDo:
    error = 0
    errorReason = 74

except FileNotFoundError:
    print("Some previous files are not found in make_predicted_disp.py!", flush=True)
    print(traceback.format_exc(), flush=True)
    error = 1
    errorReason = 54

except Exception:
    print("Some errors occur in make_predicted_disp.py!", flush=True)
    print(traceback.format_exc(), flush=True)
    error = 1
    errorReason = 55

else:
    error = 0
    errorReason = 54

finally:
    errorFile = open("error.txt", "a")
    errorFile.write("{0:d} {1:d} 517 \n".format(error, errorReason))
    errorFile.close()

    if error == 1:
        print_detailed_log.print_detailed_log(dict(globals()))
