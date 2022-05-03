#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import numpy as np
import re
from astropy.io import fits,ascii
from astropy.wcs import wcs
import scipy.spatial as ss
#read catalog

import glob
import subprocess

from photutils import source_properties
from photutils import data_properties
from astropy.stats import sigma_clipped_stats
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from photutils import RectangularAperture
from photutils import RectangularAnnulus
from astropy import units as u
from photutils import aperture_photometry
from astropy.visualization import SqrtStretch
from astropy.visualization.mpl_normalize import ImageNormalize
from astropy.coordinates import SkyCoord
from astropy.time import Time
import re
from bokeh.plotting import figure
#2022.5.4 major revised by S.U 
#get path 
path = os.getcwd()
#get x,y coord and file name
text      = path + '/memo2.txt'
f         = open(text,'r')
textfile  = f.read()
textfile2 = textfile.replace('(','').replace(')','').replace('\'','')
textfile3 = ascii.read(textfile2)

#define click event
def on_press1(event):
    global ix, iy, coords
    global width, height, angle, center, xy2,xy3,radec1,gyou,tt1,radec1b,ypix
    global ap1
    ix = event.xdata
    iy = event.ydata
    #plot mouse point
    ln1.set_data(ix,iy)
    plt.draw()
    print('x = %d, y = %d'%(ix, iy))
    #apend coordinate info
    coords.append([ix,iy])    
    #exec after 3 points click
    if len(coords) == 3:
        # set rectangle aperture
        a = np.array(coords[0])
        b = np.array(coords[1])
        # width: distance between a and b
        r1 = b - a
        width = np.linalg.norm(r1)
        # hight* distance between b and c
        c = np.array(coords[2])
        r2 = c - b
        height = np.linalg.norm(r2)
        # angle : theta = arctan(y1-y0/x1-x0) [rad]
        angle = np.arctan(r1[1]/r1[0])
        angle2 = angle * 180/np.pi
        center = (a +c)/2
        xy2 = xy1 - [15,15] + center
        xy3 = np.array([[xy2[0,0], ypix - xy2[0,1]]]) 
        radec1 = w1.wcs_pix2world(xy3,1)
        gyou = len(radec1)
        tt1 = np.zeros(gyou) + jd1
        radec1b = np.c_[tt1,radec1]
        #the purpose of ap1-set is to draw rectangle aperture. photometry is exec in def approve 
        ap1 = RectangularAperture(center, w = width, h = height,theta =angle)
        ap1.plot(color='#d62728')
        cid2 = plt.connect('button_press_event',approve)
    return
def approve(event):
    global j,tmpy,tmpy2,tmpx,tmpx2,tmp,ap1,rawflux_table1,final_sum1,sigma_ron,gain
    global S_star1,N21,N1,SNR1,mag1,mage1
    plt.draw()
    if event.dblclick == 1:
        ap1 = RectangularAperture(center, w = width, h = height,theta =angle)
        rawflux_table1 = aperture_photometry(tmp, ap1, method ='subpixel',subpixels = 5)
#flux with 2X2 binning mode        
        final_sum1 = nbin*nbin*(rawflux_table1['aperture_sum'])
#magnitude
        mag1 = np.round(zm1 - 2.5*np.log10(final_sum1),decimals=3)
#error estimation
        sigma_ron =  4.5*nbin*nbin #read out noise of HSC with 2X2 binning: nobinning 4.5 e-
        gain = 3.0 / nbin # gain of HSC with 2X2 binning :nobinning 3.0e/ADU
        S_star1 = gain * final_sum1     
#            N2 = S_star + effective_area * (gain * bkg_mean + sigma_ron)
        N21 = S_star1
        N1 = np.sqrt(N21)
#Noise in electron
        SNR1 = S_star1 / N1
#error in magnitude m_err = 1.0857/SNR
#Noise in ADU
        mage1 = np.round(1.0857/SNR1,decimals=3)
        result.append([number,radec1b[0,0],radec1b[0,1],radec1b[0,2],mag1,mage1,xy1[0,0],ypix-xy1[0,1]+30,fil1])
        plt.title("Good aperture!")
        j+=1
#        plt.draw()
#    elif event.button == 3:
    else:
        plt.title("Retry!")
    return 

#start photometry
result = []

j = 0    
while j <  len(textfile3):
    print(textfile3['col1','col2'][j])
    print(j)
    
#input all point source after find.sh
    xycoord1 = textfile3['col1','col2'][j]
#read scidata
    scidata1 = fits.open(textfile3['col3'][j])
#read personal number
    number = textfile3['col4'][j]
#time information & filter
    fil1 = scidata1[0].header['FILTER']
    jd1 = scidata1[0].header['JD']
#zero magnitude
    zm1 = scidata1[0].header['Z_P']
#X,Y pix
    xpix = scidata1[0].header['NAXIS1']
    ypix = scidata1[0].header['NAXIS2']
#nbin
    nbin = scidata1[0].header['NBIN']
    
#scidata
#scidata = [scidata1[0].data,scidata2[0].data,scidata3[0].data,scidata4[0].data,scidata5[0].data]
    scidata = [scidata1[0].data]
#x,y to wcs because warp image has same wcs info
    w1 = wcs.WCS(scidata1[0].header)
#time,x,y
    xy1 = np.array([[textfile3['col1'][j],textfile3['col2'][j]]])


########################   photometry  ################################
#i: id number #j:frame number # 0:time 1:ra 2:dec 
##############   exec  /as possible as row lever program##############
#S.U modified 22.4.29
#check ypix valuce because y pixel of memo2.txt is 30pixel larger than fits file
    tmpy = int(ypix+30 -(xy1[0,1]+15)) 
    tmpy2 = int(ypix+30 - (xy1[0,1]-15))
    tmpx = int(xy1[0,0]-15)
    tmpx2 = int(xy1[0,0]+15) 
    tmp = scidata[0][tmpy:tmpy2,tmpx:tmpx2]
#draw image    
    plt.imshow(tmp,origin='lower', cmap='viridis',interpolation='nearest')
    coords = []
#draw click point    
    ln1, = plt.plot([],[],'X')
    cid = plt.connect('button_press_event',on_press1)
    plt.show()
#result and output
result2 = np.array(result,dtype='object') #revised by S.U 2021.10.28
np.savetxt("./listb3.txt",result2,fmt="%d %.9f %.7f %.7f %.3f %.3f %.2f %.2f %s")
