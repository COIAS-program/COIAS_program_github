#!/usr/bin/env python3
# -*- coding: UTF-8 -*
# Timestamp: 2024/2/3 14:00 sugiura, 2023/08/10 20:00 urakawa
################################################################################################
# 過去にMPCに報告したデータ(同じファイル内でも違っても)とほとんど同じjd, ra, decを持つデータを再度報告すると,
# 名前が一致していてもしていなくてもMPCに怒られる.
# これを防ぐため過去の報告データ(measure_resultテーブル)とカレントにある報告データ(pre_repo.txt)の照合を行って一致するデータを削除する.
# 削除の結果カレントに書き出されるファイルがpre_repo2.txtである.
# measure_resultテーブルに記載のディレクトリとカレントディレクトリが一致している場合は, 削除を行わない.
# なぜならば, AstsearchR_afterReCOIASを何らかの理由でカレントディレクトリで2回連続で実行した場合,
# 1回目の実行時に測定データがmeasure_resultテーブルに保存されるが,
# 2回目の実行時にこれを削除の照合対象にしたらカレントのpre_repo.txtと全て一致して全部消えてしまうからである.
# (原則として画像を変えたら作業ディレクトリも変えるということを念頭に置いている)
#
# 2023/10/25 たとえ同時に複数枚測定をしていてある天体名の測定が十分にあったとしても,
#            その天体の測定のうち測定点が1つしかないような測定日が1つでもあった場合,
#            MPCにレポートごと丸ごとrejectされてしまう.
#            そのため, 1 object / 1 night になるような測定もここで弾く.
#
# 入力: warp*_bin.fits 今回測定した画像の中心座標と時刻一覧を取得するのに使用
# 　　  measure_resultテーブル
# 出力: pre_repo2.txt
# 　　    measure_resultテーブルの過去のデータと照合を行い,
# 　　    jd, ra, decがほぼ一致したデータをpre_repo.txtから削除したもの.
# 2023/08/10 20:00 urakawa
# raDiff, decDiffを6.0秒角に変更=>DUPLICATE_THRESH_ARCSEC で定義に変更
################################################################################################
import traceback
import sys
import os
import glob
from astropy.io import fits
from astropy.wcs import wcs
import print_detailed_log
import PARAM
import changempc
import COIAS_MySQL


# Define thresh degree (6.0秒角に対応する角度をdegree単位で設定する)
DUPLICATE_THRESH_DEGREE = 6.0 / 3600.0
# Define thresh jd (40秒に対応する時間をjd単位で設定する)
DUPLICATE_THRESH_JD = 40.0 / (24 * 60 * 60)
# measure_resultテーブルからデータを拾ってくるra, decの範囲(degree)
SEARCH_RA_DEC_RANGE_DEGREE = 0.4


class NothingToDo(Exception):
    pass


