#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#timestamp: 2022/6/7 12:00 sugiura

import os
import numpy as np
import re
import traceback
from changempc import *

try:
    ############ UNKNOWN  ######################
    if os.stat("nomatch_manual.txt").st_size == 0:
        empty = []
        np.savetxt("unknown_mpc_m.txt",empty,fmt="%s")
        np.savetxt("unknown_all_m.txt",empty,fmt="%s")
        np.savetxt("unknown_disp_m.txt",empty,fmt="%s")
    else:
        data = np.loadtxt("nomatch_manual.txt",dtype="str")
        fileUnknownMpc = open("unknown_mpc_m.txt","w",newline="\n")
        fileUnknownAll = open("unknown_all_m.txt","w",newline="\n")
        fileUnknownDisp = open("unknown_disp_m.txt","w",newline="\n")
        for l in range(len(data)):
            #name
            nameStr = "     H" + "{:06d}".format(int(data[l][0]))
            #time
            timeStr = change_jd_to_MPC_format_date(float(data[l][1]))
            #ra dec
            raDecStr = change_ra_dec_to_MPC_format(float(data[l][2]),float(data[l][3]))

            mpc1Row = nameStr + "  " + timeStr + " " + raDecStr + "         " + "{:.1f}".format(float(data[l][4])).rjust(4,'0') + " " + data[l][8] + "      " + "568"
            fileUnknownMpc.write(mpc1Row + "\n")
            fileUnknownAll.write(mpc1Row + " " + data[l][9] + " " + data[l][4] + " " + data[l][5] + " " + data[l][6] + " " + data[l][7] + "\n")
            fileUnknownDisp.write(nameStr + " " + data[l][9] + " " + data[l][6] + " " + data[l][7] + "\n")

        fileUnknownMpc.close()
        fileUnknownAll.close()
        fileUnknownDisp.close()
    #############################################


    ############# NUMBERED ######################
    if os.stat("match_manual.txt").st_size == 0:
        empty = []
        np.savetxt("karifugo_mpc_m.txt",empty,fmt="%s")
        np.savetxt("karifugo_all_m.txt",empty,fmt="%s")
        np.savetxt("karifugo_disp_m.txt",empty,fmt="%s")
        np.savetxt("numbered_mpc_m.txt",empty,fmt="%s")
        np.savetxt("numbered_all_m.txt",empty,fmt="%s")
        np.savetxt("numbered_disp_m.txt",empty,fmt="%s")
    else:
        data = np.loadtxt("match_manual.txt",dtype="str")
        fileKarifugoMpc = open("karifugo_mpc_m.txt","w",newline="\n")
        fileKarifugoAll = open("karifugo_all_m.txt","w",newline="\n")
        fileKarifugoDisp = open("karifugo_disp_m.txt","w",newline="\n")
        fileNumberedMpc = open("numbered_mpc_m.txt","w",newline="\n")
        fileNumberedAll = open("numbered_all_m.txt","w",newline="\n")
        fileNumberedDisp = open("numbered_disp_m.txt","w",newline="\n")
    
        for l in range(len(data)):
            #---name----------------------------
            if re.search(r'[a-zA-Z]',data[l][0]):
                nameStr = "     " + get_MPC_format_name_for_karifugo_asteroids(data[l][0])
                fileMpc = fileKarifugoMpc
                fileAll = fileKarifugoAll
                fileDisp = fileKarifugoDisp
            else:
                nameStr = get_MPC_format_name_for_numbered_asteroids(data[l][0]) + "       "
                fileMpc = fileNumberedMpc
                fileAll = fileNumberedAll
                fileDisp = fileNumberedDisp
            #-----------------------------------

            #time
            timeStr = change_jd_to_MPC_format_date(float(data[l][1]))
            #ra dec
            raDecStr = change_ra_dec_to_MPC_format(float(data[l][2]),float(data[l][3]))
            mpc1Row = nameStr + "  " + timeStr + " " + raDecStr + "         " + "{:.1f}".format(float(data[l][4])).rjust(4,'0') + " " + data[l][8] + "      " + "568"
            fileMpc.write(mpc1Row + "\n")
            fileAll.write(mpc1Row + " " + data[l][9] + " " + data[l][4] + " " + data[l][5] + " " + data[l][6] + " " + data[l][7] + "\n")
            fileDisp.write(nameStr + " " + data[l][9] + " " + data[l][6] + " " + data[l][7] + "\n")

        fileKarifugoMpc.close()
        fileKarifugoAll.close()
        fileKarifugoDisp.close()
        fileNumberedMpc.close()
        fileNumberedAll.close()
        fileNumberedDisp.close()
    #############################################

except FileNotFoundError:
    print("Some previous files are not found in change_data_to_mpc_format_manual.py!")
    print(traceback.format_exc())
    error = 1
    errorReason = 84

except Exception:
    print("Some errors occur in change_data_to_mpc_format_manual.py!")
    print(traceback.format_exc())
    error = 1
    errorReason = 85

else:
    error = 0
    errorReason = 84

finally:
    errorFile = open("error.txt","a")
    errorFile.write("{0:d} {1:d} 804 \n".format(error,errorReason))
    errorFile.close()
