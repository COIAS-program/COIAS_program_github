#!/usr/bin/env python3
# -*- coding: UTF-8 -*
#Timestamp: 2023/01/13 14:30 sugiura
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
from os.path import expanduser
from email.mime.text import MIMEText
from email.utils import formatdate
from smtplib import SMTP

try:
    sendMpcFileName = glob.glob("????????????_*_send_mpc.txt")
    if len(sendMpcFileName)==0:
        raise FileNotFoundError("Any send_mpc.txt is not found in the current directory.")
    if len(sendMpcFileName)>=2:
        print(f"something wrong. More than two send_mpc.txt files exist. files={sendMpcFileName}")

    #---create an object for e-mail contents------------------------------------
    f = open(sendMpcFileName[0], "r")
    message = f.read()
    f.close()

    msg = MIMEText(message, "plain", "utf-8")
    msg["Subject"] = sendMpcFileName[0]
    msg["From"] = "coias@jsga.sakura.ne.jp"
    msg["To"] = "coias@jsga.sakura.ne.jp,sugiuraks1991@star.gmobb.jp"
    msg["Date"] = formatdate()
    #---------------------------------------------------------------------------

    #---send e-mail-------------------------------------------------------------
    pwFileName = expanduser("~") + "/.pw/pwEMail.txt"
    f = open(pwFileName, "r")
    pw = f.readline().rstrip("\n")
    f.close()

    account = "coias@jsga.sakura.ne.jp"
    host = "mail.jsga.sakura.ne.jp"
    port = 587

    server = SMTP(host, port)
    server.starttls()
    server.login(account, pw)
    server.send_message(msg)
    server.quit()
    #---------------------------------------------------------------------------

except FileNotFoundError:
    print("Some previous files are not found in send_mail_to_MPC.py!",flush=True)
    print(traceback.format_exc(),flush=True)
    error = 1
    errorReason = 94

except Exception:
    print("Some errors occur in send_mail_to_MPC.py",flush=True)
    print(traceback.format_exc(),flush=True)
    error = 1
    errorReason = 95

else:
    error = 0
    errorReason = 94

finally:
    errorFile = open("error.txt","a")
    errorFile.write("{0:d} {1:d} 902 \n".format(error,errorReason))
    errorFile.close()

    if error==1:
        print_detailed_log.print_detailed_log(dict(globals()))

    sys.exit(error)