try:
    ### suppress warnings #########################################################
    if not sys.warnoptions:
        import warnings

        warnings.simplefilter("ignore")

    # ---MySQL DBのmeasure_resultテーブルが必須なため, web COIASでない場合は何もしない---
    if not PARAM.IS_WEB_COIAS:
        print("This script that removes near duplicates requires COIAS MySQL table.")
        print("So that we ignore this script for NON WEB COIAS mode.")
        raise NothingToDo
    # ----------------------------------------------------------------------------

    # ---測定している画像の中心のra, decおよびjdの最大・最小値を取得--
    ### 中心座標取得
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

    ### jdの最大値と最小値を取得
    # 画像の時刻の一覧を取得
    warpFileNameList = sorted(glob.glob("warp*_bin.fits"))
    warpJdList = []
    for fileName in warpFileNameList:
        scidata = fits.open(fileName)
        jd = scidata[0].header["JD"]
        warpJdList.append(jd)

    # 最大値と最小値取得
    jdMax = max(warpJdList)
    jdMin = min(warpJdList)
    # --------------------------------------------------------

    # ---measure_resultテーブルから近いデータを取得----------------
    # ---検索範囲は, ra・decに関して画像中心からSEARCH_RA_DEC_RANGE_DEGREE以内,
    # ---jdに関して選択画像のjdの最大・最小よりさらにDUPLICATE_THRESH_JD違うjd以内.
    # ---ただし, work_dirがカレントディレクトリと一致するものは除外
    currentDir = os.getcwd()
    searchJdMax = jdMax + DUPLICATE_THRESH_JD
    searchJdMin = jdMin - DUPLICATE_THRESH_JD
    searchRaMax = raCenterDeg + SEARCH_RA_DEC_RANGE_DEGREE
    searchRaMin = raCenterDeg - SEARCH_RA_DEC_RANGE_DEGREE
    searchDecMax = decCenterDeg + SEARCH_RA_DEC_RANGE_DEGREE
    searchDecMin = decCenterDeg - SEARCH_RA_DEC_RANGE_DEGREE

    # jdの検索条件
    jdConditionStr = f"(jd > {searchJdMin} AND jd < {searchJdMax})"
    # raについては周期的になっているため、範囲を超えた場合のケアが必要
    if searchRaMin < 0.0:
        searchRaMin2 = searchRaMin + 360.0
        raConditionStr = f"((ra_deg > {searchRaMin} AND ra_deg < {searchRaMax}) OR ra_deg > {searchRaMin2})"
    elif searchRaMax > 360.0:
        searchRaMax2 = searchRaMax - 360.0
        raConditionStr = f"((ra_deg > {searchRaMin} AND ra_deg < {searchRaMax}) OR ra_deg < {searchRaMax2})"
    else:
        raConditionStr = f"(ra_deg > {searchRaMin} AND ra_deg < {searchRaMax})"
    # decの検索条件
    decConditionStr = f"(dec_deg > {searchDecMin} AND dec_deg < {searchDecMax})"
    # work_dirの検索条件
    dirConditionStr = f"(work_dir != '{currentDir}')"

    # 検索実行
    connection, cursor = COIAS_MySQL.connect_to_COIAS_database()
    cursor.execute(
        f"SELECT jd, ra_deg, dec_deg FROM measure_result WHERE {jdConditionStr} AND {raConditionStr} AND {decConditionStr} AND {dirConditionStr}"
    )
    queryResult = cursor.fetchall()
    # ---------------------------------------------------------

    # ---remove duplicate--------------------------------------
    preRepoInputFile = open("pre_repo.txt", "r")
    inputLines = preRepoInputFile.readlines()
    preRepoInputFile.close()

    for l in reversed(range(len(inputLines))):
        inputLine = inputLines[l]
        inputLineInfo = changempc.parse_MPC80_and_get_jd_ra_dec(inputLine.rstrip("\n"))

        for aResult in queryResult:
            ### compare aResult and inputLine
            ### if difference of jd is smaller than 40 sec and differences of ra and dec are smaller than 6 arcsec
            ### we delete the line and do not output it
            raDiff = abs(inputLineInfo["raDegree"] - aResult["ra_deg"])
            decDiff = abs(inputLineInfo["decDegree"] - aResult["dec_deg"])
            jdDiff = abs(inputLineInfo["jd"] - aResult["jd"])
            if (
                jdDiff < DUPLICATE_THRESH_JD
                and raDiff < DUPLICATE_THRESH_DEGREE
                and decDiff < DUPLICATE_THRESH_DEGREE
            ):
                del inputLines[l]
                break
    # --------------------------------------------------------

    # ---remove 1 object / 1 night data ----------------------
    # 各測定行は例えば
    # "     H238748  C2019 09 27.27542 ......"
    # のようになるため, 0 - 24 番目の文字で同じ天体・同じ測定日であるか判断できる

    ### 各天体・各測定日ごとの測定行数をカウント
    NObsPerObjectPerNight = {}
    for i in range(len(inputLines)):
        thisObjectNightStr = inputLines[i][0:25]
        if thisObjectNightStr not in NObsPerObjectPerNight:
            NObsPerObjectPerNight[thisObjectNightStr] = 0
        NObsPerObjectPerNight[thisObjectNightStr] += 1

    ### 各天体・各測定日の測定行数が1行しかないデータを削除
    for i in reversed(range(len(inputLines))):
        thisObjectNightStr = inputLines[i][0:25]
        if NObsPerObjectPerNight[thisObjectNightStr] == 1:
            del inputLines[i]
    # --------------------------------------------------------

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
