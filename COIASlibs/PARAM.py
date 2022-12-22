#!/usr/bin/env python3
# -*- coding: UTF-8 -*
#Timestamp: 2022/12/21 15:00 sugiura
#################################################################
# 以下のいくつかのパラメータを定義しているスクリプト. (python用) 
# ~/.coias/のPATHを定義した COIAS_DATA_PATH
# webCOIASのwarp画像を格納したディレクトリのトップである
# dataディレクトリまでのPATHを定義した WARP_DATA_PATH
# webCOIASであるか否かを判定する IS_WEB_COIAS
# (IS_WEB_COIASはwebCOIAS用のリポジトリではtrue, それ以外ではfalseにする)
#################################################################

from os.path import expanduser

COIAS_DATA_PATH = expanduser("~") + "/.coias"
WARP_DATA_PATH="/Users/sugiuraks/Documents/COIAS/COIAS_program/webCOIASRoughDevelopment/disk2/"
IS_WEB_COIAS=False
