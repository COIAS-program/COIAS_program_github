#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#cython: boundscheck=False
import os
import numpy as np
#cimport numpy as np
#cimport cython
import re
import time
from astropy.io import fits,ascii
from astropy.wcs import wcs
import scipy.spatial as ss
    #read catalog
    
import glob
    #from makedata6 import makedata6
    #from deldaburi2 import deldaburi2
    
    #multiprocessing
from multiprocessing import Pool
from multiprocessing import Process

start = time.time()

#input all point source after find.sh
text_fnames1 = ascii.read('warp1_bin.dat')
text_fnames2 = ascii.read('warp2_bin.dat')
text_fnames3 = ascii.read('warp3_bin.dat')
text_fnames4 = ascii.read('warp4_bin.dat')
text_fnames5 = ascii.read('warp5_bin.dat')


#read scidata
scidata1 = fits.open('warp1_bin.fits')
scidata2 = fits.open('warp2_bin.fits')
scidata3 = fits.open('warp3_bin.fits')
scidata4 = fits.open('warp4_bin.fits')
scidata5 = fits.open('warp5_bin.fits')


#time information & filter
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


#zero magnitude
zm1 = scidata1[0].header['Z_P']
zm2 = scidata2[0].header['Z_P']
zm3 = scidata3[0].header['Z_P']
zm4 = scidata4[0].header['Z_P']
zm5 = scidata5[0].header['Z_P']
zm = [zm1,zm2,zm3,zm4,zm5]

#X,Y pix
xpix = scidata1[0].header['NAXIS1']
ypix = scidata1[0].header['NAXIS2']

#scidata
scidata = [scidata1[0].data,scidata2[0].data,scidata3[0].data,scidata4[0].data,scidata5[0].data]


#x,y to wcs because warp image is same wcs info
w1 = wcs.WCS(scidata1[0].header)

#t,x,y
xy1 = np.array([text_fnames1['X_IMAGE'],text_fnames1['Y_IMAGE']])   
xy1 = xy1.T
radec1 = w1.wcs_pix2world(xy1,1)
gyou = len(radec1)
tt1 = np.zeros(gyou) + jd1
radec1b = np.c_[tt1,radec1]

xy2 = np.array([text_fnames2['X_IMAGE'],text_fnames2['Y_IMAGE']])   
xy2 = xy2.T
radec2 = w1.wcs_pix2world(xy2,1)
gyou = len(radec2)
tt1 = np.zeros(gyou) + jd2
radec2b = np.c_[tt1,radec2]

xy3 = np.array([text_fnames3['X_IMAGE'],text_fnames3['Y_IMAGE']])   
xy3 = xy3.T
radec3 = w1.wcs_pix2world(xy3,1)
gyou = len(radec3)
tt1 = np.zeros(gyou) + jd3
radec3b = np.c_[tt1,radec3]

xy4 = np.array([text_fnames4['X_IMAGE'],text_fnames4['Y_IMAGE']])   
xy4 = xy4.T
radec4 = w1.wcs_pix2world(xy4,1)
gyou = len(radec4)
tt1 = np.zeros(gyou) + jd4
radec4b = np.c_[tt1,radec4]

xy5 = np.array([text_fnames5['X_IMAGE'],text_fnames5['Y_IMAGE']])   
xy5 = xy5.T
radec5 = w1.wcs_pix2world(xy5,1)
gyou = len(radec5)
tt1 = np.zeros(gyou) + jd5
radec5b = np.c_[tt1,radec5]


#prepare delta T
dT1 = (jd2 - jd1)*1440
dT2 = (jd3 - jd2)*1440
dT3 = (jd3 - jd1)*1440
dT4 = (jd4 - jd3)*1440
dT5 = (jd4 - jd1)*1440
dT6 = (jd5 - jd4)*1440
dT7 = (jd5 - jd3)*1440
dT8 = (jd4 - jd2)*1440
dT9 = (jd5 - jd2)*1440


cimport numpy as np
cimport cython
DOUBLE = np.float64
#S.U edit 2021.8.21
#DTYPE = np.int
DTYPE = np.int64
ctypedef np.int_t DTYPE_t 
ctypedef np.float64_t DOUBLE_t

#  i is ccd chip number
#make data

#selection of moving objcect candidate by comparing file1 and file2
###########tracklet 1-2 #########
def traclet1(np.ndarray[DOUBLE_t,ndim =2] radec1,np.ndarray[DOUBLE_t,ndim =2] radec2):
#    cdef np.ndarray[DOUBLE_t,ndim=1] temp2 = np.zeros([240,4],dtype=DOUBLE)
    cdef int i,j,num1,num2
    num1 = len(radec1)
    num2 = len(radec2)
    list1 = []
    for i in range(num1):
        for j in range(num2):
            tmp1 = radec2[j,0] - radec1[i,0]
            tmp2 = radec2[j,1] - radec1[i,1]
    #arcsec/min
            vel = np.sqrt(tmp1*tmp1+tmp2*tmp2)*3600/dT1
    #MBA ra decrease along with time.
    #        if tmp1 < 0 and vel > 0.2 and vel<1:
    #revised 2021.9.2. selection of less than 1.5 aresec/min 
            if vel < 1.5:
    #             print(radec1[i,0],radec2[j,0])
                list1.append([radec1b[i],radec2b[j]])
    #trac1
    trac1 = np.array(list1)
    return trac1
