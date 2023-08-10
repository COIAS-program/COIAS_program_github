#!/usr/bin/env python3
# -*- coding: UTF-8 -*
# Timestamp: 2023/03/29 9:30 sugiura 　=> 2023/08/10 20:00 urakawa
################################################################################################
# 過去にMPCに報告したデータ(同じファイル内でも違っても)とほとんど同じjd, ra, decを持つデータを再度報告すると,
# 名前が一致していてもしていなくてもMPCに怒られる.
# これを防ぐため過去の報告データ(pre_repo3_*.txt)が~/.coias/past_pre_repo_data/以下に保存されているので,
# それらとカレントにある報告データ(pre_repo.txt)の照合を行って一致するデータを削除する.
# 削除の結果カレントに書き出されるファイルがpre_repo3.txtである.
# なお, ~/.coias/past_pre_repo_data/以下のpre_repo3_*.txtの一行目にはこのファイルの作成を行った
# ディレクトリの絶対パスが記載されている.
# この記載ディレクトリとカレントディレクトリが一致している場合は, 削除を行わない.
# なぜならば, AstsearchR_afterReCOIASを何らかの理由でカレントディレクトリで2回連続で実行した場合,
# 1回目の実行時に現在のpre_repo3.txtが~/.coias/past_pre_repo_data/以下に保存されるが,
# 2回目の実行時にこれを削除の照合対象にしたらカレントのpre_repo.txtと全て一致して全部消えてしまうからである.
# (原則として画像を変えたら作業ディレクトリも変えるということを念頭に置いている)
#
# 入力: warp01_bin.fits 今回測定した画像観測日のyyyy-mm-ddを取得するために使用
# 　　  pre_repo.txt
# 出力: pre_repo2.txt
# 　　    過去の計測で出力されたpre_repo3_*.txtと照合を行い, jd, ra, decがほぼ一致したデータを
# 　　    pre_repo.txtから削除したもの.
# 2023/08/10 20:00 urakawa
# L123 L124 raDiff, decDiffを4.0秒角に変更=>DUPLICATE_THRESH_ARCSEC で定義に変更 
################################################################################################
import traceback
import os
import shutil
import glob
from astropy.io import fits
from astropy.time import Time
import print_detailed_log
import PARAM

#Define thresh arcsec
DUPLICATE_THRESH_ARCSEC = 6.0


class NothingToDo(Exception):
    pass


def extract_jd_ra_dec_info_from_MPC_line(MPCOneLine):
    jdStr = MPCOneLine[15:31]

    raHour = float(MPCOneLine.split()[4])
    raMin = float(MPCOneLine.split()[5])
    raSec = float(MPCOneLine.split()[6])
    raArcSec = (360.0 / 24.0) * (raHour * 60 * 60 + raMin * 60 + raSec)

    decDegree = float(MPCOneLine.split()[7])
    if decDegree < 0.0:
        sign = -1.0
    else:
        sign = 1.0
    decMin = sign * float(MPCOneLine.split()[8])
    decSec = sign * float(MPCOneLine.split()[9])
    decArcSec = decDegree * 60 * 60 + decMin * 60 + decSec

    return {"jdStr": jdStr, "raArcSec": raArcSec, "decArcSec": decArcSec}


