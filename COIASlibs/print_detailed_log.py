#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#Timestamp: 2022/11/17 16:00 sugiura
######################################################################################################
# エラーが生じた時に詳細なlog情報をlog.txtに書き出すための関数を定義したスクリプト.
# 2022/11/17時点で書き出す情報は以下の通り:
# 1. カレントディレクトリがどこであるか
# 2. カレントディレクトリにあるファイルの一覧とサイズ(ls -lの内容)
# 3. エラーが生じた時点のpythonスクリプト中で定義している変数の一覧
#    これはこの関数を実行する時に, dict(globals())を引数として渡された辞書を使って出力している.
# ひとまず形式と内容は適当. 検討が進めば随時アップデートしていく.
######################################################################################################
import os
import subprocess

def print_detailed_log(varDict):
    f = open("log.txt","a")

    f.write("###the current directory##########################\n")
    f.write(os.getcwd()+"\n")
    f.write("##################################################\n\n")

    f.write("###the file list in the current directory#########\n")
    f.flush()
    subprocess.run("ls -l >> log.txt",shell=True)
    f.write("##################################################\n\n")

    f.write("###the variable list##############################\n")
    for key in varDict.keys():
        f.write(f"{key}: {varDict[key]} \n\n")
    f.write("##################################################\n\n")

    f.close()
