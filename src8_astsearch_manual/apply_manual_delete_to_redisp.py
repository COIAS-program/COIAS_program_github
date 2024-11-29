#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: 2022/08/31 10:00 sugiura
##############################################################################################
# manual measureモードで削除した自動測定天体の情報をredisp.txtから削除する.
#
# 入力: manual_delete_list.txt
# 　　    manual measureモードで削除した自動検出天体の情報
# 　　    書式: manualMeasureモードでの自動検出天体名 画像番号
# 　　  redisp.txt
# 　　    manual_delete_list.txtに記載の情報を消したいファイル
# 出力: redisp2.txt
# 　　    redisp.txtからmanual_delete_list.txtに記載の自動検出天体の情報を削除したもの
##############################################################################################
import traceback
import os
import print_detailed_log

try:
    if os.path.isfile("manual_delete_list.txt"):
        # ---remove data in manual_delete_list.txt from redisp.txt and produce redisp2.txt------
        f = open("redisp.txt", "r")
        redispLines = f.readlines()
        f.close()

        f = open("manual_delete_list.txt", "r")
        manualDeleteLines = f.readlines()
        f.close()

        for manualLine in manualDeleteLines:
            for l in reversed(range(len(redispLines))):
                if (
                    manualLine.split()[0] == redispLines[l].split()[0]
                    and manualLine.split()[1] == redispLines[l].split()[1]
                ):
                    del redispLines[l]

        f = open("redisp2.txt", "w", newline="\n")
        f.writelines(redispLines)
        f.close()
        # --------------------------------------------------------------------------------------

except FileNotFoundError:
    print(
        "Some previous files are not found in apply_manual_delete_to_redisp.py!",
        flush=True,
    )
    print(traceback.format_exc(), flush=True)
    error = 1
    errorReason = 84

except Exception:
    print("Some errors occur in apply_manual_delete_to_redisp.py!", flush=True)
    print(traceback.format_exc(), flush=True)
    error = 1
    errorReason = 85

else:
    error = 0
    errorReason = 84

finally:
    errorFile = open("error.txt", "a")
    errorFile.write("{0:d} {1:d} 812 \n".format(error, errorReason))
    errorFile.close()

    if error == 1:
        print_detailed_log.print_detailed_log(dict(globals()))