###########tracklet 1-3 #########
def traclet2(np.ndarray[DOUBLE_t,ndim =2] radec1,np.ndarray[DOUBLE_t,ndim =2] radec3):
#    cdef np.ndarray[DOUBLE_t,ndim=1] temp2 = np.zeros([240,4],dtype=DOUBLE)
    cdef int i,j,num1,num2
    num1 = len(radec1)
    num2 = len(radec3)
    list1 = []
    for i in range(num1):
        for j in range(num2):
            tmp1 = radec3[j,0] - radec1[i,0]
            tmp2 = radec3[j,1] - radec1[i,1]
    #arcsec/min
            vel = np.sqrt(tmp1*tmp1+tmp2*tmp2)*3600/dT3
    #MBA ra decrease along with time.
    #        if tmp1 < 0 and vel > 0.2 and vel<1:
    #revised 2021.9.2
            if vel < 1.5:
    #             print(radec1[i,0],radec2[j,0])
                list1.append([radec1b[i],radec3b[j]])
    #trac1
    trac1b = np.array(list1)
    return trac1b
###########tracklet 2-3 #########
def traclet3(np.ndarray[DOUBLE_t,ndim =2] radec2,np.ndarray[DOUBLE_t,ndim =2] radec3):
#    cdef np.ndarray[DOUBLE_t,ndim=1] temp2 = np.zeros([240,4],dtype=DOUBLE)
    cdef int i,j,num1,num2
    num1 = len(radec2)
    num2 = len(radec3)
    list1 = []
    for i in range(num1):
        for j in range(num2):
            tmp1 = radec3[j,0] - radec2[i,0]
            tmp2 = radec3[j,1] - radec2[i,1]
    #arcsec/min
            vel = np.sqrt(tmp1*tmp1+tmp2*tmp2)*3600/dT2
    #MBA ra decrease along with time.
    #        if tmp1 < 0 and vel > 0.2 and vel<1:
    #revised 2020.5.22
            if  vel < 1.5:
    #             print(radec1[i,0],radec2[j,0])
                list1.append([radec2b[i],radec3b[j]])
    #trac1
    trac1c = np.array(list1)
    return trac1c
###########tracklet 1-4 #########
def traclet4(np.ndarray[DOUBLE_t,ndim =2] radec1,np.ndarray[DOUBLE_t,ndim =2] radec4):
#    cdef np.ndarray[DOUBLE_t,ndim=1] temp2 = np.zeros([240,4],dtype=DOUBLE)
    cdef int i,j,num1,num2
    num1 = len(radec1)
    num2 = len(radec4)
    list1 = []
    for i in range(num1):
        for j in range(num2):
            tmp1 = radec4[j,0] - radec1[i,0]
            tmp2 = radec4[j,1] - radec1[i,1]
    #arcsec/min
            vel = np.sqrt(tmp1*tmp1+tmp2*tmp2)*3600/dT5
    #MBA ra decrease along with time.
    #        if tmp1 < 0 and vel > 0.2 and vel<1:
    #revised 2020.5.22
            if  vel < 1.5:
    #             print(radec1[i,0],radec2[j,0])
                list1.append([radec1b[i],radec4b[j]])
    #trac1
    trac1d = np.array(list1)
    return trac1d

###########tracklet 2-4 #########
def traclet5(np.ndarray[DOUBLE_t,ndim =2] radec2,np.ndarray[DOUBLE_t,ndim =2] radec4):
#    cdef np.ndarray[DOUBLE_t,ndim=1] temp2 = np.zeros([240,4],dtype=DOUBLE)
    cdef int i,j,num1,num2
    num1 = len(radec2)
    num2 = len(radec4)
    list1 = []
    for i in range(num1):
        for j in range(num2):
            tmp1 = radec4[j,0] - radec2[i,0]
            tmp2 = radec4[j,1] - radec2[i,1]
    #arcsec/min
            vel = np.sqrt(tmp1*tmp1+tmp2*tmp2)*3600/dT8
    #MBA ra decrease along with time.
    #        if tmp1 < 0 and vel > 0.2 and vel<1:
    #revised 2020.5.22
            if  vel < 1.5:
    #             print(radec1[i,0],radec2[j,0])
                list1.append([radec2b[i],radec4b[j]])
    #trac1
    trac1e = np.array(list1)
    return trac1e
###########tracklet 3-4 #########
def traclet6(np.ndarray[DOUBLE_t,ndim =2] radec3,np.ndarray[DOUBLE_t,ndim =2] radec4):
#    cdef np.ndarray[DOUBLE_t,ndim=1] temp2 = np.zeros([240,4],dtype=DOUBLE)
    cdef int i,j,num1,num2
    num1 = len(radec3)
    num2 = len(radec4)
    list1 = []
    for i in range(num1):
        for j in range(num2):
            tmp1 = radec4[j,0] - radec3[i,0]
            tmp2 = radec4[j,1] - radec3[i,1]
    #arcsec/min
            vel = np.sqrt(tmp1*tmp1+tmp2*tmp2)*3600/dT4
    #MBA ra decrease along with time.
    #        if tmp1 < 0 and vel > 0.2 and vel<1:
    #revised 2020.5.22
            if vel < 1.5:  
    #             print(radec1[i,0],radec2[j,0])
                list1.append([radec3b[i],radec4b[j]])
    #trac1
    trac1f = np.array(list1)
    return trac1f
