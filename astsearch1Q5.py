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

#get path 
path = os.getcwd()
#get x,y coord and file name
text      = path + '/memo2.txt'
f         = open(text,'r')
textfile  = f.read()
textfile2 = textfile.replace('(','').replace(')','').replace('\'','')
textfile3 = ascii.read(textfile2)

result = []
for j in range(len(textfile3)):
    print(textfile3['col1','col2'][j])
    
    
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

#scidata
#scidata = [scidata1[0].data,scidata2[0].data,scidata3[0].data,scidata4[0].data,scidata5[0].data]
    scidata = [scidata1[0].data]


#x,y to wcs because warp image has same wcs info
    w1 = wcs.WCS(scidata1[0].header)

#t,x,y
    xy1 = np.array([[textfile3['col1'][j],textfile3['col2'][j]]])
#xy1 = xy1.T
#    radec1 = w1.wcs_pix2world(xy1,1)
#    gyou = len(radec1)
#    tt1 = np.zeros(gyou) + jd1
#    radec1b = np.c_[tt1,radec1]


########################   photometry  ################################

#
#    result=[]


#i: id number #j:frame number # 0:time 1:ra 2:dec 
##############   exec  /as possible as row lever program##############
#first
    tmpy = int(ypix -(xy1[0,1]+15)) 
    tmpy2 = int(ypix - (xy1[0,1]-15))
    tmpx = int(xy1[0,0]-15)
    tmpx2 = int(xy1[0,0]+15) 
    tmp = scidata[0][tmpy:tmpy2,tmpx:tmpx2]
#mean,median,std = sigma_clipped_stats(tmp,sigma=1.0,maxiters=5)
#tmp-=median 
#mean,median,std = sigma_clipped_stats(tmp,sigma=1.0,maxiters=5)
#tmp-=median

#


#plt.imshow(tmp,origin='lower', cmap='viridis',interpolation='nearest')
#define rectangle aperture
    i = 0
    while i < 3:
#    i+=1
        plt.imshow(tmp,origin='lower', cmap='viridis',interpolation='nearest')
        coords = []

        def on_press1(event):
            global ix, iy
            global width, height, angle, center, xy2,xy3,radec1,gyou,tt1,radec1b,ypix
            ix = event.xdata
            iy = event.ydata
    #plott mouse point
            ln1.set_data(ix,iy)
#       plt.draw()
            print('x = %d, y = %d'%(ix, iy))
            global coords
            coords.append([ix,iy])

            if len(coords) == 3:
#        eve
                plt.disconnect(cid)
#        print(coords[0])
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

                plt.draw()
#        print(center,width, height, angle,angle2)
            return
        
        ln1, = plt.plot([],[],'X')

        cid = plt.connect('button_press_event',on_press1)
#plt.connect('button_press_event',on_press2)

        plt.show()

# approve of aperture
        def approve(event):
            global i
            if event.dblclick == 1:
                plt.title("Good aperture!")
                i = 4
            plt.draw()
        ap1 = RectangularAperture(center, w = width, h = height,theta =angle)
        rawflux_table1 = aperture_photometry(tmp, ap1, method ='subpixel',subpixels = 5)
        plt.imshow(tmp,origin='lower', cmap='viridis',interpolation='nearest')
        ap1.plot(color='#d62728')
        cid2 = plt.connect('button_press_event',approve)
        plt.show()


#cid = plt.connect('button_press_event',on_press1)




#            final_sum = 4.0*(rawflux_table['aperture_sum'] - bkg_sum)
        final_sum1 = 4.0*(rawflux_table1['aperture_sum'])

#magnitude
        mag1 = np.round(zm1 - 2.5*np.log10(final_sum1),decimals=3)


#error estimation
        sigma_ron =  4.5 #read out noise of HSC
        gain = 9.0 # HSC
        S_star1 = gain * final_sum1     
#            N2 = S_star + effective_area * (gain * bkg_mean + sigma_ron)
        N21 = S_star1

        N1 = np.sqrt(N21)
#Noise in electron
#
        SNR1 = S_star1 / N1


#error in magnitude m_err = 1.0857/SNR
#Noise in ADU
        mage1 = np.round(1.0857/SNR1,decimals=3)

        result.append([number,radec1b[0,0],radec1b[0,1],radec1b[0,2],mag1,mage1,xy1[0,0],xy1[0,1],fil1])

result2 = np.array(result,dtype='object') #revised by S.U 2021.10.28
#np.savetxt("/home/urakawa/bin/Asthunter/listb2.txt",result2,fmt="%d %.9f %.7f %.7f %.3f %.3f %.2f %.2f %s")

np.savetxt("./listb3.txt",result2,fmt="%d %.9f %.7f %.7f %.3f %.3f %.2f %.2f %s")
