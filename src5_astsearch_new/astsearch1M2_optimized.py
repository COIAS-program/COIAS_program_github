#!/usr/bin/env python3
# -*- coding: utf-8 -*-

### import modules #######################################
import time
import glob
import numpy as np
import scipy.spatial as ss
from astropy.io import fits, ascii
from astropy.wcs import wcs
import subprocess
import traceback
import mktracklet_opt
import readparam

from photutils import CircularAperture
from photutils import CircularAnnulus
    
from astropy import units as u
from photutils import aperture_photometry
##########################################################

### constants ############################################
MINITS_IN_A_DAY = 1440.0
##########################################################

### class for storing a tracklet #########################
class TrackletClass:
    #---constructor------------------------------------------------
    #---second arg: int, first image id for an initial tracklet----
    #---third arg: int, second image id for an initial tracklet----
    #---fource arg: two-dimensional list for an initial tracklet---
    #---initialTrac[2(two images)][jd, ra, dec]--------------------
    def __init__(self, imageId1, imageId2, initialTrac):
        if imageId1<0 or imageId2<0 or imageId1 >= NImage or imageId2 >= NImage:
            raise ValueError("invalid imageId! imageId1={0:d} imageId2={1:d}".format(imageId1, imageId2))
        if len(initialTrac)!=2 or len(initialTrac[0])!=3 or len(initialTrac[1])!=3:
            raise ValueError("invalid shape of initialTrac! len(initialTrac)={0:d}, len(initialTrac[0])={1:d}, len(initialTrac[1])={2:d}".format(len(initialTrac), len(initialTrac[0]), len(initialTrac[1])))
        
        self.NDetect = 2
        self.isDetectedList = [False] * NImage
        self.isDetectedList[imageId1] = True
        self.isDetectedList[imageId2] = True
        self.data = [None] * NImage
        self.data[imageId1] = initialTrac[0]
        self.data[imageId2] = initialTrac[1]

    #---add additional data point---------------------------------
    #---second arg: image id for additional point-----------------
    #---third arg: a list of [jd, ra, dec]------------------------
    def add_data(self, imageId, additionalPoint):
        if imageId<0 or imageId>=NImage:
            raise ValueError("invalid imageId! imageId={0:d}".format(imageId))
        if len(additionalPoint)!=3:
            raise ValueError("invalid shape of additionalPoint! len(additionalPoint)={0:d}".format(len(additionalPoint)))
        
        self.NDetect += 1
        if self.isDetectedList[imageId]:
            raise ValueError("this imageId={0:d} is already detected!".format(imageId))
        self.isDetectedList[imageId] = True
        self.data[imageId] = additionalPoint

    #---return an image id pair for predict undetected point----
    #---input: image id which you want to predict---------------
    #---output: a tuple of a pair of image ids for predict------
    def get_image_ids_for_predict(self, idPredict):
        if self.isDetectedList[idPredict]:
            raise ValueError("This image is already detected! idPredict={0:d}".format(idPredict))

        nearestIdDist = NImage
        farestIdDist = 0
        for d in range(NImage):
            if self.isDetectedList[d]:
                dist = abs(d - idPredict)
                if dist <= nearestIdDist:
                    nearestIdDist = dist
                    nearestId = d
                if dist > farestIdDist:
                    farestIdDist = dist
                    farestId = d

        if nearestId < farestId:
            result = (nearestId, farestId)
        else:
            result = (farestId, nearestId)

        return result
##########################################################


