#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
from os.path import expanduser

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
    file_number = 5
    for i in range(file_number):
        detect_file_name = "warp"+str(i+1)+"_bin.dat"
        file = open(detect_file_name, "r")
        detect_lines = file.readlines()
        detection_number += len(detect_lines)-5
        file.close

    detection_number /= file_number
    #---------------------------------------------

    return detection_number

#---definition of file and program name------------
program_path = expanduser("~") + "/.coias/param/"
default_sex_file_name = program_path+"default.sex"
findsource_file_name = "findsource"
#--------------------------------------------------

#---first trial------------------------------------
detect_thresh = 1.2
mean_detection_number = calc_mean_detection_number(detect_thresh)
trial_number = 0
print("----------------------------------------------------------------")
print("#"+str(trial_number)+" detect_thresh="+"{:.2f}".format(detect_thresh)+"  mean_detection_number="+str(int(mean_detection_number)))
print("----------------------------------------------------------------")
#--------------------------------------------------

#---find two detection threshs so that prev>3000 and present<2000-----
if mean_detection_number>3000:
    while mean_detection_number>3000:
        detect_thresh_prev = detect_thresh
        mean_detection_number_prev = mean_detection_number
        
        detect_thresh = detect_thresh_prev * pow(10, 0.2)
        mean_detection_number = calc_mean_detection_number(detect_thresh)

        trial_number += 1
        print("----------------------------------------------------------------")
        print("#"+str(trial_number)+" detect_thresh="+"{:.2f}".format(detect_thresh)+"  mean_detection_number="+str(int(mean_detection_number)))
        print("----------------------------------------------------------------")

    #---find detection thresh so that 2000<detection number<3000-----
    if mean_detection_number<2000:
        detect_thresh_right = detect_thresh_prev
        detect_thresh_left  = detect_thresh
        
        while True:
            detect_thresh_center = (detect_thresh_right + detect_thresh_left)*0.5
            mean_detection_number_center = calc_mean_detection_number(detect_thresh_center)

            if mean_detection_number_center>2500:
                detect_thresh_right = detect_thresh_center
            if mean_detection_number_center<2500:
                detect_thresh_left  = detect_thresh_center

            trial_number += 1
            print("----------------------------------------------------------------")
            print("#"+str(trial_number)+" detect_thresh="+"{:.2f}".format(detect_thresh_center)+"  mean_detection_number="+str(int(mean_detection_number_center)))
            print("----------------------------------------------------------------")

            if (mean_detection_number_center>2000 and mean_detection_number_center<3000) or trial_number>40:
                break
    #-----------------------------------------------------------------
            
#---------------------------------------------------------------------
