#!/usr/bin/env python3
# -*- coding: UTF-8 -*
# Timestamp: 2022/12/22 12:00 sugiura
########################################################
# param.txtを読み込み, パラメータを読み出し,
# 辞書型に変換して返却する関数readparam()を定義したスクリプト.
# 他のpythonスクリプトでは,
# import readparam
# params = readparam.readparam()
# APARTURE_RADIUS = params["ar"]
# などとして利用できる.
#
# また使用したパラメータをused_param.txtに書き出す関数
# write_used_param(paramDict)も定義している.
# 引数に辞書型で与えられたパラメータをused_param.txtに
# 重複の無いように書き出す.
########################################################
import os
from uuid import UUID


def is_num(s):
    try:
        float(s)
    except ValueError:
        return False
    else:
        return True

def is_uuid(s):
    try:
        UUID(s, version=4)
    except ValueError:
        return False
    else:
        return True


def readparam():
    f = open("param.txt", "r")
    lines = f.readlines()
    f.close()

    params = {}
    for line in lines:
        if len(line) >= 1:
            content = line.split()
            if not (is_num(content[1]) or is_uuid(content[1])):
                raise ValueError(
                    "some second laws in param.txt are not valid! content[1]={0}".format(
                        content[1]
                    )
                )

            if (
                content[0] == "nd"
                or content[0] == "ar"
                or content[0] == "dm"
                or content[0] == "sn"
            ):
                params[content[0]] = int(content[1])
            elif content[0] == "vt" or content[0] == "vl":
                params[content[0]] = float(content[1])
            elif content[0] == "id":
                params[content[0]] = content[1]

    return params


def write_used_param(paramKey, paramValue):
    if not isinstance(paramKey, str) or not (is_num(paramValue) or is_uuid(paramValue)):
        raise ValueError("argument is not a pair of a key and a valid value")

    existParamDict = {}
    if os.path.isfile("used_param.txt"):
        f = open("used_param.txt", "r")
        lines = f.readlines()
        f.close()

        for line in lines:
            contents = line.split()
            key = contents[0]
            if key == "nd" or key == "ar" or key == "dm" or key == "sn":
                value = int(contents[1])
            elif key == "vt" or key == "vl":
                value = float(contents[1])
            elif key == "id":
                value = contents[1]
            else:
                raise ValueError(f"invalid key. key={key}")

            existParamDict[key] = value

    existParamDict[paramKey] = paramValue
    f = open("used_param.txt", "w")
    for k in existParamDict:
        if k == "nd" or k == "ar" or k == "dm" or k == "sn":
            f.write(k + " " + "{0:d} \n".format(existParamDict[k]))
        elif k == "vt" or k == "vl":
            f.write(k + " " + "{0:.1f} \n".format(existParamDict[k]))
        elif k == "id":
            f.write(k + " " + "{0} \n".format(existParamDict[k]))
        else:
            raise ValueError(f"invalid key. k={k}")
    f.close()
