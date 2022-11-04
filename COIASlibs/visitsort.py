#!/usr/bin/env python3
# -*- coding: UTF-8 -*
#Timestamp: 2022/08/19 8:30 sugiura
#################################################################
# key_func_for_visit_sort()関数を記載したスクリプト.
# 元画像fitsファイルの名前の書式は,
# warp-HSC-[filter]-[tract]-[patch],[patch]-[visit].fits
# filterの種類に関わらずvisitの数字の順に並べたいが,
# 組み込み関数のsorted()をそのまま使うと, 異なるフィルターが混在
# している時にvisitの順に並べてくれない.
# そのため, 元画像fitsファイルからvisitの数値のみを取り出して返す関数を
# 作成し, sorted()のkey引数に指定してやれば良い.
#################################################################

def key_func_for_visit_sort(fitsNameStr):
    visitNum = int(fitsNameStr.split("-")[5].split(".")[0])
    return visitNum