### function for detecting points from arbitrary tracklets
def detect_points_from_tracklets(trackletClassList, imageIdTrac1, imageIdTrac2, imageIdPredict):
    if imageIdTrac1==imageIdTrac2 or imageIdTrac1==imageIdPredict or imageIdTrac2==imageIdPredict:
        raise ValueError("invalid index for detect_points_from_tracklets! imageIdTrac1={0:d}, imageIdTrac2={1:d}, imageIdPredict={2:d}".format(imageIdTrac1, imageIdTrac2, imageIdPredict))

    if imageIdPredict > imageIdTrac2:
        mode = "DetectUndetect"
    else:
        mode = "DestructDetected"

    NFuturePossibleDetection = NImage - imageIdPredict - 1
    if imageIdTrac1 > imageIdPredict: NFuturePossibleDetection -= 1
    if imageIdTrac2 > imageIdPredict: NFuturePossibleDetection -= 1

    for k in reversed(range(len(trackletClassList))):
        id1, id2 = trackletClassList[k].get_image_ids_for_predict(imageIdPredict)
        
        raPredict  = trackletClassList[k].data[id1][1] + (trackletClassList[k].data[id2][1] - trackletClassList[k].data[id1][1]) * (jdList[imageIdPredict] - jdList[id1]) / (jdList[id2] - jdList[id1])
        decPredict = trackletClassList[k].data[id1][2] + (trackletClassList[k].data[id2][2] - trackletClassList[k].data[id1][2]) * (jdList[imageIdPredict] - jdList[id1]) / (jdList[id2] - jdList[id1])
        pradec = (raPredict, decPredict)

        d, ref = treeList[imageIdPredict].query(pradec, distance_upper_bound=0.004)
        if d < 0.0005:
            if mode == "DetectUndetect":
                trackletClassList[k].add_data(imageIdPredict, radecbList[imageIdPredict][ref])
            elif mode == "DestructDetected":
                del trackletClassList[k]
                continue

        #If the maximum detection number for this tracklet in this stage is smaller than N_DETECT_THRESH,
        #this tracklet has no future and delete this.
        if trackletClassList[k].NDetect + NFuturePossibleDetection < N_DETECT_THRESH:
            del trackletClassList[k]
##########################################################


