#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#cython: boundscheck=False
import numpy as np
cimport numpy as np
cimport cython
from cython import boundscheck, wraparound

ctypedef np.float64_t DOUBLE_t

### make tracklets from two images ###########################################################################
### input: two-dimensional numpy arrays, first-dim: point id, second-dim: jd, ra, dec, mag####################
### input: delta t of two images in the unit of "minits" #####################################################
### output: three-dimensional list, first-dim: tracklet id, second-dim: image id, third-dim: jd, ra, dec, mag#
def make_tracklet(np.ndarray[DOUBLE_t,ndim =2] radec1b, np.ndarray[DOUBLE_t,ndim =2] radec2b, double dt, double velThresh):
    cdef int i,j,num1,num2
    cdef double raDelta, decDelta, vel
    with  boundscheck(False), wraparound(False):
    
        num1 = len(radec1b)
        num2 = len(radec2b)
        tracList = []
        for i in range(num1):
            for j in range(num2):
                raDelta  = radec2b[j,1] - radec1b[i,1]
                decDelta = radec2b[j,2] - radec1b[i,2]
                #arcsec/min
                vel = np.sqrt(raDelta*raDelta + decDelta*decDelta)*3600/dt
                #revised 2021.9.2. selection of less than 1.5 aresec/min 
                if vel < velThresh:
                    tracList.append([radec1b[i],radec2b[j]])
                    
    return tracList
