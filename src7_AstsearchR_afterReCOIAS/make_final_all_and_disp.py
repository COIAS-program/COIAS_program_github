#!/usr/bin/env python3
# -*- coding: UTF-8 -*
# Timestamp: 2024/12/01 14:00 sugiura
###########################################################################################
# modify_preRepo_as_H_sequential.pyにてH番号が連番になるようにpre_repo2_2.txtのH番号を付け替えたので,
# その付け替えをnewall_automanual2.txtにも適用してfinal_all.txtを作成し, 最終的なdisp系ファイルも作成する.
# その際pre_repo3.txt(誤差が大きいデータや重複を弾いたり名前の付け替えを全て終えた報告ファイル)に記載の
# 行の情報のみ, newall_automanual2.txtから探してきてfinal_all.txtおよびfinal_disp.txtを作成する.
# さらに, 初期の画像ファイルの名前, 新天体の数, ウェブ版findorbで得られた軌道やサイズなどの情報
# などもfinal_all.txtに追記する.
#
# 入力: H_conversion_list_simple.txt 名前付け替えの履歴のリスト
# 　　  newall_automanual2.txt 出力するall系データの検索に使用
# 　　  orbital_elements_summary_web.txt 出力する軌道情報の検索に使用
# 　　  pre_repo3.txt データを弾いたり名前の付け替えを終えた後の報告ファイル
# 出力: final_all.txt
# 　　    最終的な名前付け替えの結果まで反映されたall系ファイル
# 　　    初期の画像ファイルの名前, 新天体の数, ウェブ版findorbで得られた軌道やサイズなどの情報も持つ
# 　　  final_disp.txt
# 　　    最終的な名前付け替えの結果まで反映されたdisp系ファイル
###########################################################################################
import glob
import os
import traceback
import re
from astropy.io import fits
import visitsort
import print_detailed_log
import PARAM
import readparam