try:
    print("astsearch1M2.py starts")
    start = time.time()

    ### read parameters ######################################
    params = readparam.readparam()
    N_DETECT_THRESH = params["nd"]
    VEL_THRESH = params["vt"]
    APARTURE_RADIUS = params["ar"]
    ##########################################################
    
    
    ### read global data #####################################
    textFileNames = sorted(glob.glob('warp*_bin.dat'))
    warpFileNames = sorted(glob.glob('warp*_bin.fits'))
    NImage = len(warpFileNames)

    if N_DETECT_THRESH > NImage:
        raise ValueError("N_DETECT_THRESH(={0}) is larger than NImage(={1})!".format(N_DETECT_THRESH,NImage))

    #---read scidata-----------------------------------
    jdList = []
    zmList = []
    nbinList = []
    filList = []
    for f in range(NImage):
        scidata = fits.open(warpFileNames[f])
        jdList.append(scidata[0].header['JD'])
        zmList.append(scidata[0].header['Z_P'])
        nbinList.append(scidata[0].header['NBIN'])
        filList.append(scidata[0].header['FILTER'])
        if f==0:
            wcs0 = wcs.WCS(scidata[0].header)
    #--------------------------------------------------

    #---read ascii source list-------------------------
    textFNamesList = []
    radecList = []
    radecbList = []
    for f in range(NImage):
        textFNamesList.append(ascii.read(textFileNames[f]))
        xy = np.array([textFNamesList[f]['X_IMAGE'], textFNamesList[f]['Y_IMAGE']])
        xy = xy.T
        radecList.append(wcs0.wcs_pix2world(xy, 1))
        gyou = len(radecList[f])
        tt = np.zeros(gyou) + jdList[f]
        radecbList.append(np.c_[tt, radecList[f]])
    #--------------------------------------------------

    #---prepare KDTree---------------------------------
    treeList = []
    for f in range(NImage):
        treeList.append(ss.KDTree(radecList[f], leafsize=10))
    #--------------------------------------------------
    ##########################################################


    ### MAIN PART ############################################
    ##########################################################
    trackletListAll = []
    for leftTracId in range(NImage-1):
        for rightTracId in range(leftTracId+1, NImage):
            #If the maximum detection number for this tracklet is smaller than N_DETECT_THRESH,
            #we skip all calculations and predictions.
            if 2 + (NImage - rightTracId - 1) < N_DETECT_THRESH:
                continue

            #---mktracklet and store tracklets-----------
            tracList = mktracklet_opt.make_tracklet(radecbList[leftTracId], radecbList[rightTracId], abs(jdList[rightTracId]-jdList[leftTracId])*MINITS_IN_A_DAY,abs(VEL_THRESH))
            trackletClassList = []
            for k in range(len(tracList)):
                trackletClassList.append( TrackletClass(leftTracId, rightTracId, tracList[k]) )
            #---------------------------------------------
            
            for predictId in range(NImage):
                if leftTracId==predictId or rightTracId==predictId:
                    continue

                #---predict-------------------------------
                detect_points_from_tracklets(trackletClassList, leftTracId, rightTracId, predictId)
                #-----------------------------------------

            trackletListAll.append(trackletClassList)
    ##########################################################
    ##########################################################


    ### photometry ###########################################

    ## define id
    idtrac = 0
    idTracklet = []
    for p in range(len(trackletListAll)):
        idTrackletInner = []
        for k in range(len(trackletListAll[p])):
            idTrackletInner.append(idtrac)
            idtrac += 1
        idTracklet.append(idTrackletInner)
    
    result = []
    for image in range(NImage):
        scidata = fits.open(warpFileNames[image])
    
        for p in range(len(trackletListAll)):
            for k in range(len(trackletListAll[p])):
                if trackletListAll[p][k].NDetect < N_DETECT_THRESH:
                    raise ValueError("Something wrong! Tracklets with NDetect < N_DETECT_THRESH survive! this NDetect={0:d}".format(trackletListAll[p][k].NDetect))
            
                if not trackletListAll[p][k].isDetectedList[image]:
                    continue
                
                xypix = wcs0.wcs_world2pix(trackletListAll[p][k].data[image][1], trackletListAll[p][k].data[image][2], 1)

                # param of aperture
                w = APARTURE_RADIUS
                wa = w * u.pix
                w_in = (w + 2) * u.pix
                w_out = (w + 8) * u.pix

                position = (xypix[0], xypix[1])
                # aperture phot
                ap = CircularAperture(position, wa.value)
                sap = CircularAnnulus(position, w_in.value, w_out.value)

                rawflux_table = aperture_photometry(scidata[0].data, ap, method='subpixel', subpixels=5)
                bkgflux_table = aperture_photometry(scidata[0].data, sap, method='subpixel', subpixels=5)
                # 2020.11.25 revised
                bkg_mean = bkgflux_table['aperture_sum'] / sap.area
                bkg_sum = bkg_mean * ap.area
                final_sum = nbinList[image]*nbinList[image]*(rawflux_table['aperture_sum'] - bkg_sum) #K.S. modified 2022/5/3
                if final_sum <= 0:
                    final_sum = 1
                mag = np.round(zmList[image] - 2.5 * np.log10(final_sum), decimals=3)
                # error
                sigma_ron =  4.5*nbinList[image]*nbinList[image] # read out noise of HSC /nobining :4.5e S.U modified 2022/5/4
                gain = 3.0 / nbinList[image] # gain of HSC/nobining :3.0  S.U modified 2022/5/4
                S_star = gain * final_sum
                SNR = np.sqrt(S_star)
                # error in magnitude m_err = 1.0857/SNR
                # Noise in ADU
                mage = np.round(1.0857 / SNR, decimals=3)

                result.append([idTracklet[p][k], trackletListAll[p][k].data[image][0], trackletListAll[p][k].data[image][1], trackletListAll[p][k].data[image][2], mag, mage, xypix[0], xypix[1], filList[image]])


    result2 = np.array(result, dtype='object')  # revised by N.M 2020.12.14
    np.savetxt("listb2.txt", result2, fmt="%d %.9f %.7f %.7f %.3f %.3f %.2f %.2f %s")
    subprocess.run("sort -t ' ' -k 1,1n -k 2,2n listb2.txt -o listb2.txt", shell=True)
    ##########################################################
    end = time.time()
    print("astsearch1M2.py ends. elapsed time = {0:.2f} s".format(end-start))
    

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
