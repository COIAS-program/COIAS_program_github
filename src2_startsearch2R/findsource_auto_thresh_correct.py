#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#Timestamp: 2022/08/04 13:00 sugiura
##############################################################################
# SExtractorを用いた光源検出スクリプトfindsourceのラッパー的スクリプト.
# 読み込む画像から検出される光源の数の画像に対する平均値が,
# param.txtに記載のsn (Source Number) 程度になるようにパラメータを調整しつつ,
# 繰り返しfindsourceを呼ぶ.
# 調整するパラメータはdefault.sexに記載のDETECT_THRESH.
# 検出光源数が多すぎる場合は, まずDETECT_THRESHを1.2から指数関数的に増やしていき,
# sn以下になるようなDETECT_THRESHを見つける.
# 次に2分法的な処理で検出光源数の平均がだいたいsnになるようにDETECT_THRESHを調整する.
#
# (正確には以下の入力と出力はfindsourceスクリプトのもの)
# 入力: マスク後の画像データ warp*_bin.fits
# 出力: 検出された光源のピクセル座標のリスト warp*_bin.dat
# 　　  (書式はファイルを直接見ればわかる)
##############################################################################
import subprocess
import traceback
import glob
import readparam
import print_progress
import print_detailed_log
from def_coias_data_path import *

### function #####################################################
def calc_mean_detection_number(detect_thresh):
    #---set detect thresh and path name to default.sex---
    file = open(default_sex_file_name, "r")
    default_sex_lines = file.readlines()
    default_sex_lines[15]="DETECT_THRESH    " + "{:.2f}".format(detect_thresh) + "          # <sigmas> or <threshold>,<ZP> in mag.arcsec-2\n"

    default_sex_lines[9]="PARAMETERS_NAME  " + coiasDataPath + "/param/default2.param  # name of the file containing catalog contents\n"
    default_sex_lines[19]="FILTER_NAME      " + coiasDataPath + "/param/default.conv   # name of the file containing the filter\n"
    file.close()

    file = open(default_sex_file_name, "w")
    file.writelines(default_sex_lines)
    file.close()
    #---------------------------------------------------

    #---point source detection--------------------
    subprocess.run(f"{findsource_file_name} > /dev/null 2>&1",shell=True)
    #---------------------------------------------

    #---calc mean detection number----------------
    detection_number = 0
    fileNameList = sorted(glob.glob('warp*_bin.dat'))
    file_number = len(fileNameList)
    for fileName in fileNameList:
        file = open(fileName, "r")
        detect_lines = file.readlines()
        detection_number += len(detect_lines)-5
        file.close

    detection_number /= file_number
    #---------------------------------------------

    return detection_number
##################################################################

try:
    print_progress.print_progress(currentCheckPoint=15)
    
    #---definition of file and program name------------
    default_sex_file_name = "default.sex"
    findsource_file_name = "findsource"
    params = readparam.readparam()
    SOURCE_NUMBER = params["sn"]
    readparam.write_used_param("sn", params["sn"])
    #--------------------------------------------------

    #---first trial------------------------------------
    detect_thresh = 1.2
    mean_detection_number = calc_mean_detection_number(detect_thresh)
    trial_number = 0
    print("----------------------------------------------------------------")
    print("#"+str(trial_number)+" detect_thresh="+"{:.2f}".format(detect_thresh)+"  mean_detection_number="+str(int(mean_detection_number)))
    print("----------------------------------------------------------------")
    #--------------------------------------------------

    #---find two detection threshs so that prev>SOURCE_NUMBER*1.25 and present<SOURCE_NUMBER*1.25-----
    if mean_detection_number>SOURCE_NUMBER*1.25:
        while mean_detection_number>SOURCE_NUMBER*1.25:
            detect_thresh_prev = detect_thresh
            mean_detection_number_prev = mean_detection_number
        
            detect_thresh = detect_thresh_prev * pow(10, 0.2)
            mean_detection_number = calc_mean_detection_number(detect_thresh)

            trial_number += 1
            print("----------------------------------------------------------------")
            print("#"+str(trial_number)+" detect_thresh="+"{:.2f}".format(detect_thresh)+"  mean_detection_number="+str(int(mean_detection_number)))
            print("----------------------------------------------------------------")

        #---find detection thresh so that SOURCE_NUMBER*0.75<detection number<SOURCE_NUMBER*1.25-----
        if mean_detection_number<SOURCE_NUMBER*0.75:
            detect_thresh_right = detect_thresh_prev
            detect_thresh_left  = detect_thresh
        
            while True:
                detect_thresh_center = (detect_thresh_right + detect_thresh_left)*0.5
                mean_detection_number_center = calc_mean_detection_number(detect_thresh_center)

                if mean_detection_number_center>SOURCE_NUMBER:
                    detect_thresh_right = detect_thresh_center
                if mean_detection_number_center<SOURCE_NUMBER:
                    detect_thresh_left  = detect_thresh_center

                trial_number += 1
                print("----------------------------------------------------------------")
                print("#"+str(trial_number)+" detect_thresh="+"{:.2f}".format(detect_thresh_center)+"  mean_detection_number="+str(int(mean_detection_number_center)))
                print("----------------------------------------------------------------")

                if (mean_detection_number_center>SOURCE_NUMBER*0.75 and mean_detection_number_center<SOURCE_NUMBER*1.25) or trial_number>40:
                    break
        #-----------------------------------------------------------------
            
    #---------------------------------------------------------------------
    print_progress.print_progress()

except FileNotFoundError:
    print("Some previous files are not found in findsource_auto_thresh_correct.py!",flush=True)
    print(traceback.format_exc(),flush=True)
    error = 1
    errorReason = 24

except Exception:
    print("Some errors occur in findsource_auto_thresh_correct.py!",flush=True)
    print(traceback.format_exc(),flush=True)
    error = 1
    errorReason = 25

else:
    error = 0
    errorReason = 24

finally:
    errorFile = open("error.txt","a")
    errorFile.write("{0:d} {1:d} 204 \n".format(error,errorReason))
    errorFile.close()

    if error==1:
        print_detailed_log.print_detailed_log(dict(globals()))
