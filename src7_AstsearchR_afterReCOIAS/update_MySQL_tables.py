#!/usr/bin/env python3
# -*- coding: UTF-8 -*
#Timestamp: 2022/12/26 11:00 sugiura
################################################################################################################
# webCOIASにて今回の測定結果に基づいてMySQLのデータベースを更新し, サーバ内に保存する用のsend_mpc.txtとfinal_all.txtとして
# それらのファイル名の頭にyyyymmddHHMM_id_を付与したファイルとしてカレントにコピーする.
#
# 最初に重複したファイル作成やデータベース登録を防ぐため, カレントにあるyyyymmddHHMM_id_send_mpc.txt or final_all.txtを削除し,
# measure_resultテーブルのwork_dirが同じかつmeasure_dataがこのスクリプトを走らせている日, 前日, 翌日に該当するレコードは削除する.
# 削除されたレコードが存在した場合, 今回のデータでのレポート作成は2回目と見なしsecondDone=Trueとする.
#
# selected_warp_files.txtに記載の今回解析した画像について, image_infoテーブルの当該画像のis_auto_measuredをtrueにし,
# secondDone==Falseの時はmeasurer_uidにユーザーidを追記する.
# final_all.txtに手動測定点が1つでもあった場合, image_infoテーブルの当該画像のis_manual_measuredもtrueにする.
# 当該画像について, このスクリプト実施前はis_auto_measured=falseだった場合, 新規解析なのでdir_structureテーブルの
# この画像が含まれている上位のディレクトリ全てのn_measured_imagesを1ずつ増やす.
#
# final_all.txtに記載の情報を元にmeasure_resultテーブルにデータを追加する.
# mpcフォーマットの情報が含まれている行が1レコードに対応するようにデータを追加する.
#
# 最後に, send_mpc.txtとfinal_all.txtをコピーしてファイルにyyyymmddHHMM_id_の接頭辞をつける.
################################################################################################################
import os
import glob
import re
import shutil
from os.path import expanduser
from datetime import datetime, timedelta
import traceback
import print_detailed_log
import readparam
import changempc
import pymysql

### function: connect to the database COIAS ###############
def connect_to_COIAS_database():
    ## get password
    pwFileName = expanduser("~") + "/.pw/pwCOIASdb.txt"
    f = open(pwFileName, "r")
    pw = f.readline().rstrip("\n")
    f.close()

    ## connect
    connection = pymysql.connect(host="localhost",
                                 user="dataHandler",
                                 database="COIAS",
                                 charset="utf8",
                                 password=pw,
                                 cursorclass=pymysql.cursors.DictCursor
                                 )
    cursor = connection.cursor()

    return (connection, cursor)
###########################################################

class InvalidIDError(Exception):
    pass

