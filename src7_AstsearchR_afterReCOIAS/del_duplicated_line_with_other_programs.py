#!/usr/bin/env python3
# -*- coding: UTF-8 -*
# Timestamp: 2024/10/20 16:00 sugiura
################################################################################################
# COIASの測定でなくてもSSP PDRの画像を使った報告が他の人によって既に送信されていた場合,
# 我々が同じ報告を再度送信すると怒られてしまう.
# そのため既送信のうちT09でプログラムコードが4ではないものと比較し,
# near duplicatesになるものはこのスクリプトで弾いておく.
#
# 2023/10/25 たとえ同時に複数枚測定をしていてある天体名の測定が十分にあったとしても,
#            その天体の測定のうち測定点が1つしかないような測定日が1つでもあった場合,
#            MPCにレポートごと丸ごとrejectされてしまう.
#            そのため, 1 object / 1 night になるような測定もここで弾く.
#
# 入力: pre_repo2.txt
# 　　  Observations APIから取得する既知天体のMPC80行の情報
# 　　  ~/coias/param/itf_T09_except4.txt itfのうちT09かつプログラムコードが4ではないもののMPC80行情報をまとめたもの
# 出力: pre_repo2_2.txt
# 　　  pre_repo2.txtから他プログラムコードの測定を除去したもの
################################################################################################

import requests
import time
import traceback
import shutil
import re
import PARAM
import changempc

MPC_OBSERVATIONS_API_URL = "https://data.minorplanetcenter.net/api/get-obs"
COIAS_PARAM_PATH = PARAM.COIAS_DATA_PATH + "/param"
# Define thresh degree (6.0秒角に対応する角度をdegree単位で設定する)
DUPLICATE_THRESH_DEGREE = 6.0 / 3600.0
# Define thresh jd (40秒に対応する時間をjd単位で設定する)
DUPLICATE_THRESH_JD = 40.0 / (24 * 60 * 60)

try:
    ### pre_repo2.txtからpackedのままで良いので既知天体の仮符号及び確定番号の一覧を取得する
    # キーがpackedな天体名, valueがMPC80行の配列
    MPC80LinesObj = {}
    with open("pre_repo2.txt", "r") as f:
        lines = f.readlines()
        for line in lines:
            objectName = line[0:12].strip()
            if not re.match("^H......", objectName) and objectName not in MPC80LinesObj:
                MPC80LinesObj[objectName] = []

    ### Observations APIを用いて既知天体の既報告済みMPC80行の一覧を取得する
    for objectName in MPC80LinesObj:
        while True:
            try:
                response = requests.get(
                    MPC_OBSERVATIONS_API_URL,
                    json={"desigs": [objectName], "output_format": ["OBS80"]},
                )
                MPC80LinesObj[objectName] = response.json()[0]["OBS80"].rstrip("\n").split(
                    "\n"
                )
                time.sleep(0.1)
                break
            except Exception:
                time.sleep(0.1)
                continue


    ### ~/coias/param/itf_T09_except4.txtから未知天体の既報告済みMPC80行の一覧を取得する
    itfFileName = COIAS_PARAM_PATH + "/itf_T09_except4.txt"
    MPC80LinesObj["itf"] = []
    with open(itfFileName, "r") as f:
        lines = f.readlines()
        for line in lines:
            MPC80LinesObj["itf"].append(line.rstrip("\n"))

    ### pre_repo2.txtのMPC80行と, 上記のMPC80行の一覧を比較し, near duplicatesになるものを削除する
    f = open("pre_repo2.txt", "r")
    inputLines = f.readlines()
    f.close()

    for l in reversed(range(len(inputLines))):
        inputLine = inputLines[l].rstrip("\n")
        objectName = inputLine[0:12].strip()
        keyObjectName = objectName if not re.match("^H......", objectName) else "itf"
        inputLineInfo = changempc.parse_MPC80_and_get_jd_ra_dec(inputLine)

        for compareLine in MPC80LinesObj[keyObjectName]:
            # 比較相手には14文字目がCではないものがあるが, ライブラリ的にそれは困るので強制置換する
            listCompareLine = list(compareLine)
            listCompareLine[14] = "C"
            compareLineWithC = "".join(listCompareLine)

            # 比較相手にたまにパース不可能なものがあるが, 無視する
            try:
                compareLineInfo = changempc.parse_MPC80_and_get_jd_ra_dec(
                    compareLineWithC
                )
            except Exception:
                print(f"compare line is not parsable. omit. line = {compareLine}")
                continue

            # 比較・削除
            raDiff = abs(inputLineInfo["raDegree"] - compareLineInfo["raDegree"])
            decDiff = abs(inputLineInfo["decDegree"] - compareLineInfo["decDegree"])
            jdDiff = abs(inputLineInfo["jd"] - compareLineInfo["jd"])
            if (
                jdDiff < DUPLICATE_THRESH_JD
                and raDiff < DUPLICATE_THRESH_DEGREE
                and decDiff < DUPLICATE_THRESH_DEGREE
            ):
                del inputLines[l]
                break

    ### remove 1 object / 1 night data ------------------------
    # 各測定行は例えば
    # "     H238748  C2019 09 27.27542 ......"
    # のようになるため, 0 - 24 番目の文字で同じ天体・同じ測定日であるか判断できる

    ### 各天体・各測定日ごとの測定行数をカウント
    NObsPerObjectPerNight = {}
    for i in range(len(inputLines)):
        thisObjectNightStr = inputLines[i][0:25]
        if thisObjectNightStr not in NObsPerObjectPerNight:
            NObsPerObjectPerNight[thisObjectNightStr] = 0
        NObsPerObjectPerNight[thisObjectNightStr] += 1

    ### 各天体・各測定日の測定行数が1行しかないデータを削除
    for i in reversed(range(len(inputLines))):
        thisObjectNightStr = inputLines[i][0:25]
        if NObsPerObjectPerNight[thisObjectNightStr] == 1:
            del inputLines[i]
    # --------------------------------------------------------

    ### 削除されずに残った結果をpre_repo2_2.txtに書き出す
    with open("pre_repo2_2.txt", "w") as f:
        f.writelines(inputLines)

except Exception:
    ### 本スクリプトの内容は常に必須ではないため, エラーハンドリングはせず,
    ### 何某かのエラーが出たときはpre_repo2.txtを単にpre_repo2_2.txtにコピーするだけとする
    print(
        "Some errors occur in del_duplicated_line_with_other_programs.py!", flush=True
    )
    print(traceback.format_exc(), flush=True)

    shutil.copy2("pre_repo2.txt", "pre_repo2_2.txt")
