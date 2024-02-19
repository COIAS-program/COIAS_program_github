#!/usr/bin/env python3
# -*- coding: UTF-8 -*
# Timestamp: 2024/2/13 17:00 sugiura
################################################################################################################
# webCOIASにて今回の測定結果に基づいてMySQLのデータベースを更新する。
#
# selected_warp_files.txtに記載の今回解析した画像について,
# image_infoテーブルの当該画像のis_auto_measuredをtrueにし, measurer_uidにユーザーidを追記する.
# final_all.txtに手動測定点が1つでもあった場合, image_infoテーブルの当該画像のis_manual_measuredもtrueにする.
# 当該画像について, このスクリプト実施前はis_auto_measured=falseだった場合, 新規解析なのでdir_structureテーブルの
# この画像が含まれている上位のディレクトリ全てのn_measured_imagesを1ずつ増やす.
#
# final_all.txtに記載の情報を元にmeasure_resultテーブルにデータを追加する.
# mpcフォーマットの情報が含まれている行が1レコードに対応するようにデータを追加する.
################################################################################################################
import glob
import re
import os
import traceback
from datetime import datetime
import print_detailed_log
import readparam
import changempc
import COIAS_MySQL


try:
    ## connect to the COIAS database
    connection, cursor = COIAS_MySQL.connect_to_COIAS_database()

    # ---get user id ----------------------------------------
    params = readparam.readparam()
    measurerId = params["id"]
    # -------------------------------------------------------

    ## read all contents of final_all.txt
    f = open("final_all.txt", "r")
    finalAllLines = f.readlines()
    NLinesOfFinalAll = len(finalAllLines)
    f.close()

    ## check the current analysis includes manually measured points
    isManualMeasured = False
    for line in finalAllLines:
        contents = line.split()
        if len(contents) != 0:
            if (
                re.fullmatch("\w[0-9]{4}", contents[0])
                or re.fullmatch("~....", contents[0])
                or re.fullmatch("J......", contents[0])
                or re.fullmatch("K......", contents[0])
                or re.fullmatch("H[0-9]{6}", contents[0])
            ):
                if contents[-1] == "m":
                    isManualMeasured = True

    currentLine = 0
    # ---update image_info and dir_structure tables----------
    ## get warp image names analysed in this time
    imageNameList = []
    while not finalAllLines[currentLine].startswith("---initial fits files"):
        currentLine += 1
    while not finalAllLines[currentLine].startswith("---------------------"):
        imageName = finalAllLines[currentLine].split()[1].rstrip(":")
        if imageName.startswith("warp-HSC"):
            imageNameList.append(imageName)
        currentLine += 1

    imageIdList = []
    for imageName in imageNameList:
        ## check this image is already analyzed or not
        cursor.execute(
            f"SELECT is_auto_measured,image_id,direct_parent_dir_id,measurer_uid FROM image_info WHERE image_name='{imageName}'"
        )
        result = cursor.fetchall()
        if len(result) != 1:
            raise Exception(
                f"something wrong! image_info table has no or multiple records with image name {imageName}. N records = {len(result)}"
            )
        isAlreadyMeasuredImage = result[0]["is_auto_measured"] == 1
        imageIdList.append(result[0]["image_id"])
        directParentDirId = result[0]["direct_parent_dir_id"]
        previousMeasurerUidStr = result[0]["measurer_uid"]

        ## update is_auto_measured field of image_info table
        cursor.execute(
            f"UPDATE image_info SET is_auto_measured=true WHERE image_name='{imageName}'"
        )

        ## update is_manual_measured field of image_info table
        if isManualMeasured:
            cursor.execute(
                f"UPDATE image_info SET is_manual_measured=true WHERE image_name='{imageName}'"
            )

        ## update measurer_uid field of image_info table
        if previousMeasurerUidStr == "":
            measurerUidStr = f"{measurerId}"
        else:
            measurerUidStr = previousMeasurerUidStr + f",{measurerId}"
        cursor.execute(
            f"UPDATE image_info SET measurer_uid='{measurerUidStr}' WHERE image_name='{imageName}'"
        )

        ## update n_measured_images field of dir_structure table
        if not isAlreadyMeasuredImage:
            parentDirId = directParentDirId
            while True:
                cursor.execute(
                    f"SELECT n_measured_images,n_total_images,this_dir_id,parent_dir_id,level FROM dir_structure WHERE this_dir_id={parentDirId}"
                )
                result = cursor.fetchall()
                if len(result) != 1:
                    raise Exception(
                        f"something wrong! dir_structure table has no or multiple records with this_dir_is={parentDirId}. N records = {len(result)}"
                    )
                thisDirId = result[0]["this_dir_id"]
                level = result[0]["level"]
                nTotalImages = result[0]["n_total_images"]
                updatedNMeasuredImages = result[0]["n_measured_images"] + 1
                if updatedNMeasuredImages > nTotalImages:
                    raise Exception(
                        f"something wrong! this directory id = {thisDirId} has more measured images (N={updatedNMeasuredImages}) than total images (N={updatedNMeasuredImages})"
                    )

                cursor.execute(
                    f"UPDATE dir_structure SET n_measured_images={updatedNMeasuredImages} WHERE this_dir_id={thisDirId}"
                )

                if level == 0:
                    break

                parentDirId = result[0]["parent_dir_id"]
    # -------------------------------------------------------

    ## get the name of prefixed final_all.txt
    finalAllCandidateNames = glob.glob("????????????_*_final_all.txt")
    if len(finalAllCandidateNames) == 0:
        raise FileNotFoundError("cannot find any prefixed final_all.txt")
    if len(finalAllCandidateNames) >= 2:
        raise Exception(
            f"There is more than two prefixed final_all.txt. N={len(finalAllCandidateNames)}"
        )
    prefixedFinalAllFileName = finalAllCandidateNames[0]

    ## get some information
    strToday = datetime.strftime(datetime.today(), "%Y-%m-%d")
    currentDirName = os.getcwd()

    ## get aparture radius from final_all.txt
    while not finalAllLines[currentLine].startswith("---used parameters"):
        currentLine += 1
    while not finalAllLines[currentLine].startswith("---------------------"):
        if finalAllLines[currentLine].startswith("ar"):
            apartureRadius = int(finalAllLines[currentLine].split()[1])
        currentLine += 1

    # ---insert data in final_all.txt to measure_result table-----
    finalAllOneLineInfoObjectList = []
    while currentLine < NLinesOfFinalAll:
        line = finalAllLines[currentLine].rstrip("\n")
        contents = line.split()
        ## empty line
        if len(contents) == 0:
            pass
        ## line including mpc format information
        elif (
            re.fullmatch("\w[0-9]{4}", contents[0])
            or re.fullmatch("~....", contents[0])
            or re.fullmatch("J......", contents[0])
            or re.fullmatch("K......", contents[0])
            or re.fullmatch("H[0-9]{6}", contents[0])
        ) and (contents[-1] == "a" or contents[-1] == "m"):
            obj = {}
            obj["final_all_one_line"] = line
            obj["object_name"] = contents[0]
            obj["jd"] = changempc.change_datetime_in_MPC_to_jd(
                contents[1] + " " + contents[2] + " " + contents[3]
            )
            obj["ra_deg"] = changempc.change_ra_in_MPC_to_degree(
                contents[4] + " " + contents[5] + " " + contents[6]
            )
            obj["dec_deg"] = changempc.change_dec_in_MPC_to_degree(
                contents[7] + " " + contents[8] + " " + contents[9]
            )
            obj["measured_image_id"] = imageIdList[int(contents[13])]
            obj["mag"] = float(contents[14])
            obj["mag_err"] = float(contents[15])
            obj["x_pix"] = float(contents[16])
            obj["y_pix"] = float(contents[17])
            obj["is_auto"] = "true" if contents[18] == "a" else "false"
            finalAllOneLineInfoObjectList.append(obj)
        ## line of observation arc == the end of one asteroid. Insert into the table.
        elif re.search("observations", line):
            observationArcLine = line.rstrip("\n")
            for obj in finalAllOneLineInfoObjectList:
                cursor.execute(
                    f"INSERT INTO measure_result (measured_image_id, measurer_uid, final_all_txt_name, measure_date, work_dir, aparture_radius, final_all_one_line, object_name, jd, ra_deg, dec_deg, mag, mag_err, x_pix, y_pix, is_auto, observation_arc) VALUES({obj['measured_image_id']}, '{measurerId}', '{prefixedFinalAllFileName}', '{strToday}', '{currentDirName}', {apartureRadius}, '{obj['final_all_one_line']}', '{obj['object_name']}', {obj['jd']}, {obj['ra_deg']}, {obj['dec_deg']}, {obj['mag']}, {obj['mag_err']}, {obj['x_pix']}, {obj['y_pix']}, {obj['is_auto']}, '{observationArcLine}')"
                )
            finalAllOneLineInfoObjectList = []

        currentLine += 1

    ### findOrbの接続の問題などでfinal_all.txtに"observations"を含む行がなかった場合,
    ### データがDBに記録されないことが起こる.
    ### そのような場合でも大丈夫なように, ここで残っているデータをDBに挿入する
    observationArcLine = ""
    for obj in finalAllOneLineInfoObjectList:
        cursor.execute(
            f"INSERT INTO measure_result (measured_image_id, measurer_uid, final_all_txt_name, measure_date, work_dir, aparture_radius, final_all_one_line, object_name, jd, ra_deg, dec_deg, mag, mag_err, x_pix, y_pix, is_auto, observation_arc) VALUES({obj['measured_image_id']}, '{measurerId}', '{prefixedFinalAllFileName}', '{strToday}', '{currentDirName}', {apartureRadius}, '{obj['final_all_one_line']}', '{obj['object_name']}', {obj['jd']}, {obj['ra_deg']}, {obj['dec_deg']}, {obj['mag']}, {obj['mag_err']}, {obj['x_pix']}, {obj['y_pix']}, {obj['is_auto']}, '{observationArcLine}')"
        )
    # ------------------------------------------------------------


except FileNotFoundError:
    print("Some previous files are not found in update_MySQL_tables.py!", flush=True)
    print(traceback.format_exc(), flush=True)
    # エラー時はrollback
    connection.rollback()
    error = 1
    errorReason = 74


except Exception:
    print("Some errors occur in update_MySQL_tables.py!", flush=True)
    print(traceback.format_exc(), flush=True)
    # エラー時はrollback
    connection.rollback()
    error = 1
    errorReason = 75

else:
    # 成功時のみcommitを実行
    connection.commit()
    error = 0
    errorReason = 74

finally:
    COIAS_MySQL.close_COIAS_database(connection, cursor)
    errorFile = open("error.txt", "a")
    errorFile.write("{0:d} {1:d} 914 \n".format(error, errorReason))
    errorFile.close()

    if error == 1:
        print_detailed_log.print_detailed_log(dict(globals()))