try:
    # ---get distinct yyyy-mm-dd list of this measurement---
    distinct_yyyy_mm_dd_list = []
    warpFileNameList = glob.glob("warp*_bin.fits")
    for warpFileName in warpFileNameList:
        scidata = fits.open(warpFileName)
        jd = scidata[0].header["JD"]
        tInTimeObj = Time(jd, format="jd")
        tInIso = tInTimeObj.iso
        yyyy_mm_dd = tInIso.split()[0]
        if yyyy_mm_dd not in distinct_yyyy_mm_dd_list:
            distinct_yyyy_mm_dd_list.append(yyyy_mm_dd)
    # -------------------------------------------------------

    # ---check ~/.coias/past_pre_repo_data/yyyy-mm-dd directory exists or not
    foundCheckDir = False
    for yyyy_mm_dd in distinct_yyyy_mm_dd_list:
        dirName = PARAM.COIAS_DATA_PATH + "/past_pre_repo_data/" + yyyy_mm_dd
        if os.path.isdir(dirName):
            foundCheckDir = True
    if not foundCheckDir:
        shutil.copy("pre_repo.txt", "pre_repo2.txt")
        raise NothingToDo
    # -----------------------------------------------------------------------

    # ---remove duplicate--------------------------
    preRepoInputFile = open("pre_repo.txt", "r")
    inputLines = preRepoInputFile.readlines()
    preRepoInputFile.close()

    currentDir = os.getcwd()
    compareFileNames = []
    for yyyy_mm_dd in distinct_yyyy_mm_dd_list:
        compareFileNames += sorted(
            glob.glob(
                PARAM.COIAS_DATA_PATH
                + "/past_pre_repo_data/"
                + yyyy_mm_dd
                + "/pre_repo3_*.txt"
            )
        )
    for l in reversed(range(len(inputLines))):
        inputLine = inputLines[l]
        inputLineInfo = extract_jd_ra_dec_info_from_MPC_line(inputLine)
        duplicateFlag = False

        for fileName in compareFileNames:
            compareFile = open(fileName, "r")
            compareLines = compareFile.readlines()
            compareFile.close()

            if compareLines[0].rstrip("\n") == currentDir:
                ### we skip the data produced from the same working directory
                continue

            for lc in range(1, len(compareLines)):
                compareLineInfo = extract_jd_ra_dec_info_from_MPC_line(compareLines[lc])
                ### compare compareLine and inputLine
                ### if jd exactly match, differences of ra and dec are smaller than 1 arcsec
                ### we delete the line and do not output it
                raDiff = abs(inputLineInfo["raArcSec"] - compareLineInfo["raArcSec"])
                decDiff = abs(inputLineInfo["decArcSec"] - compareLineInfo["decArcSec"])
                if (
                    inputLineInfo["jdStr"] == compareLineInfo["jdStr"]
                    and raDiff < DUPLICATE_THRESH_ARCSEC
                    and decDiff < DUPLICATE_THRESH_ARCSEC
                ):
                    del inputLines[l]
                    duplicateFlag = True
                    break

            if duplicateFlag:
                break
    # ---------------------------------------------

    # ---remove objects with observation numbers smaller than 2-----
    if len(inputLines) != 0:
        prevObsName = inputLines[-1][0:12]
        nObs = 0
        for i in reversed(range(len(inputLines))):
            obsName = inputLines[i][0:12]
            if obsName == prevObsName:
                nObs += 1
            else:
                if nObs <= 2:
                    for n in reversed(range(nObs)):
                        del inputLines[i + n + 1]
                nObs = 1

            if i == 0 and nObs <= 2:
                for n in reversed(range(nObs)):
                    del inputLines[n]

            prevObsName = obsName
    # --------------------------------------------------------------

    # ---output------------------------------------
    preRepoOutputFile = open("pre_repo2.txt", "w", newline="\n")
    preRepoOutputFile.writelines(inputLines)
    preRepoOutputFile.close()
    # ---------------------------------------------

except NothingToDo:
    error = 0
    errorReason = 74

except FileNotFoundError:
    print(
        "Some previous files are not found in del_duplicated_line_from_pre_repo.py!",
        flush=True,
    )
    print(traceback.format_exc(), flush=True)
    error = 1
    errorReason = 74

except Exception:
    print("Some errors occur in del_duplicated_line_from_pre_repo.py!", flush=True)
    print(traceback.format_exc(), flush=True)
    error = 1
    errorReason = 75

else:
    error = 0
    errorReason = 74

finally:
    errorFile = open("error.txt", "a")
    errorFile.write("{0:d} {1:d} 711 \n".format(error, errorReason))
    errorFile.close()

    if error == 1:
        print_detailed_log.print_detailed_log(dict(globals()))
