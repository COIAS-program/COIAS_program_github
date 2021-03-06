#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# timestamp: 2022/7/15 15:00 sugiura

import subprocess
from os.path import expanduser
import traceback
import glob
import readparam

### function #####################################################
def calc_mean_detection_number(detect_thresh):
    #---set detect thresh and path name to default.sex---
    file = open(default_sex_file_name, "r")
    default_sex_lines = file.readlines()
    default_sex_lines[15]="DETECT_THRESH    " + "{:.2f}".format(detect_thresh) + "          # <sigmas> or <threshold>,<ZP> in mag.arcsec-2\n"

    default_sex_lines[9]="PARAMETERS_NAME  " + expanduser("~") + "/.coias/param/default2.param  # name of the file containing catalog contents\n"
    default_sex_lines[19]="FILTER_NAME      " + expanduser("~") + "/.coias/param/default.conv   # name of the file containing the filter\n"
    file.close()

    file = open(default_sex_file_name, "w")
    file.writelines(default_sex_lines)
    file.close()
    #---------------------------------------------------

    #---point source detection--------------------
    subprocess.run(findsource_file_name)
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
    #---definition of file and program name------------
    program_path = expanduser("~") + "/.coias/param/"
    default_sex_file_name = program_path+"default.sex"
    findsource_file_name = "findsource"
    params = readparam.readparam()
    SOURCE_NUMBER = params["sn"]
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

except FileNotFoundError:
    print("Some previous files are not found in findsource_auto_thresh_correct.py!")
    print(traceback.format_exc())
    error = 1
    errorReason = 24

except Exception:
    print("Some errors occur in findsource_auto_thresh_correct.py!")
    print(traceback.format_exc())
    error = 1
    errorReason = 25

else:
    error = 0
    errorReason = 24

finally:
    errorFile = open("error.txt","a")
    errorFile.write("{0:d} {1:d} 204 \n".format(error,errorReason))
    errorFile.close()
