#!/usr/bin/env python3
# -*- coding: UTF-8 -*
# Timestamp: 2024/2/10 16:30 sugiura
################################################################################################################
# カレントディレクトリに存在するsend_mpc.txtとfinal_all.txtのファイル名に, yyyymmddHHMM_uid_の接頭辞をつけ,
# 内容をそのままに新しいファイル名でコピーする.
# ただしレポート前処理は繰り返し実行される可能性があり, その度に時刻が変わるためファイル名も変わる.
# コピー先のファイルが複数あると困るので, 前回実行時のファイルがあった場合は削除を行う.
################################################################################################################

import os
import glob
import datetime
import shutil
import traceback
import readparam
import print_detailed_log

try:
    # ---If this script runs second time in the same analysis, -----------
    # ---duplicated data are created, thus we clear such data. -----------
    shouldRmSendMPCFileName = glob.glob("????????????_*_send_mpc.txt")
    for fileName in shouldRmSendMPCFileName:
        os.remove(fileName)
    shouldRmFinalAllFileName = glob.glob("????????????_*_final_all.txt")
    for fileName in shouldRmFinalAllFileName:
        os.remove(fileName)
    # --------------------------------------------------------------------

    # --- ユーザIDと時刻を取得し, prefixを生成 -------------------------------
    params = readparam.readparam()
    measurerId = params["id"]
    dtNow = datetime.now()
    prefix = datetime.strftime(dtNow, "%Y%m%d%H%M") + f"_{measurerId}_"
    # --------------------------------------------------------------------

    # --- コピー実行 -------------------------------------------------------
    prefixedFinalAllFileName = prefix + "final_all.txt"
    prefixedSendMPCFileName = prefix + "send_mpc.txt"

    shutil.copyfile("final_all.txt", prefixedFinalAllFileName)
    shutil.copyfile("send_mpc.txt", prefixedSendMPCFileName)
    # --------------------------------------------------------------------


except FileNotFoundError:
    print(
        "Some previous files are not found in make_prefixed_sendMpc_and_finalAll.py!",
        flush=True,
    )
    print(traceback.format_exc(), flush=True)
    error = 1
    errorReason = 74


except Exception:
    print("Some errors occur in make_prefixed_sendMpc_and_finalAll.py!", flush=True)
    print(traceback.format_exc(), flush=True)
    error = 1
    errorReason = 75

else:
    error = 0
    errorReason = 74

finally:
    errorFile = open("error.txt", "a")
    errorFile.write("{0:d} {1:d} 714 \n".format(error, errorReason))
    errorFile.close()

    if error == 1:
        print_detailed_log.print_detailed_log(dict(globals()))
