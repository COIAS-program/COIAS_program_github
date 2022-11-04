#!/usr/bin/env python3
# -*- coding: UTF-8 -*
#Timestamp: 2022/08/04 10:00 sugiura
#################################################################
# calc_rectangle_parameters()関数を記したスクリプト.
# この関数は3点の(x,y)座標を引数に取り, 特定の手順に従って長方形を計算し,
# その長方形の幅, 高さ, 中心座標(x,y), 幅方向の水平からの角度,
# 長方形の四角の座標(x,y)を辞書型にて返却する.
#################################################################

import math

def is_num(s):
    try:
        float(s)
    except ValueError:
        return False
    else:
        return True

### calculate a rectangle from three 2-dimensional positions ###
### procedure is based on the Urakawa-san's script #############
def calc_rectangle_parameters(r1, r2, r3):
    if len(r1)!=2 or len(r2)!=2 or len(r3)!=2:
        raise ValueError("3 arguments for calc_rectanble_parameters should be 2-dimensional positional vectors.")
    if not is_num(r1[0]) or not is_num(r1[1]) or not is_num(r2[0]) or not is_num(r2[1]) or not is_num(r3[0]) or not is_num(r3[1]):
        raise ValueError("all arguments for calc_rectanble_parameters should be numeric.")

    if r1 == r2 or r2 == r3 or r1 == r3:
        return None
    else:
        width  = math.sqrt( (r2[0]-r1[0])*(r2[0]-r1[0]) + (r2[1]-r1[1])*(r2[1]-r1[1]) )
        height = math.sqrt( (r3[0]-r2[0])*(r3[0]-r2[0]) + (r3[1]-r2[1])*(r3[1]-r2[1]) )
        center = [ (r1[0]+r3[0])/2.0, (r1[1]+r3[1])/2.0 ]
        if r2[0] != r1[0]:
            angle = math.atan( (r2[1]-r1[1]) / (r2[0]-r1[0]) )
        elif r2[1]-r1[1] > 0.0:
            angle = 0.5*math.pi
        else:
            angle = -0.5*math.pi
            
        e1 = [math.cos(angle),             math.sin(angle)]
        e2 = [math.cos(angle+0.5*math.pi), math.sin(angle+0.5*math.pi)]

        rectPos1 = [int(center[0] - 0.5*width*e1[0] - 0.5*height*e2[0]), int(center[1] - 0.5*width*e1[1] - 0.5*height*e2[1])]
        rectPos2 = [int(rectPos1[0] + width*e1[0]), int(rectPos1[1] + width*e1[1])]
        rectPos3 = [int(rectPos2[0] + height*e2[0]), int(rectPos2[1] + height*e2[1])]
        rectPos4 = [int(rectPos3[0] - width*e1[0]), int(rectPos3[1] - width*e1[1])]

        retDict = {"width":width, "height":height, "center":center, "angle":angle, "rectPos1":rectPos1, "rectPos2":rectPos2, "rectPos3":rectPos3, "rectPos4":rectPos4}
        
        return retDict
