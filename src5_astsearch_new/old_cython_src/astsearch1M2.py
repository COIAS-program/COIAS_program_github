#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# cython: boundscheck=False
# %load_ext Cython
# %%cython
# @cython.boundscheck(False)
# @cython.wraparound(False)
# cimport numpy as np
# cimport cython
import time

# multiprocessing
import numpy as np
import scipy.spatial as ss
from astropy.io import fits, ascii
from astropy.wcs import wcs
import traceback

try:
    import mktraclet
    # read catalog
    # from makedata6 import makedata6
    # from deldaburi2 import deldaburi2

    start = time.time()

    # input all point source after find.sh
    text_fnames1 = ascii.read('warp1_bin.dat')
    text_fnames2 = ascii.read('warp2_bin.dat')
    text_fnames3 = ascii.read('warp3_bin.dat')
    text_fnames4 = ascii.read('warp4_bin.dat')
    text_fnames5 = ascii.read('warp5_bin.dat')

    # read scidata
    scidata1 = fits.open('warp1_bin.fits')
    scidata2 = fits.open('warp2_bin.fits')
    scidata3 = fits.open('warp3_bin.fits')
    scidata4 = fits.open('warp4_bin.fits')
    scidata5 = fits.open('warp5_bin.fits')

    # time information & filter
    fil1 = scidata1[0].header['FILTER']
    fil2 = scidata2[0].header['FILTER']
    fil3 = scidata3[0].header['FILTER']
    fil4 = scidata4[0].header['FILTER']
    fil5 = scidata5[0].header['FILTER']

    jd1 = scidata1[0].header['JD']
    jd2 = scidata2[0].header['JD']
    jd3 = scidata3[0].header['JD']
    jd4 = scidata4[0].header['JD']
    jd5 = scidata5[0].header['JD']

    # zero magnitude
    zm1 = scidata1[0].header['Z_P']
    zm2 = scidata2[0].header['Z_P']
    zm3 = scidata3[0].header['Z_P']
    zm4 = scidata4[0].header['Z_P']
    zm5 = scidata5[0].header['Z_P']
    zm = [zm1, zm2, zm3, zm4, zm5]

    # nbin(K.S. added 2022/5/2)
    nbin1 = scidata1[0].header['NBIN']
    nbin2 = scidata2[0].header['NBIN']
    nbin3 = scidata3[0].header['NBIN']
    nbin4 = scidata4[0].header['NBIN']
    nbin5 = scidata5[0].header['NBIN']
    nbin = [nbin1, nbin2, nbin3, nbin4, nbin5]

    # X,Y pix
    xpix = scidata1[0].header['NAXIS1']
    ypix = scidata1[0].header['NAXIS2']

    # scidata
    scidata = [scidata1[0].data, scidata2[0].data, scidata3[0].data, scidata4[0].data, scidata5[0].data]

    # x,y to wcs because warp image is same wcs info
    w1 = wcs.WCS(scidata1[0].header)

    # t,x,y
    xy1 = np.array([text_fnames1['X_IMAGE'], text_fnames1['Y_IMAGE']])
    xy1 = xy1.T
    radec1 = w1.wcs_pix2world(xy1, 1)
    gyou = len(radec1)
    tt1 = np.zeros(gyou) + jd1
    radec1b = np.c_[tt1, radec1]

    xy2 = np.array([text_fnames2['X_IMAGE'], text_fnames2['Y_IMAGE']])
    xy2 = xy2.T
    radec2 = w1.wcs_pix2world(xy2, 1)
    gyou = len(radec2)
    tt1 = np.zeros(gyou) + jd2
    radec2b = np.c_[tt1, radec2]

    xy3 = np.array([text_fnames3['X_IMAGE'], text_fnames3['Y_IMAGE']])
    xy3 = xy3.T
    radec3 = w1.wcs_pix2world(xy3, 1)
    gyou = len(radec3)
    tt1 = np.zeros(gyou) + jd3
    radec3b = np.c_[tt1, radec3]

    xy4 = np.array([text_fnames4['X_IMAGE'], text_fnames4['Y_IMAGE']])
    xy4 = xy4.T
    radec4 = w1.wcs_pix2world(xy4, 1)
    gyou = len(radec4)
    tt1 = np.zeros(gyou) + jd4
    radec4b = np.c_[tt1, radec4]

    xy5 = np.array([text_fnames5['X_IMAGE'], text_fnames5['Y_IMAGE']])
    xy5 = xy5.T
    radec5 = w1.wcs_pix2world(xy5, 1)
    gyou = len(radec5)
    tt1 = np.zeros(gyou) + jd5
    radec5b = np.c_[tt1, radec5]

    # prepare delta T
    dT1 = (jd2 - jd1) * 1440
    dT2 = (jd3 - jd2) * 1440
    dT3 = (jd3 - jd1) * 1440
    dT4 = (jd4 - jd3) * 1440
    dT5 = (jd4 - jd1) * 1440
    dT6 = (jd5 - jd4) * 1440
    dT7 = (jd5 - jd3) * 1440
    dT8 = (jd4 - jd2) * 1440
    dT9 = (jd5 - jd2) * 1440

    # prepare KDTree
    tree1 = ss.KDTree(radec1, leafsize=10)
    tree2 = ss.KDTree(radec2, leafsize=10)
    tree3 = ss.KDTree(radec3, leafsize=10)
    tree4 = ss.KDTree(radec4, leafsize=10)
    tree5 = ss.KDTree(radec5, leafsize=10)

    ######################   tracklet 1-2 ##############################################
    # make traclet from frame 1 and 2
    # def mktraclet is double for

    trac1 = mktraclet.traclet1(radec1, radec2)
    # print(trac1)
    # print(list1.shape)
    # trac1 = np.array(list1)
    # revised 2020.2.13
    trac7 = []

    # strage list
    tmp4 = []
    tmp5 = []
    tmp4b = np.empty((2, 3), float)
    num3 = len(trac1)
    for k in range(num3):
        # predict #3 position
        ra3 = trac1[k, 1, 1] + (trac1[k, 1, 1] - trac1[k, 0, 1]) * dT2 / dT1
        dec3 = trac1[k, 1, 2] + (trac1[k, 1, 2] - trac1[k, 0, 2]) * dT2 / dT1
        pradec3 = (ra3, dec3)
        # make tree from radec3
        # search point from radec3 within r=0.001 deg = 3.6"
        # 2020.2.20/r=0.0005=>r=0.001 distance_upper_bound = 0.001 => 0.002
        # 2020.5.23/r=0.0001=>r=0.0005 distance_upper_bound = 0.002 => 0.004
        res = tree3.query_ball_point(pradec3, r=0.0005)
        d, ref = tree3.query(pradec3, distance_upper_bound=0.004)
        # reject number of res > 1 because it has a high possibility to be noise
        if len(res) == 1 and d < 0.001:
            # print(trac1[k],radec3[ref])
            tmp4 = np.append(trac1[k], [radec3b[ref]], axis=0)
            tmp5 = np.append(tmp5, tmp4)
        elif len(res) == 0:
            tmp4b = np.append(tmp4b, trac1[k], axis=0)
    a = int(len(tmp5) / 9)
    trac2 = tmp5.reshape(a, 3, 3)
    b = int(len(tmp4b) / 2)
    trac2b = tmp4b.reshape(b, 2, 3)
    trac2b = trac2b[1:b]
    
    # predict #4 position
    tmp4 = []
    tmp5 = []
    tmp4b = np.empty((3, 3), float)
    num4 = len(trac2)
    for l in range(num4):
        ra4 = trac2[l, 2, 1] + (trac2[l, 2, 1] - trac2[l, 0, 1]) * dT4 / dT3
        dec4 = trac2[l, 2, 2] + (trac2[l, 2, 2] - trac2[l, 0, 2]) * dT4 / dT3
        pradec4 = (ra4, dec4)
        # make tree from radec4
        # search point from radec3 within r=0.001 deg = 3.6"
        res = tree4.query_ball_point(pradec4, r=0.0005)
        d, ref = tree4.query(pradec4, distance_upper_bound=0.004)
        # reject number of res > 1 because it has a high possibility to be noise
        if len(res) == 1 and d < 0.001:
            # print(trac2[l],radec4[ref])
            tmp4 = np.append(trac2[l], [radec4b[ref]], axis=0)
            tmp5 = np.append(tmp5, tmp4)
        # tmp4b is not detected signal in frame #4
        elif len(res) == 0:
            # print(trac2[l])
            tmp4b = np.append(tmp4b, trac2[l], axis=0)
            # tmp5b = np.append(tmp5b,tmp4b)
            # tmp4b = np.append(trac2[l],axis =0)
    # 1,2,3,4 detect        
    a = int(len(tmp5) / 12)
    trac3 = tmp5.reshape(a, 4, 3)
    # 1,2,3 detect 4 undetect
    b = int(len(tmp4b) / 3)
    trac3b = tmp4b.reshape(b, 3, 3)
    trac3b = trac3b[1:b]
    
    # predict #5 position
    tmp4 = []
    tmp5 = []
    tmp4c = np.empty((4, 3), float)
    num5 = len(trac3)
    for l in range(num5):
        ra5 = trac3[l, 3, 1] + (trac3[l, 3, 1] - trac3[l, 0, 1]) * dT6 / dT5
        dec5 = trac3[l, 3, 2] + (trac3[l, 3, 2] - trac3[l, 0, 2]) * dT6 / dT5
        pradec5 = (ra5, dec5)
        # make tree from radec4
        # search point from radec3 within r=0.001 deg = 3.6"
        res = tree5.query_ball_point(pradec5, r=0.0005)
        d, ref = tree5.query(pradec5, distance_upper_bound=0.004)
        # reject number of res > 1 because it has a high possibility to be noise
        if len(res) == 1 and d < 0.001:
            # print(trac3[l],radec5[ref])
            tmp4 = np.append(trac3[l], [radec5b[ref]], axis=0)
            tmp5 = np.append(tmp5, tmp4)
        elif len(res) == 0:
            tmp4c = np.append(tmp4c, trac3[l], axis=0)
    # 1,2,3,4,5 detect
    a = int(len(tmp5) / 15)
    if a == 0:
        trac4 = []
    else:
        trac4 = tmp5.reshape(a, 5, 3)
    # 1,2,3,4 detect 5 undetect
    b = int(len(tmp4c) / 4)
    trac4b = tmp4c.reshape(b, 4, 3)
    trac4b = trac4b[1:b]
    
    # predict #5 position from #3
    tmp4 = []
    tmp5 = []
    tmp4c = np.empty((3, 3), float)
    num5 = len(trac3b)
    for l in range(num5):
        ra5 = trac3b[l, 2, 1] + (trac3b[l, 2, 1] - trac3b[l, 0, 1]) * dT7 / dT3
        dec5 = trac3b[l, 2, 2] + (trac3b[l, 2, 2] - trac3b[l, 0, 2]) * dT7 / dT3
        pradec5b = (ra5, dec5)
        # make tree from radec4
        # search point from radec3 within r=0.001 deg = 3.6"
        res = tree5.query_ball_point(pradec5b, r=0.0005)
        d, ref = tree5.query(pradec5b, distance_upper_bound=0.004)
        # reject number of res > 1 because it has a high possibility to be noise
        if len(res) == 1 and d < 0.001:
            # print(trac3b[l],radec5b[ref])
            tmp4 = np.append(trac3b[l], [radec5b[ref]], axis=0)
            tmp5 = np.append(tmp5, tmp4)
        elif len(res) == 0:
            tmp4c = np.append(tmp4c, trac3b[l], axis=0)
    # 1,2,3,5 detect 4 undetect
    a = int(len(tmp5) / 12)
    if a == 0:
        trac5 = []
    else:
        trac5 = tmp5.reshape(a, 4, 3)
    # 1,2,3 detect 4,5 undetect
    b = int(len(tmp4c) / 3)
    trac5b = tmp4c.reshape(b, 3, 3)
    trac5b = trac5b[1:b]
    
    # predict #4 from #2
    tmp4 = []
    tmp5 = []
    tmp4c = np.empty((2, 3), float)
    num3 = len(trac2b)
    for k in range(num3):
        # predict #4 position
        ra4 = trac2b[k, 1, 1] + (trac2b[k, 1, 1] - trac2b[k, 0, 1]) * dT8 / dT1
        dec4 = trac2b[k, 1, 2] + (trac2b[k, 1, 2] - trac2b[k, 0, 2]) * dT8 / dT1
        pradec4 = (ra4, dec4)
        # make tree from radec4
        # search point from radec4 within r=0.001 deg = 3.6"
        res = tree4.query_ball_point(pradec4, r=0.0005)
        d, ref = tree4.query(pradec4, distance_upper_bound=0.004)
        # reject number of res > 1 because it has a high possibility to be noise
        if len(res) == 1 and d < 0.001:
            # print(trac1[k],radec3[ref])
            tmp4 = np.append(trac2b[k], [radec4b[ref]], axis=0)
            tmp5 = np.append(tmp5, tmp4)
        elif len(res) == 0:
            tmp4c = np.append(tmp4c, trac2b[k], axis=0)
    # 1,2,4 detect 3 undetect
    a = int(len(tmp5) / 9)
    # Revised 2020.2.13
    if a == 0:
        trac6 = []
    else:
        trac6 = tmp5.reshape(a, 3, 3)
    # 1,2 detect 3,4 undetect
    b = int(len(tmp4c) / 2)
    trac6b = tmp4c.reshape(b, 2, 3)
    trac6b = trac6b[1:b]

    # predict #5 from trac6
    tmp4 = []
    tmp5 = []
    tmp4c = np.empty((3, 3), float)
    num3 = len(trac6)
    for k in range(num3):
        # predict #4 position
        ra5 = trac6[k, 2, 1] + (trac6[k, 2, 1] - trac6[k, 0, 1]) * dT6 / dT5
        dec5 = trac6[k, 2, 2] + (trac6[k, 2, 2] - trac6[k, 0, 2]) * dT6 / dT5
        pradec5 = (ra5, dec5)
        # make tree from radec4
        # search point from radec4 within r=0.001 deg = 3.6"
        res = tree5.query_ball_point(pradec5, r=0.0005)
        d, ref = tree5.query(pradec5, distance_upper_bound=0.004)
        # reject number of res > 1 because it has a high possibility to be noise
        if len(res) == 1 and d < 0.001:
            # print(trac1[k],radec3[ref])
            tmp4 = np.append(trac6[k], [radec5b[ref]], axis=0)
            tmp5 = np.append(tmp5, tmp4)
        elif len(res) == 0:
            tmp4c = np.append(tmp4c, trac6[k], axis=0)
    # 1,2,4 5 detect 3 undetect
    # revise 2020.2.3
    if len(tmp5) == 0:
        pass
    else:
        a = int(len(tmp5) / 12)
        trac7 = tmp5.reshape(a, 4, 3)
        # a = int(len(tmp5)/12)
        # trac7 = tmp5.reshape(a,4,3)
    # 1,2 4 detect 3,5 undetect
    b = int(len(tmp4c) / 3)
    trac7b = tmp4c.reshape(b, 3, 3)
    trac7b = trac7b[1:b]

    # predict #5 from trac6b(1,2 detect 3,4 undectc)
    tmp4 = []
    tmp5 = []
    num3 = len(trac6b)
    for k in range(num3):
        # predict #4 position
        ra5 = trac6b[k, 1, 1] + (trac6b[k, 1, 1] - trac6b[k, 0, 1]) * dT9 / dT1
        dec5 = trac6b[k, 1, 2] + (trac6b[k, 1, 2] - trac6b[k, 0, 2]) * dT9 / dT1
        pradec5 = (ra5, dec5)
        # make tree from radec4
        # search point from radec4 within r=0.001 deg = 3.6"
        res = tree5.query_ball_point(pradec5, r=0.0005)
        d, ref = tree5.query(pradec5, distance_upper_bound=0.004)
        # reject number of res > 1 because it has a high possibility to be noise
        if len(res) == 1 and d < 0.001:
            # print(trac1[k],radec3[ref])
            tmp4 = np.append(trac6b[k], [radec5b[ref]], axis=0)
            tmp5 = np.append(tmp5, tmp4)
    # 1,2,5 detect 3 ,4undetect
    a = int(len(tmp5) / 9)
    # Revised 2020.2.13
    if a == 0:
        trac8 = []
    else:
        trac8 = tmp5.reshape(a, 3, 3)

    ######################   tracklet 1-3 and 2 undetected #############################
    trac1b = mktraclet.traclet2(radec1, radec3)

    tmp4 = []
    tmp5 = []
    tmp4d = np.empty((2, 3), float)
    num3 = len(trac1b)
    for k in range(num3):
        # predict #2 position
        ra2 = trac1b[k, 1, 1] - (trac1b[k, 1, 1] - trac1b[k, 0, 1]) * dT2 / dT3
        dec2 = trac1b[k, 1, 2] - (trac1b[k, 1, 2] - trac1b[k, 0, 2]) * dT2 / dT3
        pradec2 = (ra2, dec2)
        # make tree from radec4
        # search point from radec4 within r=0.001 deg = 3.6"
        res = tree2.query_ball_point(pradec2, r=0.0005)
        d, ref = tree2.query(pradec2, distance_upper_bound=0.004)
        # reject number of res > 1 because it has a high possibility to be noise
        if len(res) == 1 and d < 0.001:
            # print(trac1[k],radec3[ref])
            tmp4 = np.append(trac1b[k], [radec2b[ref]], axis=0)
            tmp5 = np.append(tmp5, tmp4)
        elif len(res) == 0:
            tmp4d = np.append(tmp4d, trac1b[k], axis=0)
    # 1,3,2 detect
    a = int(len(tmp5) / 9)
    trac9 = tmp5.reshape(a, 3, 3)
    # 1,3 detect 2 undetect
    b = int(len(tmp4d) / 2)
    trac9b = tmp4d.reshape(b, 2, 3)
    trac9b = trac9b[1:b]

    # predict #4 from trac9b
    tmp4 = []
    tmp5 = []
    tmp4c = np.empty((2, 3), float)
    num3 = len(trac9b)
    for k in range(num3):
        # predict #4 position
        # ra4  = trac9b[k,1,1] + (trac9b[k,1,1] - trac9b[k,0,1])*dT8/dT1
        # dec4 = trac9b[k,1,2] + (trac9b[k,1,2] - trac9b[k,0,2])*dT8/dT1
        # revised 2020.5.5
        ra4 = trac9b[k, 1, 1] + (trac9b[k, 1, 1] - trac9b[k, 0, 1]) * dT4 / dT3
        dec4 = trac9b[k, 1, 2] + (trac9b[k, 1, 2] - trac9b[k, 0, 2]) * dT4 / dT3
        pradec4 = (ra4, dec4)
        # make tree from radec4
        # search point from radec4 within r=0.001 deg = 3.6"
        res = tree4.query_ball_point(pradec4, r=0.0005)
        d, ref = tree4.query(pradec4, distance_upper_bound=0.004)
        # reject number of res > 1 because it has a high possibility to be noise
        if len(res) == 1 and d < 0.001:
            # print(trac1[k],radec3[ref])
            tmp4 = np.append(trac9b[k], [radec4b[ref]], axis=0)
            tmp5 = np.append(tmp5, tmp4)
        elif len(res) == 0:
            tmp4c = np.append(tmp4c, trac9b[k], axis=0)
    # 1,3,4 detect 2 undetect
    a = int(len(tmp5) / 9)
    # Revised 2020.2.13
    if a == 0:
        trac10 = []
    else:
        trac10 = tmp5.reshape(a, 3, 3)
    # 1,3 detect 2,4 undetect
    b = int(len(tmp4c) / 2)
    trac10b = tmp4c.reshape(b, 2, 3)
    trac10b = trac10b[1:b]

    # predict #5 from trac10
    tmp4 = []
    tmp5 = []
    tmp4c = np.empty((3, 3), float)
    num3 = len(trac10)
    for k in range(num3):
        # predict #5 position
        ra5 = trac10[k, 2, 1] + (trac10[k, 2, 1] - trac10[k, 0, 1]) * dT6 / dT5
        dec5 = trac10[k, 2, 2] + (trac10[k, 2, 2] - trac10[k, 0, 2]) * dT6 / dT5
        pradec5 = (ra5, dec5)
        # make tree from radec5
        # search point from radec5 within r=0.001 deg = 3.6"
        res = tree5.query_ball_point(pradec5, r=0.0005)
        d, ref = tree5.query(pradec5, distance_upper_bound=0.004)
        # reject number of res > 1 because it has a high possibility to be noise
        if len(res) == 1 and d < 0.001:
            # print(trac1[k],radec3[ref])
            tmp4 = np.append(trac10[k], [radec5b[ref]], axis=0)
            tmp5 = np.append(tmp5, tmp4)
        elif len(res) == 0:
            tmp4c = np.append(tmp4c, trac10[k], axis=0)
    # 1,3,4 5 detect 2 undetect
    a = int(len(tmp5) / 12)
    if a == 0:
        trac11 = []
    else:
        trac11 = tmp5.reshape(a, 4, 3)
    # 1,3,4 detect 2,5 undetect
    b = int(len(tmp4c) / 3)
    trac11b = tmp4c.reshape(b, 3, 3)
    trac11b = trac11b[1:b]

    # predict #5 from trac10b
    tmp4 = []
    tmp5 = []
    tmp4c = np.empty((2, 3), float)
    num3 = len(trac10b)
    for k in range(num3):
        # predict #5 position
        ra5 = trac10b[k, 1, 1] + (trac10b[k, 1, 1] - trac10b[k, 0, 1]) * dT7 / dT3
        dec5 = trac10b[k, 1, 2] + (trac10b[k, 1, 2] - trac10b[k, 0, 2]) * dT7 / dT3
        pradec5 = (ra5, dec5)
        # make tree from radec5
        # search point from radec5 within r=0.001 deg = 3.6"
        res = tree5.query_ball_point(pradec5, r=0.0005)
        d, ref = tree5.query(pradec5, distance_upper_bound=0.004)
        # reject number of res > 1 because it has a high possibility to be noise
        if len(res) == 1 and d < 0.001:
            # print(trac1[k],radec3[ref])
            tmp4 = np.append(trac10b[k], [radec5b[ref]], axis=0)
            tmp5 = np.append(tmp5, tmp4)
        elif len(res) == 0:
            tmp4c = np.append(tmp4c, trac10b[k], axis=0)
    # 1,3,5 detect 2,4 undetect
    a = int(len(tmp5) / 9)
    if a == 0:
        trac12 = []
    else:
        trac12 = tmp5.reshape(a, 3, 3)
    # 1,3 detect 2,4,5 undetect
    b = int(len(tmp4c) / 2)
    trac12b = tmp4c.reshape(b, 2, 3)
    trac12b = trac12b[1:b]

    ######################   tracklet 2-3 and 1 undetected #############################
    trac1c = mktraclet.traclet3(radec2, radec3)
    
    tmp4 = []
    tmp5 = []
    tmp4d = np.empty((2, 3), float)
    num3 = len(trac1c)
    for k in range(num3):
        # predict #1 position
        ra1 = trac1c[k, 0, 1] - (trac1c[k, 1, 1] - trac1c[k, 0, 1]) * dT1 / dT2
        dec1 = trac1c[k, 0, 2] - (trac1c[k, 1, 2] - trac1c[k, 0, 2]) * dT1 / dT2
        pradec1 = (ra1, dec1)
        # make tree from radec1
        # search point from radec1 within r=0.001 deg = 3.6"
        res = tree1.query_ball_point(pradec1, r=0.0005)
        d, ref = tree1.query(pradec1, distance_upper_bound=0.004)
        # reject number of res > 1 because it has a high possibility to be noise
        if len(res) == 1 and d < 0.001:
            # print(trac1[k],radec3[ref])
            tmp4 = np.append(trac1c[k], [radec1b[ref]], axis=0)
            tmp5 = np.append(tmp5, tmp4)
        elif len(res) == 0:
            tmp4d = np.append(tmp4d, trac1c[k], axis=0)
    # 2,3,1 detect
    a = int(len(tmp5) / 9)
    if a == 0:
        trac13 = []
    else:
        trac13 = tmp5.reshape(a, 3, 3)
    # 2,3 detect 1 undetect
    b = int(len(tmp4d) / 2)
    trac13b = tmp4d.reshape(b, 2, 3)
    trac13b = trac13b[1:b]

    # predict #4 from trac13b
    tmp4 = []
    tmp5 = []
    tmp4c = np.empty((2, 3), float)
    num3 = len(trac13b)
    for k in range(num3):
        # predict #4 position
        ra4 = trac13b[k, 1, 1] + (trac13b[k, 1, 1] - trac13b[k, 0, 1]) * dT4 / dT2
        dec4 = trac13b[k, 1, 2] + (trac13b[k, 1, 2] - trac13b[k, 0, 2]) * dT4 / dT2
        pradec4 = (ra4, dec4)
        # make tree from radec5
        # search point from radec4 within r=0.001 deg = 3.6"
        res = tree4.query_ball_point(pradec4, r=0.0005)
        d, ref = tree4.query(pradec4, distance_upper_bound=0.004)
        # reject number of res > 1 because it has a high possibility to be noise
        if len(res) == 1 and d < 0.001:
            # print(trac1[k],radec3[ref])
            tmp4 = np.append(trac13b[k], [radec4b[ref]], axis=0)
            tmp5 = np.append(tmp5, tmp4)
        elif len(res) == 0:
            tmp4c = np.append(tmp4c, trac13b[k], axis=0)
    # 2,3,4 detect 1 undetect
    a = int(len(tmp5) / 9)
    if a == 0:
        trac14 = []
    else:
        trac14 = tmp5.reshape(a, 3, 3)
    # 2,3 detect 1,4 undetect
    b = int(len(tmp4c) / 2)
    trac14b = tmp4c.reshape(b, 2, 3)
    trac14b = trac14b[1:b]

    # predict #5 from trac14
    tmp4 = []
    tmp5 = []
    tmp4c = np.empty((3, 3), float)
    num3 = len(trac14)
    for k in range(num3):
        # predict #5 position
        ra5 = trac14[k, 2, 1] + (trac14[k, 2, 1] - trac14[k, 0, 1]) * dT6 / dT8
        dec5 = trac14[k, 2, 2] + (trac14[k, 2, 2] - trac14[k, 0, 2]) * dT6 / dT8
        pradec5 = (ra5, dec5)
        # make tree from radec5
        # search point from radec4 within r=0.001 deg = 3.6"
        res = tree5.query_ball_point(pradec5, r=0.0005)
        d, ref = tree5.query(pradec5, distance_upper_bound=0.004)
        # reject number of res > 1 because it has a high possibility to be noise
        if len(res) == 1 and d < 0.001:
            # print(trac1[k],radec3[ref])
            tmp4 = np.append(trac14[k], [radec5b[ref]], axis=0)
            tmp5 = np.append(tmp5, tmp4)
        elif len(res) == 0:
            tmp4c = np.append(tmp4c, trac14[k], axis=0)
    # 2,3,4 5 detect 1 undetect
    a = int(len(tmp5) / 12)
    if a == 0:
        trac15 = []
    else:
        trac15 = tmp5.reshape(a, 4, 3)
    # 2,3 4 detect 1,5 undetect
    b = int(len(tmp4c) / 3)
    trac15b = tmp4c.reshape(b, 3, 3)
    trac15b = trac15b[1:b]

    # predict #5 from trac14b
    tmp4 = []
    tmp5 = []
    tmp4c = np.empty((2, 3), float)
    num3 = len(trac14)
    for k in range(num3):
        # predict #5 position
        ra5 = trac14b[k, 1, 1] + (trac14b[k, 1, 1] - trac14b[k, 0, 1]) * dT7 / dT2
        dec5 = trac14b[k, 1, 2] + (trac14b[k, 1, 2] - trac14b[k, 0, 2]) * dT7 / dT2
        pradec5 = (ra5, dec5)
        # make tree from radec5
        # search point from radec4 within r=0.001 deg = 3.6"
        res = tree5.query_ball_point(pradec5, r=0.0005)
        d, ref = tree5.query(pradec5, distance_upper_bound=0.004)
        # reject number of res > 1 because it has a high possibility to be noise
        if len(res) == 1 and d < 0.001:
            # print(trac1[k],radec3[ref])
            tmp4 = np.append(trac14b[k], [radec5b[ref]], axis=0)
            tmp5 = np.append(tmp5, tmp4)
        elif len(res) == 0:
            tmp4c = np.append(tmp4c, trac14b[k], axis=0)
    # 2,3,5 detect 1,4 undetect
    a = int(len(tmp5) / 9)
    if a == 0:
        trac16 = []
    else:
        trac16 = tmp5.reshape(a, 3, 3)
    # 2,3detect 1,4,5 undetect
    b = int(len(tmp4c) / 2)
    trac16b = tmp4c.reshape(b, 2, 3)
    trac16b = trac16b[1:b]
    
    ######################   tracklet 1-4 and 2,3 undetected #########################
    trac1d = mktraclet.traclet4(radec1, radec4)
    
    # 3 from trac1d(1,4 detect)
    tmp4 = []
    tmp5 = []
    tmp4d = np.empty((2, 3), float)
    num3 = len(trac1d)
    for k in range(num3):
        # predict #3 position
        ra3 = trac1d[k, 1, 1] - (trac1d[k, 1, 1] - trac1d[k, 0, 1]) * dT4 / dT5
        dec3 = trac1d[k, 1, 2] - (trac1d[k, 1, 2] - trac1d[k, 0, 2]) * dT4 / dT5
        pradec3 = (ra3, dec3)
        # make tree from radec1
        # search point from radec1 within r=0.001 deg = 3.6"
        res = tree3.query_ball_point(pradec3, r=0.0005)
        d, ref = tree3.query(pradec3, distance_upper_bound=0.004)
        # reject number of res > 1 because it has a high possibility to be noise
        if len(res) == 1 and d < 0.001:
            # print(trac1[k],radec3[ref])
            tmp4 = np.append(trac1d[k], [radec3b[ref]], axis=0)
            tmp5 = np.append(tmp5, tmp4)
        elif len(res) == 0:
            tmp4d = np.append(tmp4d, trac1d[k], axis=0)
    # 1,4,3 detect
    a = int(len(tmp5) / 9)
    if a == 0:
        trac17 = []
    else:
        trac17 = tmp5.reshape(a, 3, 3)
    # 1,4 detect 3 undetect
    b = int(len(tmp4d) / 2)
    trac17b = tmp4d.reshape(b, 2, 3)
    trac17b = trac17b[1:b]

    # predict #2 from trac17b
    tmp4 = []
    tmp5 = []
    tmp4d = np.empty((2, 3), float)
    num3 = len(trac17b)
    for k in range(num3):
        # predict #2 position
        ra2 = trac1d[k, 1, 1] - (trac1d[k, 1, 1] - trac1d[k, 0, 1]) * dT8 / dT5
        dec2 = trac1d[k, 1, 2] - (trac1d[k, 1, 2] - trac1d[k, 0, 2]) * dT8 / dT5
        pradec2 = (ra2, dec2)
        # make tree from radec1
        # search point from radec1 within r=0.001 deg = 3.6"
        res = tree2.query_ball_point(pradec2, r=0.0005)
        d, ref = tree2.query(pradec2, distance_upper_bound=0.004)
        # reject number of res > 1 because it has a high possibility to be noise
        if len(res) == 1 and d < 0.001:
            # print(trac1[k],radec3[ref])
            tmp4 = np.append(trac17b[k], [radec2b[ref]], axis=0)
            tmp5 = np.append(tmp5, tmp4)
        elif len(res) == 0:
            tmp4d = np.append(tmp4d, trac17b[k], axis=0)
    # 1,4,2 detect 3 undetect
    a = int(len(tmp5) / 9)
    if a == 0:
        trac18 = []
    else:
        trac18 = tmp5.reshape(a, 3, 3)
        # 1,4 detect 2,3 undetect
        b = int(len(tmp4d) / 2)
        trac18b = tmp4d.reshape(b, 2, 3)
        trac18b = trac18b[1:b]

    # predict #5 from trac18b
    tmp4 = []
    tmp5 = []
    tmp4d = np.empty((2, 3), float)
    num3 = len(trac18b)
    for k in range(num3):
        # predict #5 position
        ra5 = trac1d[k, 1, 1] + (trac1d[k, 1, 1] - trac1d[k, 0, 1]) * dT6 / dT5
        dec5 = trac1d[k, 1, 2] + (trac1d[k, 1, 2] - trac1d[k, 0, 2]) * dT6 / dT5
        pradec5 = (ra5, dec5)
        # make tree from radec1
        # search point from radec1 within r=0.001 deg = 3.6"
        res = tree5.query_ball_point(pradec5, r=0.0005)
        d, ref = tree5.query(pradec5, distance_upper_bound=0.004)
        # reject number of res > 1 because it has a high possibility to be noise
        if len(res) == 1 and d < 0.001:
            # print(trac1[k],radec3[ref])
            tmp4 = np.append(trac18b[k], [radec5b[ref]], axis=0)
            tmp5 = np.append(tmp5, tmp4)
        elif len(res) == 0:
            tmp4d = np.append(tmp4d, trac18b[k], axis=0)
    # 1,4,5 detect 2,3 undetect
    a = int(len(tmp5) / 9)
    if a == 0:
        trac19 = []
    else:
        trac19 = tmp5.reshape(a, 3, 3)
    # 1,4 detect 2,3,5 undetect
    b = int(len(tmp4d) / 2)
    trac19b = tmp4d.reshape(b, 2, 3)
    trac19b = trac19b[1:b]

    ######################   tracklet 2-4 and 1,3 undetected #############################
    trac1e = mktraclet.traclet5(radec2, radec4)

    # 3 from trac1e(2,4 detect)
    tmp4 = []
    tmp5 = []
    tmp4d = np.empty((2, 3), float)
    num3 = len(trac1e)
    for k in range(num3):
        # predict #3 position
        ra3 = trac1e[k, 1, 1] - (trac1e[k, 1, 1] - trac1e[k, 0, 1]) * dT4 / dT8
        dec3 = trac1e[k, 1, 2] - (trac1e[k, 1, 2] - trac1e[k, 0, 2]) * dT4 / dT8
        pradec3 = (ra3, dec3)
        # make tree from radec1
        # search point from radec1 within r=0.001 deg = 3.6"
        res = tree3.query_ball_point(pradec3, r=0.0005)
        d, ref = tree3.query(pradec3, distance_upper_bound=0.004)
        # reject number of res > 1 because it has a high possibility to be noise
        if len(res) == 1 and d < 0.001:
            # print(trac1[k],radec3[ref])
            tmp4 = np.append(trac1e[k], [radec3b[ref]], axis=0)
            tmp5 = np.append(tmp5, tmp4)
        elif len(res) == 0:
            tmp4d = np.append(tmp4d, trac1e[k], axis=0)
    # 2,4,3 detect
    a = int(len(tmp5) / 9)
    if a == 0:
        trac20 = []
    else:
        trac20 = tmp5.reshape(a, 3, 3)
    # 2,4 detect 3 undetect
    b = int(len(tmp4d) / 2)
    trac20b = tmp4d.reshape(b, 2, 3)
    # trac20b = trac17b[1:b]
    trac20b = trac20b[1:b]  # 2021/5/24 K.S. modify

    # predict #1 from trac20b
    tmp4 = []
    tmp5 = []
    tmp4d = np.empty((2, 3), float)
    num3 = len(trac20b)
    for k in range(num3):
        # predict #1 position
        ra1 = trac20b[k, 1, 1] - (trac20b[k, 1, 1] - trac20b[k, 0, 1]) * dT5 / dT8
        dec1 = trac20b[k, 1, 2] - (trac20b[k, 1, 2] - trac20b[k, 0, 2]) * dT5 / dT8
        pradec1 = (ra1, dec1)
        # make tree from radec1
        # search point from radec1 within r=0.001 deg = 3.6"
        res = tree1.query_ball_point(pradec1, r=0.0005)
        d, ref = tree1.query(pradec1, distance_upper_bound=0.004)
        # reject number of res > 1 because it has a high possibility to be noise
        if len(res) == 1 and d < 0.001:
            # print(trac1[k],radec3[ref])
            tmp4 = np.append(trac20b[k], [radec1b[ref]], axis=0)
            tmp5 = np.append(tmp5, tmp4)
        elif len(res) == 0:
            tmp4d = np.append(tmp4d, trac20b[k], axis=0)
    # 2,4,1 detect 3 undetect
    a = int(len(tmp5) / 9)
    if a == 0:
        trac21 = []
    else:
        trac21 = tmp5.reshape(a, 3, 3)
    # 2,4 detect 1,3 undetect
    b = int(len(tmp4d) / 2)
    trac21b = tmp4d.reshape(b, 2, 3)
    trac21b = trac21b[1:b]

    # predict #5 from trac21b
    tmp4 = []
    tmp5 = []
    tmp4d = np.empty((2, 3), float)
    num3 = len(trac21b)
    for k in range(num3):
        # predict #5 position
        ra5 = trac21b[k, 1, 1] + (trac21b[k, 1, 1] - trac21b[k, 0, 1]) * dT6 / dT8
        dec5 = trac21b[k, 1, 2] + (trac21b[k, 1, 2] - trac21b[k, 0, 2]) * dT6 / dT8
        pradec5 = (ra5, dec5)
        # make tree from radec1
        # search point from radec1 within r=0.001 deg = 3.6"
        res = tree5.query_ball_point(pradec5, r=0.0005)
        d, ref = tree5.query(pradec5, distance_upper_bound=0.004)
        # reject number of res > 1 because it has a high possibility to be noise
        if len(res) == 1 and d < 0.001:
            # print(trac1[k],radec3[ref])
            tmp4 = np.append(trac21b[k], [radec5b[ref]], axis=0)
            tmp5 = np.append(tmp5, tmp4)
        elif len(res) == 0:
            tmp4d = np.append(tmp4d, trac21b[k], axis=0)
    # 2,4,5 detect 1,3 undetect
    # revised 2020.2.3
    if len(tmp5) == 0:
        pass
    else:
        a = int(len(tmp5) / 9)
        trac22 = tmp5.reshape(a, 3, 3)
        # a = int(len(tmp5)/9)
        # trac22 = tmp5.reshape(a,3,3)
    # 2,4 detect 1,3,5 undetect
    b = int(len(tmp4d) / 2)
    trac22b = tmp4d.reshape(b, 2, 3)
    trac22b = trac22b[1:b]
    
    ######################   tracklet 3-4 and 1,2 undetected #############################
    trac1f = mktraclet.traclet6(radec3, radec4)

    tmp4 = []
    tmp5 = []
    tmp4d = np.empty((2, 3), float)
    num3 = len(trac1f)
    for k in range(num3):
        # predict #2 position
        ra2 = trac1f[k, 1, 1] - (trac1f[k, 1, 1] - trac1f[k, 0, 1]) * dT2 / dT4
        dec2 = trac1f[k, 1, 2] - (trac1f[k, 1, 2] - trac1f[k, 0, 2]) * dT2 / dT4
        pradec2 = (ra2, dec2)
        # search point from radec1 within r=0.001 deg = 3.6"
        res = tree2.query_ball_point(pradec2, r=0.0005)
        d, ref = tree2.query(pradec2, distance_upper_bound=0.004)
        # reject number of res > 1 because it has a high possibility to be noise
        if len(res) == 1 and d < 0.001:
            # print(trac1[k],radec3[ref])
            tmp4 = np.append(trac1f[k], [radec2b[ref]], axis=0)
            tmp5 = np.append(tmp5, tmp4)
        elif len(res) == 0:
            tmp4d = np.append(tmp4d, trac1f[k], axis=0)
    # 3,4,2 detect
    a = int(len(tmp5) / 9)
    if a == 0:
        trac23 = []
    else:
        trac23 = tmp5.reshape(a, 3, 3)
    # 3,4 detect 2 undetect
    b = int(len(tmp4d) / 2)
    trac23b = tmp4d.reshape(b, 2, 3)
    trac23b = trac23b[1:b]

    # predict #1 from trac23b
    tmp4 = []
    tmp5 = []
    tmp4d = np.empty((2, 3), float)
    num3 = len(trac23b)
    for k in range(num3):
        # predict #1 position
        ra1 = trac23b[k, 1, 1] - (trac23b[k, 1, 1] - trac23b[k, 0, 1]) * dT3 / dT4
        dec1 = trac23b[k, 1, 2] - (trac23b[k, 1, 2] - trac23b[k, 0, 2]) * dT3 / dT4
        pradec1 = (ra1, dec1)
        # make tree from radec1
        # search point from radec1 within r=0.001 deg = 3.6"
        res = tree1.query_ball_point(pradec1, r=0.0005)
        d, ref = tree1.query(pradec1, distance_upper_bound=0.004)
        # reject number of res > 1 because it has a high possibility to be noise
        if len(res) == 1 and d < 0.001:
            # print(trac1[k],radec3[ref])
            tmp4 = np.append(trac23b[k], [radec1b[ref]], axis=0)
            tmp5 = np.append(tmp5, tmp4)
        elif len(res) == 0:
            tmp4d = np.append(tmp4d, trac23b[k], axis=0)
    # 3,4,1 detect 2 undetect
    a = int(len(tmp5) / 9)
    if a == 0:
        trac24 = []
    else:
        trac24 = tmp5.reshape(a, 3, 3)
    # 3,4 detect 1,2 undetect
    b = int(len(tmp4d) / 2)
    trac25b = tmp4d.reshape(b, 2, 3)
    trac25b = trac25b[1:b]

    # predict #5 from trac25b
    tmp4 = []
    tmp5 = []
    tmp4d = np.empty((2, 3), float)
    num3 = len(trac25b)
    for k in range(num3):
        # predict #5 position
        ra5 = trac25b[k, 1, 1] + (trac25b[k, 1, 1] - trac25b[k, 0, 1]) * dT6 / dT4
        dec5 = trac25b[k, 1, 2] + (trac25b[k, 1, 2] - trac25b[k, 0, 2]) * dT6 / dT4
        pradec5 = (ra5, dec5)
        # make tree from radec1
        # search point from radec1 within r=0.001 deg = 3.6"
        res = tree5.query_ball_point(pradec5, r=0.0005)
        d, ref = tree5.query(pradec5, distance_upper_bound=0.004)
        # reject number of res > 1 because it has a high possibility to be noise
        if len(res) == 1 and d < 0.001:
            # print(trac1[k],radec3[ref])
            tmp4 = np.append(trac25b[k], [radec5b[ref]], axis=0)
            tmp5 = np.append(tmp5, tmp4)
        elif len(res) == 0:
            tmp4d = np.append(tmp4d, trac25b[k], axis=0)
    # 3,4,5 detect 1,2 undetect
    a = int(len(tmp5) / 9)
    if a == 0:
        trac26 = []
    else:
        trac26 = tmp5.reshape(a, 3, 3)
    # 3,4 detect 1,2,5 undetect
    b = int(len(tmp4d) / 2)
    trac26b = tmp4d.reshape(b, 2, 3)
    trac26b = trac26b[1:b]

    
    ###################  summarize 4 times detection lists #################
    # revised 2020.2.4
    trac27 = []
    #######
    if len(trac4b) > 0 and len(trac5) > 0 and len(trac7) > 0 and len(trac11) > 0 and len(trac15) > 0:
        trac27 = np.vstack([trac4b, trac5, trac7, trac11, trac15])
    elif len(trac4b) == 0 and len(trac5) > 0 and len(trac7) > 0 and len(trac11) > 0 and len(trac15) > 0:
        trac27 = np.vstack([trac5, trac7, trac11, trac15])
    elif len(trac4b) > 0 and len(trac5) == 0 and len(trac7) > 0 and len(trac11) > 0 and len(trac15) > 0:
        trac27 = np.vstack([trac4b, trac7, trac11, trac15])
    elif len(trac4b) > 0 and len(trac5) > 0 and len(trac7) == 0 and len(trac11) > 0 and len(trac15) > 0:
        trac27 = np.vstack([trac4b, trac5, trac11, trac15])
    elif len(trac4b) > 0 and len(trac5) > 0 and len(trac7) > 0 and len(trac11) == 0 and len(trac15) > 0:
        trac27 = np.vstack([trac4b, trac5, trac7, trac15])
    elif len(trac4b) > 0 and len(trac5) > 0 and len(trac7) > 0 and len(trac11) > 0 and len(trac15) == 0:
        trac27 = np.vstack([trac4b, trac5, trac7, trac11])

    ########################   photometry  ################################
    from photutils import CircularAperture
    from photutils import CircularAnnulus
    
    from astropy import units as u
    from photutils import aperture_photometry

    #
    result = []
    xpix2 = 30
    ypix2 = 30
    # wcs
    w1 = wcs.WCS(scidata1[0].header)
    # i: id number #j:frame number # 0:time 1:ra 2:dec
    
    ##############   5 times detect trac4(1,2,3,4,5) ##############
    if len(trac4) == 0:
        # pass
        i = 0  # 2021/5/24 K.S. modify
    else:
        for i in range(trac4.shape[0]):
            for j in range(trac4.shape[1]):
                xypix = w1.wcs_world2pix(trac4[i, j, 1], trac4[i, j, 2], 1)

                # param of aperture
                f = 1  # factor 6: semimajor-axis no 3 bai
                # w = width * f
                w = 6
                wa = w * u.pix
                w_in = (w + 2) * u.pix
                w_out = (w + 8) * u.pix

                # scidata is y,x array
                # position = (ypix2,xpix2)
                position = (xypix[0], xypix[1])
                # aperture phot
                ap = CircularAperture(position, wa.value)
                sap = CircularAnnulus(position, w_in.value, w_out.value)

                rawflux_table = aperture_photometry(scidata[j], ap, method='subpixel', subpixels=5)
                bkgflux_table = aperture_photometry(scidata[j], sap, method='subpixel', subpixels=5)
                # 2020.11.25 revised
                bkg_mean = bkgflux_table['aperture_sum'] / sap.area
                bkg_sum = bkg_mean * ap.area
                final_sum = nbin[j]*nbin[j]*(rawflux_table['aperture_sum'] - bkg_sum) #K.S. modified 2022/5/3
                #final_sum = 4.0 * (rawflux_table['aperture_sum'] - bkg_sum)
                if final_sum <= 0:
                    final_sum = 1
                mag = np.round(zm[j] - 2.5 * np.log10(final_sum), decimals=3)
                # error
                sigma_ron =  4.5*nbin[j]*nbin[j] # read out noise of HSC /nobining :4.5e S.U modified 2022/5/4
                gain = 3.0 / nbin[j] # gain of HSC/nobining :3.0  S.U modified 2022/5/4
                S_star = gain * final_sum
                effective_area = ap.area * ((1 + ap.area) / sap.area)
                # N2 = S_star + effective_area * (gain * bkg_mean + sigma_ron)
                N2 = S_star
                N = np.sqrt(N2)  # Noise in electron
                SNR = S_star / N
                # error in magnitude m_err = 1.0857/SNR
                # Noise in ADU
                mage = np.round(1.0857 / SNR, decimals=3)
                result.append([i, trac4[i, j, 0], trac4[i, j, 1], trac4[i, j, 2], mag, mage, xypix[0], xypix[1], fil1])

    ################# 4 times detection   ###########################
    # revised 2020.2.5 in the case of nothing 4 times detection
    if len(trac27) == 0:
        np.savetxt("listb2.txt", result, fmt="%d %.9f %.7f %.7f %.3f %.3f %.2f %.2f %s")
    else:
        for l in range(trac27.shape[0]):
            for m in range(trac27.shape[1]):
                xypix = w1.wcs_world2pix(trac27[l, m, 1], trac27[l, m, 2], 1)

                # clip the asteroid region #revised 2019.11.8
                if jd1 == trac27[l, m, 0]:
                    # tmp = scidata[0][tmpy:tmpy2,tmpx:tmpx2]
                    tmp = scidata[0]
                if jd2 == trac27[l, m, 0]:
                    # tmp = scidata[1][tmpy:tmpy2,tmpx:tmpx2]
                    tmp = scidata[1]
                if jd3 == trac27[l, m, 0]:
                    # tmp = scidata[2][tmpy:tmpy2,tmpx:tmpx2]
                    tmp = scidata[2]
                if jd4 == trac27[l, m, 0]:
                    # tmp = scidata[3][tmpy:tmpy2,tmpx:tmpx2]
                    tmp = scidata[3]
                if jd5 == trac27[l, m, 0]:
                    # tmp = scidata[4][tmpy:tmpy2,tmpx:tmpx2]
                    tmp = scidata[4]
                    
                # mean,median,std = sigma_clipped_stats(tmp,sigma=3.0,maxiters=5)
                # tmp-=median

                # cat = data_properties(tmp)
                # columns =['xcentroid','ycentroid','semimajor_axis_sigma','semiminor_axis_sigma','orientation','elongation']

                # param of aperture
                f = 1  # factor 6: semimajor-axis no 3 bai
                # w = width * f
                w = 6
                wa = w * u.pix
                w_in = (w + 2) * u.pix
                w_out = (w + 8) * u.pix

                # scidata is y,x array
                position = (xypix[0], xypix[1])
                # position = (ypix2,xpix2)
            
                # revised 2020.2.20
                # position = (xypix[1],xypix[0])
                # aperture phot
                ap = CircularAperture(position, wa.value)
                sap = CircularAnnulus(position, w_in.value, w_out.value)

                rawflux_table = aperture_photometry(tmp, ap, method='subpixel', subpixels=5)
                bkgflux_table = aperture_photometry(tmp, sap, method='subpixel', subpixels=5)
                # print(bkgflux_table['aperture_sum'],sap.area())
            
                # 2020.11.25 revised
                bkg_mean = bkgflux_table['aperture_sum'] / sap.area
                # bkg_mean = 10
                bkg_sum = bkg_mean * ap.area
                final_sum = nbin[m]*nbin[m]*(rawflux_table['aperture_sum'] - bkg_sum) # K.S. modified 2022/5/3
                # final_sum = 4.0 * (rawflux_table['aperture_sum'] - bkg_sum)
                # final_sum = 4.0*(rawflux_table['aperture_sum'])
                # bug edit 2019.11.7
                if final_sum <= 0:
                    final_sum = 1
                # mag = np.round(zm[j] - 2.5*np.log10(final_sum),decimals=3)
                mag = np.round(zm[m] - 2.5 * np.log10(final_sum), decimals=3)  # 2021/5/24 K.S. modify
                # error
                sigma_ron =  4.5*nbin[m]*nbin[m] # read out noise of HSC /nobining :4.5e  S.U modified 2022/5/4
                gain = 3.0 / nbin[m] # gain of HSC/nobining :3.0  S.U modified 2022/5/4
                S_star = gain * final_sum
                effective_area = ap.area * ((1 + ap.area) / sap.area)
                # N2 = S_star + effective_area * (gain * bkg_mean + sigma_ron)
                N2 = S_star
                N = np.sqrt(N2)  # Noise in electron
                SNR = S_star / N
                # error in magnitude m_err = 1.0857/SNR
                # Noise in ADU
                mage = np.round(1.0857 / SNR, decimals=3)
                result.append([i + 1 + l, trac27[l, m, 0], trac27[l, m, 1], trac27[l, m, 2], mag, mage, xypix[0], xypix[1], fil1])

        # result2 = np.array(result)
        result2 = np.array(result, dtype='object')  # revised by N.M 2020.12.14
        np.savetxt("listb2.txt", result2, fmt="%d %.9f %.7f %.7f %.3f %.3f %.2f %.2f %s")

    end = time.time()
    elapsed_time = end - start
    print(elapsed_time)


except FileNotFoundError:
    print("Some previous files are not found in astsearch1M2.py!")
    print(traceback.format_exc())
    error = 1
    errorReason = 54

except Exception:
    print("Some errors occur in astsearch1M2.py!")
    print(traceback.format_exc())
    error = 1
    errorReason = 55

else:
    error = 0
    errorReason = 54

finally:
    errorFile = open("error.txt","a")
    errorFile.write("{0:d} {1:d} 503 \n".format(error,errorReason))
    errorFile.close()
