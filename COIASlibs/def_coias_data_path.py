#!/usr/bin/env python3
# -*- coding: UTF-8 -*
#Timestamp: 2022/10/11 6:30 sugiura
#################################################################
# ただ単に~/.coias/の場所を定義しているだけ.(python用)
# ~/.coias/以下のディレクトリ構成は変わらないと思われるが,
# 今後webCOIASに使用したりすれば~/.coias/の場所や名前そのものが変わる可能性があるため
# 手間を減らすための修正である.
#################################################################

from os.path import expanduser

coiasDataPath = expanduser("~") + "/.coias"