try:
    # ---for webCOIAS, we output user id to used_param.txt-------
    if PARAM.IS_WEB_COIAS:
        params = readparam.readparam()
        readparam.write_used_param("id", params["id"])
    # -----------------------------------------------------------

    # ---open output file and write header-----------------------
    outputFile = open("final_all.txt", "w", newline="\n")
    outputFile.write("---initial fits files---------------------------\n")
    if not PARAM.IS_WEB_COIAS:
        originalImgNames = sorted(
            glob.glob("warp-*.fits"), key=visitsort.key_func_for_visit_sort
        )
    else:
        f = open("selected_warp_files.txt", "r")
        lines = f.readlines()
        f.close()
        originalImgNames = []
        for line in lines:
            if line.startswith("data"):
                originalImgNames.append(line.rstrip("\n").split("/").pop(-1))
        originalImgNames = sorted(
            originalImgNames, key=visitsort.key_func_for_visit_sort
        )

    binnedImgNames = []
    for i in range(len(originalImgNames)):
        binnedImgNames.append("warp{0:02d}_bin.fits".format(i + 1))

    for i in range(len(originalImgNames)):
        hdul = fits.open(binnedImgNames[i])
        expTime = hdul[0].header["EXPTIME"]
        outputFile.write(
            "{:d}: ".format(i)
            + originalImgNames[i]
            + ": exptime[s]={:.1f}".format(expTime)
            + "\n"
        )
    outputFile.write("------------------------------------------------\n\n")

    outputFile.write("---used parameters-------------------------------\n")
    paramFile = open("used_param.txt", "r")
    parameters = paramFile.read()
    outputFile.write(parameters)
    outputFile.write("------------------------------------------------\n\n")
    # -----------------------------------------------------------

    # ---get number of new objects and name range----------------
    HNList = []
    HNMax = 0
    HNMin = 1000000000  # VERY LARGE VALUE
    preRepoFile = open("pre_repo3.txt", "r")
    preRepoLines = preRepoFile.readlines()
    preRepoFile.close()
    for line in preRepoLines:
        thisName = line.split()[0]
        if re.search(r"^H......", thisName) != None:
            thisHN = int(thisName.lstrip("H"))
            if thisHN not in HNList:
                HNList.append(thisHN)
            if thisHN > HNMax:
                HNMax = thisHN
            if thisHN < HNMin:
                HNMin = thisHN

    outputFile.write("The number of new objects: {0:d} \n".format(len(HNList)))
    outputFile.write(
        "Range of new object names: H"
        + str(HNMin).rjust(6, "0")
        + " - H"
        + str(HNMax).rjust(6, "0")
        + "\n"
    )
    # -----------------------------------------------------------

    # ---get H conversion list-----------------------------------
    HConversionListFile = open("H_conversion_list_simple.txt", "r")
    lines = HConversionListFile.readlines()
    HOld = []
    HNew = []
    for l in range(len(lines)):
        lineContents = lines[l].split()
        HOld.append(lineContents[0])
        HNew.append(lineContents[1])
    HConversionListFile.close()
    # -----------------------------------------------------------

    # ---search newall_automanual2.txt to produce final all------
    # ---we also produce final_disp.txt from pre_repo3.txt-------
    fileFinalDisp = open("final_disp.txt", "w", newline="\n")

    fileNewAllAutomanual = open("newall_automanual2.txt", "r")
    newAllLines = fileNewAllAutomanual.readlines()
    fileNewAllAutomanual.close()
    for l in range(len(preRepoLines)):
        thisName = preRepoLines[l].split()[0]
        ## search this old name
        if re.search(r"^H......", thisName) == None:
            thisOldName = thisName
        else:
            for l2 in range(len(HNew)):
                if thisName == HNew[l2]:
                    thisOldName = HOld[l2]

        ## search the same line in newall_automanual2.txt
        for newAllOneLine in newAllLines:
            if (
                preRepoLines[l].replace(thisName, thisOldName)[0:55]
                == newAllOneLine[0:55]
            ):
                contents = newAllOneLine.split()
                fileFinalDisp.write(
                    thisName
                    + " "
                    + contents[13]
                    + " "
                    + contents[16]
                    + " "
                    + contents[17]
                    + "\n"
                )
                outputFile.write(newAllOneLine.replace(thisOldName, thisName))
                break

        ## output contents of orbital_element_summary_web.txt###
        if (
            l == len(preRepoLines) - 1
            or len(preRepoLines[l + 1].split()) == 0
            or preRepoLines[l + 1].split()[0] != thisName
        ) and os.path.isfile("orbital_elements_summary_web.txt"):
            if len(thisName) == 7:
                headSpace = "     "
            elif len(thisName) == 5:
                headSpace = ""

            orbElemFile = open("orbital_elements_summary_web.txt", "r")
            orbElemLines = orbElemFile.readlines()
            orbElemFile.close()

            for l2 in range(len(orbElemLines)):
                if len(orbElemLines[l2].split()) != 0:
                    if orbElemLines[l2].split()[0].rstrip(":") == thisOldName:
                        outputFile.write(
                            headSpace + orbElemLines[l2].replace(thisOldName, thisName)
                        )
                        outputFile.write(headSpace + orbElemLines[l2 + 1])
                        outputFile.write(headSpace + orbElemLines[l2 + 2])
                        outputFile.write("\n")
                        break

    fileFinalDisp.close()
    outputFile.close()
    # -----------------------------------------------------------

except FileNotFoundError:
    print(
        "Some previous files are not found in make_final_all_and_disp.py!", flush=True
    )
    print(traceback.format_exc(), flush=True)
    error = 1
    errorReason = 74

except Exception:
    print("Some errors occur in make_final_all_and_disp.py!", flush=True)
    print(traceback.format_exc(), flush=True)
    error = 1
    errorReason = 75

else:
    error = 0
    errorReason = 74

finally:
    errorFile = open("error.txt", "a")
    errorFile.write("{0:d} {1:d} 707 \n".format(error, errorReason))
    errorFile.close()

    if error == 1:
        print_detailed_log.print_detailed_log(dict(globals()))
