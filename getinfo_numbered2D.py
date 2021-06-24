#!/usr/bin/env python3
# -*- coding: UTF-8 -*
#revised 2020.5.29
import numpy as np
from astroquery.jplhorizons import Horizons
import os
import time
from astropy.io import ascii
from astropy.table import Table,vstack
import itertools
from multiprocessing import Pool
from multiprocessing import Process
import re
from astropy.io import fits
path_name = os.getcwd()

#read scidata
scidata1 = fits.open('warp1_bin.fits')
scidata2 = fits.open('warp2_bin.fits')
scidata3 = fits.open('warp3_bin.fits')
scidata4 = fits.open('warp4_bin.fits')
scidata5 = fits.open('warp5_bin.fits')

jd1 = scidata1[0].header['JD']
jd2 = scidata2[0].header['JD']
jd3 = scidata3[0].header['JD']
jd4 = scidata4[0].header['JD']
jd5 = scidata5[0].header['JD']

#time_list
time_list =[jd1,jd2,jd3,jd4,jd5]
time_list2 = [np.round(float(time_list[i]),decimals=8) for i in range(len(time_list))]  
      
#file_list
file_list = ['warp1_bin.png','warp2_bin.png','warp3_bin.png','warp4_bin.png','warp5_bin.png']

#numbered name_list
tmp2 = str("cand3.txt")
tmp4 = open(tmp2,"r")
name1 = tmp4.readlines()
name_list =[]
for i in name1:
    name_list.append(i.rstrip('\n'))
#time
#time1 = time_list[0]
t1 = time.time()

#number of name
nn = len(name_list)

#get info from jpl horizons
def getinfo(x):
#    print(name_list[x])
    radec =[]
    radec.append(Horizons(id=name_list[x],location='568',epochs=time_list2[0:5]).ephemerides()['targetname','datetime_jd','RA','DEC','V'])
    return radec



#if __name__ == "__main__":
#    with Pool(10) as p:
#        print(p.map(getinfo,range(nn)))
#        print(p.map(f,range(nn)))
#        tmp10 = p.map(getinfo,range(nn))

tmp10 = list(map(getinfo,range(nn)))  
tmp5 = np.array(tmp10)
#K.S. modifies 2020/12/7############################
temporary = np.ndarray((nn, 1, 5, 5),dtype=object)
for i1 in range(nn):
    for i2 in range(1):
        for i3 in range (5):
            for i4 in range(5):
                temporary[i1, i2, i3, i4] = tmp5[i1, i2, i3][i4]
                
tmp6 = temporary.reshape(nn*5,5)
####################################################
tmp7 =[]
for i in range(len(file_list)):
    for k in range(len(tmp6)):
#                print(tmp6[k,1],time_list2[i],i,k)
        if tmp6[k,1] - 0.0000001 <time_list2[i] and tmp6[k,1] +0.000001 > time_list2[i]:
#                   print(tmp6[k],file_list[i])
            tmp7 = np.append(tmp7,tmp6[k])
            tmp7 = np.append(tmp7,file_list[i])
tmp8 = tmp7.reshape(int(len(tmp7)/6),6)
#remove name and karifugo from numberd
for l in range(len(tmp8)):
    tmp9 = re.sub(r"\(.+?\)","",tmp8[l,0]) 
    tmp11 = re.sub(r"[a-zA-Z]","",tmp9) 
    tmp12 = tmp11.rstrip()
    tmp8[l,0] = tmp12
np.savetxt('numbered_new2B.txt',tmp8, fmt='%s')
t2 = time.time()
elapsed_time = t2 -t1
print(elapsed_time)

