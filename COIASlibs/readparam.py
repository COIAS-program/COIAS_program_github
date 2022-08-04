#!/usr/bin/env python3                                                                                                                  
# -*- coding: UTF-8 -*
# Timestamp: 2022/08/04 11:00 sugiura
########################################################
# param.txtを読み込み, パラメータを読み出し,
# 辞書型に変換して返却する関数readparam()を定義したスクリプト.
# 他のpythonスクリプトでは,
# import readparam
# params = readparam.readparam()
# APARTURE_RADIUS = params["ar"]
# などとして利用できる.
########################################################

def is_num(s):
    try:
        float(s)
    except ValueError:
        return False
    else:
        return True

def readparam():
    f = open("param.txt","r")
    lines = f.readlines()
    f.close()

    params = {}
    for line in lines:
        if len(line)>=1:
            content = line.split()
            if not is_num(content[1]):
                raise ValueError("some second laws in param.txt are not numbers! content[1]={0}".format(content[1]))

            if content[0]=="nd" or content[0]=="ar" or content[0]=="dm" or content[0]=="sn":
                params[content[0]] = int(content[1])
            elif content[0]=="vt":
                params[content[0]] = float(content[1])

    return params
