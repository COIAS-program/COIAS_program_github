#!/usr/bin/env python3
# -*- coding: UTF-8 -*
# Timestamp: 2023/01/13 14:30 sugiura
#########################################################################
# カレントディレクトリにあるyyyymmddHHMM_id_send_mpc.txtの内容を
# MPCとCOIAS開発者メーリスにメール送信する.
# メールの件名はyyyymmddHHMM_id_send_mpc.txtのファイル名とする.
# メール送信がこのスクリプトの段階で成功したか失敗したかを次の
# copy_sendMpc_and_finalAll_to_data_path.pyスクリプトに通知するため,
# このスクリプトではerrorを明示的にsys.exit()で返すようにする.
#########################################################################

import sys
import traceback
import glob
import print_detailed_log
import send_email_from_sakura
from email.mime.text import MIMEText
from email.utils import formatdate

try:
    sendMpcFileName = glob.glob("????????????_*_send_mpc.txt")
    if len(sendMpcFileName) == 0:
        raise FileNotFoundError(
            "Any send_mpc.txt is not found in the current directory."
        )
    if len(sendMpcFileName) >= 2:
        print(
            f"something wrong. More than two send_mpc.txt files exist. files={sendMpcFileName}"
        )

    # ---create an object for e-mail contents------------------------------------
    f = open(sendMpcFileName[0], "r")
    message = f.read()
    f.close()

    msg = MIMEText(message, "plain", "utf-8")
    msg["Subject"] = sendMpcFileName[0]
    msg["From"] = "coias@jsga.sakura.ne.jp"
    msg["To"] = "sugiuraks1991@star.gmobb.jp,urakawa@spaceguard.or.jp"
    msg["Date"] = formatdate()
    # ---------------------------------------------------------------------------

    # ---send e-mail-------------------------------------------------------------
    send_email_from_sakura.send_email_from_sakura(msg)
    # ---------------------------------------------------------------------------

except FileNotFoundError:
    print("Some previous files are not found in send_mail_to_MPC.py!", flush=True)
    print(traceback.format_exc(), flush=True)
    error = 1
    errorReason = 74

except Exception:
    print("Some errors occur in send_mail_to_MPC.py", flush=True)
    print(traceback.format_exc(), flush=True)
    error = 1
    errorReason = 75

else:
    error = 0
    errorReason = 74

finally:
    errorFile = open("error.txt", "a")
    errorFile.write("{0:d} {1:d} 902 \n".format(error, errorReason))
    errorFile.close()

    if error == 1:
        print_detailed_log.print_detailed_log(dict(globals()))

    sys.exit(error)