try:
    #---check the input user id is valid--------------------
    params = readparam.readparam()
    measurerId = params["id"]
    if measurerId < 0:
        raise InvalidIDError
    #-------------------------------------------------------

    ## connect to the COIAS database
    connection, cursor = connect_to_COIAS_database()
    
    #---If this script runs second time in the same analysis,
    #---duplicated data are created, thus we clear such data.
    shouldRmSendMPCFileName = glob.glob("????????????_*_send_mpc.txt")
    for fileName in shouldRmSendMPCFileName:
        os.remove(fileName)
    shouldRmFinalAllFileName = glob.glob("????????????_*_final_all.txt")
    for fileName in shouldRmFinalAllFileName:
        os.remove(fileName)

    strToday     = datetime.strftime(datetime.today(), "%Y-%m-%d")
    strTomorrow  = datetime.strftime(datetime.today() + timedelta(days=1), "%Y-%m-%d")
    strYesterday = datetime.strftime(datetime.today() - timedelta(days=1), "%Y-%m-%d")
    currentDirName = os.getcwd()
    cursor.execute(f"DELETE FROM measure_result WHERE work_dir = '{currentDirName}' AND (measure_date = '{strYesterday}' OR measure_date = '{strToday}' OR measure_date = '{strTomorrow}')")
    secondDone = (cursor.rowcount!=0)
    #-------------------------------------------------------

    ## read all contents of final_all.txt
    f = open("final_all.txt","r")
    finalAllLines = f.readlines()
    NLinesOfFinalAll = len(finalAllLines)
    f.close()

    ## check the current analysis includes manually measured points
    isManualMeasured = False
    for line in finalAllLines:
        contents = line.split()
        if len(contents)!=0:
            if re.fullmatch("\w[0-9]{4}",contents[0]) or re.fullmatch("~[0-9]{4}",contents[0]) or re.fullmatch("J......",contents[0]) or re.fullmatch("K......",contents[0]) or re.fullmatch("H[0-9]{6}",contents[0]):
                if contents[-1]=="m":
                    isManualMeasured = True

    currentLine = 0
    #---update image_info and dir_structure tables----------
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
        cursor.execute(f"SELECT is_auto_measured,image_id,direct_parent_dir_id,measurer_uid FROM image_info WHERE image_name='{imageName}'")
        result = cursor.fetchall()
        if len(result)!=1:
            raise Exception(f"something wrong! image_info table has no or multiple records with image name {imageName}. N records = {len(result)}")
        isAlreadyMeasuredImage = (result[0]["is_auto_measured"]==1)
        imageIdList.append(result[0]["image_id"])
        directParentDirId = result[0]["direct_parent_dir_id"]
        previousMeasurerUidStr = result[0]["measurer_uid"]
        
        if not isAlreadyMeasuredImage and secondDone:
            raise Exception("something wrong! image_info table says this image is not yet analyzed, but secondDone flag is true.")

        ## update is_auto_measured field of image_info table
        cursor.execute(f"UPDATE image_info SET is_auto_measured=true WHERE image_name='{imageName}'")
        connection.commit()

        ## update is_manual_measured field of image_info table
        if isManualMeasured:
            cursor.execute(f"UPDATE image_info SET is_manual_measured=true WHERE image_name='{imageName}'")
            connection.commit()

        ## update measurer_uid field of image_info table
        if not secondDone:
            if previousMeasurerUidStr=='':
                measurerUidStr = f"{measurerId}"
            else:
                measurerUidStr = previousMeasurerUidStr + f",{measurerId}"
            cursor.execute(f"UPDATE image_info SET measurer_uid='{measurerUidStr}' WHERE image_name='{imageName}'")
            connection.commit()

        ## update n_measured_images field of dir_structure table
        if not isAlreadyMeasuredImage:
            parentDirId = directParentDirId
            while True:
                cursor.execute(f"SELECT n_measured_images,n_total_images,this_dir_id,parent_dir_id,level FROM dir_structure WHERE this_dir_id={parentDirId}")
                result = cursor.fetchall()
                if len(result)!=1:
                    raise Exception(f"something wrong! dir_structure table has no or multiple records with this_dir_is={parentDirId}. N records = {len(result)}")
                thisDirId = result[0]["this_dir_id"]
                level = result[0]["level"]
                nTotalImages = result[0]["n_total_images"]
                updatedNMeasuredImages = result[0]["n_measured_images"] + 1
                if updatedNMeasuredImages > nTotalImages:
                    raise Exception(f"something wrong! this directory id = {thisDirId} has more measured images (N={updatedNMeasuredImages}) than total images (N={updatedNMeasuredImages})")

                cursor.execute(f"UPDATE dir_structure SET n_measured_images={updatedNMeasuredImages} WHERE this_dir_id={thisDirId}")

                if level==0:
                    break

                parentDirId = result[0]["parent_dir_id"]
    #-------------------------------------------------------

    ## set name of final_all.txt with prefix
    dtNow = datetime.now()
    prefix = datetime.strftime(dtNow, "%Y%m%d%H%M") + f"_{measurerId}_"
    prefixedFinalAllFileName = prefix + "final_all.txt"
    prefixedSendMPCFileName  = prefix + "send_mpc.txt"

    ## get aparture radius from final_all.txt
    while not finalAllLines[currentLine].startswith("---used parameters"):
        currentLine += 1
    while not finalAllLines[currentLine].startswith("---------------------"):
        if finalAllLines[currentLine].startswith("ar"):
            apartureRadius = int(finalAllLines[currentLine].split()[1])
        currentLine += 1

    #---insert data in final_all.txt to measure_result table-----
    finalAllOneLineInfoObjectList = []
    while currentLine < NLinesOfFinalAll:
        line = finalAllLines[currentLine].rstrip("\n")
        contents = line.split()
        ## empty line
        if len(contents)==0:
            pass
        ## line including mpc format information
        elif (re.fullmatch("\w[0-9]{4}",contents[0]) or re.fullmatch("~[0-9]{4}",contents[0]) or re.fullmatch("J......",contents[0]) or re.fullmatch("K......",contents[0]) or re.fullmatch("H[0-9]{6}",contents[0])) and (contents[-1]=="a" or contents[-1]=="m"):
            obj = {}
            obj['final_all_one_line'] = line
            obj['object_name'] = contents[0]
            obj['ra_deg'] = changempc.change_ra_in_MPC_to_degree(contents[4] + " " + contents[5] + " " + contents[6])
            obj['dec_deg'] = changempc.change_dec_in_MPC_to_degree(contents[7] + " " + contents[8] + " " + contents[9])
            obj['measured_image_id'] = imageIdList[int(contents[13])]
            obj['mag'] = float(contents[14])
            obj['mag_err'] = float(contents[15])
            obj['x_pix'] = float(contents[16])
            obj['y_pix'] = float(contents[17])
            obj['is_auto'] = "true" if contents[18]=="a" else "false"
            finalAllOneLineInfoObjectList.append(obj)
        ## line of observation arc == the end of one asteroid. Insert into the table.
        elif re.search("observations",line):
            observationArcLine = line.rstrip("\n")
            for obj in finalAllOneLineInfoObjectList:
                cursor.execute(f"INSERT INTO measure_result (measured_image_id, measurer_uid, final_all_txt_name, measure_date, work_dir, aparture_radius, final_all_one_line, object_name, ra_deg, dec_deg, mag, mag_err, x_pix, y_pix, is_auto, observation_arc) VALUES({obj['measured_image_id']}, {measurerId}, '{prefixedFinalAllFileName}', '{strToday}', '{currentDirName}', {apartureRadius}, '{obj['final_all_one_line']}', '{obj['object_name']}', {obj['ra_deg']}, {obj['dec_deg']}, {obj['mag']}, {obj['mag_err']}, {obj['x_pix']}, {obj['y_pix']}, {obj['is_auto']}, '{observationArcLine}')")
                connection.commit()
            finalAllOneLineInfoObjectList = []
        
        currentLine += 1
    #------------------------------------------------------------

    ## copy send_mpc.txt and final_all.txt as file with prefixed name
    shutil.copyfile("final_all.txt", prefixedFinalAllFileName)
    shutil.copyfile("send_mpc.txt", prefixedSendMPCFileName)

    cursor.close()
    connection.close()
    
except FileNotFoundError:
    print("Some previous files are not found in update_MySQL_tables.py!",flush=True)
    print(traceback.format_exc(),flush=True)
    error = 1
    errorReason = 74

except InvalidIDError:
    print(f"Invalid ID: id={measurerId}. In webCOIAS, please specify valid id as follows: AstsearchR_afterReCOIAS id=yourUserID.")
    print(traceback.format_exc(),flush=True)
    error = 1
    errorReason = 75

except Exception:
    print("Some errors occur in update_MySQL_tables.py!",flush=True)
    print(traceback.format_exc(),flush=True)
    error = 1
    errorReason = 75

else:
    error = 0
    errorReason = 74

finally:
    errorFile = open("error.txt","a")
    errorFile.write("{0:d} {1:d} 714 \n".format(error,errorReason))
    errorFile.close()

    if error==1:
        print_detailed_log.print_detailed_log(dict(globals()))
