#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# timestamp: 2022/08/04 18:00 sugiura
###################################################################################
# match.txtおよびnomatch.txtに記載のデータを全てMPC フォーマットに変換し,
# さらに未発見天体候補(unknown_), 仮符号既知天体(karifugo_), 確定番号付き既知天体(numbered_)
# に振り分ける.
#
# 入力: nomatch.txt 既知天体と照合しなかった移動天体候補のデータ点リスト
# 　　  match.txt   既知天体と照合したデータ点のリスト
# 出力: unknown_ karifugo_ numbered_
#                   x
# 　　  mpc.txt   all.txt   disp.txt
# 　　  の9種類のファイル.
# 　　  例えばunknown_*.txtは書式が違うだけでデータ点や数は同じ.
# 　　  unknown_*.txtの天体名は, H+0左詰6桁にしたtrackletID
# 　　  mpc.txtの書式: MPC 80カラムフォーマット
# 　　  all.txtの書式: MPC 80カラムフォーマット 画像番号 詳細等級 等級誤差 Xpixel Ypixel
# 　　  disp.txtの書式: 天体名 画像番号 Xpixel Ypixel
###################################################################################
import os
import numpy as np
import re
import traceback
from changempc import *

try:
    ############ UNKNOWN  ######################
    if os.stat("nomatch.txt").st_size == 0:
        empty = []
        np.savetxt("unknown_mpc.txt",empty,fmt="%s")
        np.savetxt("unknown_all.txt",empty,fmt="%s")
        np.savetxt("unknown_disp.txt",empty,fmt="%s")
    else:
        data = np.loadtxt("nomatch.txt",dtype="str")
        fileUnknownMpc = open("unknown_mpc.txt","w",newline="\n")
        fileUnknownAll = open("unknown_all.txt","w",newline="\n")
        fileUnknownDisp = open("unknown_disp.txt","w",newline="\n")
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
    if os.stat("match.txt").st_size == 0:
        empty = []
        np.savetxt("karifugo_mpc.txt",empty,fmt="%s")
        np.savetxt("karifugo_all.txt",empty,fmt="%s")
        np.savetxt("karifugo_disp.txt",empty,fmt="%s")
        np.savetxt("numbered_mpc.txt",empty,fmt="%s")
        np.savetxt("numbered_all.txt",empty,fmt="%s")
        np.savetxt("numbered_disp.txt",empty,fmt="%s")
    else:
        data = np.loadtxt("match.txt",dtype="str")
        fileKarifugoMpc = open("karifugo_mpc.txt","w",newline="\n")
        fileKarifugoAll = open("karifugo_all.txt","w",newline="\n")
        fileKarifugoDisp = open("karifugo_disp.txt","w",newline="\n")
        fileNumberedMpc = open("numbered_mpc.txt","w",newline="\n")
        fileNumberedAll = open("numbered_all.txt","w",newline="\n")
        fileNumberedDisp = open("numbered_disp.txt","w",newline="\n")
    
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
    print("Some previous files are not found in change_data_to_mpc_format.py!")
    print(traceback.format_exc())
    error = 1
    errorReason = 54

except Exception:
    print("Some errors occur in change_data_to_mpc_format.py!")
    print(traceback.format_exc())
    error = 1
    errorReason = 55

else:
    error = 0
    errorReason = 54

finally:
    errorFile = open("error.txt","a")
    errorFile.write("{0:d} {1:d} 505 \n".format(error,errorReason))
    errorFile.close()
