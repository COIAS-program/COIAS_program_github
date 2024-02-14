#!/usr/bin/env python3
# -*- coding: UTF-8 -*
# Timestamp: 2023/01/13 14:30 sugiura
#########################################################################
# カレントディレクトリにあるyyyymmddHHMM_id_send_mpc.txtと
# yyyymmddHHMM_id_final_all.txtをCOIASサーバ内の適切な場所にコピーする.
# このスクリプトは直前にメールを送ったスクリプトの終了コードを第二引数に取る.
# 0ならその時点でのメール成功, 1なら失敗である.
# 成功ならyyyymmddHHMM_id_send_mpc.txtは$COIAS_DATA_PATH/send_mpc_files/succeeded_to_be_sent以下にコピーし,
# 失敗なら$COIAS_DATA_PATH/send_mpc_files/failed_to_be_sent以下にコピーする.
# yyyymmddHHMM_id_final_all.txtは$COIAS_DATA_PATH/final_all_files/以下にコピーする.
#########################################################################

import glob
import shutil
import sys
import traceback
import print_detailed_log
import PARAM

try:
    if len(sys.argv) != 2:
        raise Exception(
            "invalid argument. Please input the name of this script and return code of send_mail_to_MPC.py"
        )

    sendMpcFileName = glob.glob("????????????_*_send_mpc.txt")
    if len(sendMpcFileName) == 0:
        raise FileNotFoundError(
            "Any send_mpc.txt is not found in the current directory."
        )
    if len(sendMpcFileName) >= 2:
        print(
            f"something wrong. More than two send_mpc.txt files exist. files={sendMpcFileName}"
        )

    finalAllFileName = glob.glob("????????????_*_final_all.txt")
    if len(finalAllFileName) == 0:
        raise FileNotFoundError(
            "Any final_all.txt is not found in the current directory."
        )
    if len(finalAllFileName) >= 2:
        print(
            f"something wrong. More than two final_all.txt files exist. files={finalAllFileName}"
        )
    finalAllDestFileName = (
        PARAM.COIAS_DATA_PATH + "/final_all_files/" + finalAllFileName[0]
    )

    succeedSendMail = True if int(sys.argv[1]) == 0 else False
    if succeedSendMail:
        sendMpcDestFileName = (
            PARAM.COIAS_DATA_PATH
            + "/send_mpc_files/succeeded_to_be_sent/"
            + sendMpcFileName[0]
        )
    else:
        sendMpcDestFileName = (
            PARAM.COIAS_DATA_PATH
            + "/send_mpc_files/failed_to_be_sent/"
            + sendMpcFileName[0]
        )
    shutil.copyfile(sendMpcFileName[0], sendMpcDestFileName)
    shutil.copyfile(finalAllFileName[0], finalAllDestFileName)


except FileNotFoundError:
    print(
        "Some previous files are not found in copy_sendMpc_and_finalAll_to_data_path.py!",
        flush=True,
    )
    print(traceback.format_exc(), flush=True)
    error = 1
    errorReason = 74

except Exception:
    print("Some errors occur in copy_sendMpc_and_finalAll_to_data_path.py", flush=True)
    print(traceback.format_exc(), flush=True)
    error = 1
    errorReason = 75

else:
    error = 0
    errorReason = 74

finally:
    errorFile = open("error.txt", "a")
    errorFile.write("{0:d} {1:d} 903 \n".format(error, errorReason))
    errorFile.close()

    if error == 1:
        print_detailed_log.print_detailed_log(dict(globals()))
