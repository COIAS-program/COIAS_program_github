#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# timestamp: 2022/08/04 17:00 sugiura
###################################################################################
# 光源の情報から移動天体候補自動検出・測光を行う.
# (このスクリプトの説明はあまりにも複雑なので詳細は杉浦に聞いて欲しい)
#
# 1本のtrackletでもノイズとシグナルが共存してしまうことがあるが,
# その場合多くは等級が大きく違うので, 中央値から大きく外れたデータ点は弾く.
# その後同じ移動天体と思しきtrackletたちは1本にマージするという操作も行っている.
#
# 1本のtrackletの情報を保持するクラスとしてTrackletClassを定義している.
#
# 光源を繋いだとき時間と共に線形に動いている光源の組を1つのtracklet(移動天体候補)と見なす.
# まず, 任意の2枚の画像から1つずつ光源を選び取り, それが移動したとき速度がvt(デフォルト1.5"/min)
# 以下になるような全ての組み合わせをmktracklet_opt.pyxのmake_tracklet()関数で取得する.
# 次に, それが線形に移動したとき他の画像にいるであろう場所のすぐ近くに光源がないかどうか探し,
# あった場合はそれをtrackletの一部と見なす.
# これを全ての画像・全ての光源の組み合わせに対して適用し, nd以上検出したら移動天体と見なす.
# なお, detect_points_from_tracklets()関数の中で mode = "DestructDetected" (破壊)
# モードがあるが, これはすでに試した組み合わせを重複して残さないようにするための措置である.
#
# 上記の方法でtrackletを作っても誤差などのせいで1つの移動天体が複数のtrackletに分割されてしまうことがある.
# それらを1本のtrackletにマージする操作をするが, 1本と見なせるかどうかの判定は
# is_identical_to_another_tracklet()メソッドで行っている.
# ここではselfとanotherのtrackletを比べ, 並行に近く, 速度も近く, 位置も近く, 等級も近い
# 場合には同じtrackletと見なしTrueを返す. (実際のマージはmerge_another_tracklet_to_this()メソッドで行う)
# 位置が近い(condition 3 と 4)について補足: selfのtrackletの中央の位置からこのtrackletの速度で移動して,
# anotherのtrackletの中央の時刻に移動したとき, anotherのtrackletと並行かつそれを囲う長方形の内部にいたら近いと見なす.
#
# 入力: warp*_bin.dat 光源の位置の一覧を取得する.
# 　　  warp*_bin.fits jdを取得したり, 測光したりするために使用する.
# 出力: listb2.txt
# 　　    移動天体候補と見なされた天体の各画像におけるデータを全て列挙したもの
# 　　    書式: trackletID jd ra[degree] dec[degree] mag magerr Xpixel Ypixel フィルター 画像番号
###################################################################################

### import modules #######################################
import sys
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
import print_progress
import print_detailed_log

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
    #---initialTrac[2(two images)][jd, ra, dec, mag]---------------
    def __init__(self, imageId1, imageId2, initialTrac):
        if imageId1<0 or imageId2<0 or imageId1 >= NImage or imageId2 >= NImage:
            raise ValueError("invalid imageId! imageId1={0:d} imageId2={1:d}".format(imageId1, imageId2))
        if len(initialTrac)!=2 or len(initialTrac[0])!=4 or len(initialTrac[1])!=4:
            raise ValueError("invalid shape of initialTrac! len(initialTrac)={0:d}, len(initialTrac[0])={1:d}, len(initialTrac[1])={2:d}".format(len(initialTrac), len(initialTrac[0]), len(initialTrac[1])))
        
        self.NDetect = 2
        self.isDetectedList = [False] * NImage
        self.isDetectedList[imageId1] = True
        self.isDetectedList[imageId2] = True
        self.data = [None] * NImage
        self.data[imageId1] = initialTrac[0]
        self.data[imageId2] = initialTrac[1]

        ### properties for characterize this tracklet-------------
        self.lendgh = None             #degree
        self.centerXY = [None, None]   #degree, degree
        self.angle = None              #radian (0 means +x direction, pi/2 means +y direction)
        self.speed = None              #degree/jd
        self.direction = [None, None]  #dimensionless
        self.centerJd = None           #jd

    #---add additional data point---------------------------------
    #---second arg: image id for additional point-----------------
    #---third arg: a list of [jd, ra, dec, mag]-------------------
    def add_data(self, imageId, additionalPoint):
        if imageId<0 or imageId>=NImage:
            raise ValueError("invalid imageId! imageId={0:d}".format(imageId))
        if len(additionalPoint)!=4:
            raise ValueError("invalid shape of additionalPoint! len(additionalPoint)={0:d}".format(len(additionalPoint)))
        if self.isDetectedList[imageId]:
            raise ValueError("this imageId={0:d} is already detected!".format(imageId))
        
        self.NDetect += 1
        self.isDetectedList[imageId] = True
        self.data[imageId] = additionalPoint

    #---del a data point----------------------------------------
    #---input: image id for data would be removed---------------
    def del_data(self, imageId):
        if imageId<0 or imageId>=NImage:
            raise ValueError("invalid imageId! imageId={0:d}".format(imageId))
        if not self.isDetectedList[imageId]:
            raise ValueError("this imageId={0:d} is not yet detected, but you want to delete it!".format(imageId))

        self.NDetect -= 1
        self.isDetectedList[imageId] = False
        self.data[imageId] = None

    #---merge another tracklet to this tracklet----------------------------------
    #---If another tracklet has data in images where this tracklet does not have,
    #---simply copy the data to this tracklet.-----------------------------------
    #---If another tracklet has data in images where this tracklet already has,--
    #---this tracklet has priority and ignore data in another tracklet-----------
    #---input: another tracklet--------------------------------------------------
    def merge_another_tracklet_to_this(self, anotherTracklet):
        for image in range(NImage):
            if (not self.isDetectedList[image]) and (anotherTracklet.isDetectedList[image]):
                self.isDetectedList[image] = True
                self.NDetect += 1
                self.data[image] = anotherTracklet.data[image]

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

    #---return median mag. of this tracklet---------------
    #---input: void---------------------------------------
    #---output: median mag. of this tracklet--------------
    def get_median_mag_of_this_tracklet(self):
        magList = []
        for image in range(NImage):
            if self.isDetectedList[image]:
                magList.append(self.data[image][3])

        return np.sort(magList)[len(magList)//2]

    #---calculate characteristic properties of this tracklet
    #---input: void, output: void---------------------------
    def calculate_characteristic_properties(self):
        ### find min and max valid index
        minIndex = NImage
        maxIndex = 0
        for image in range(NImage):
            if (self.isDetectedList[image]) and (minIndex>image): minIndex = image
            if (self.isDetectedList[image]) and (maxIndex<image): maxIndex = image

        ### calculate
        self.length = np.sqrt( (self.data[maxIndex][1]-self.data[minIndex][1])*(self.data[maxIndex][1]-self.data[minIndex][1]) + (self.data[maxIndex][2]-self.data[minIndex][2])*(self.data[maxIndex][2]-self.data[minIndex][2]) )
        self.centerXY = [(self.data[maxIndex][1]+self.data[minIndex][1])/2.0, (self.data[maxIndex][2]+self.data[minIndex][2])/2.0]
        self.angle = np.arctan2((self.data[maxIndex][2]-self.data[minIndex][2]), (self.data[maxIndex][1]-self.data[minIndex][1]))
        self.speed = abs(self.length / (self.data[maxIndex][0] - self.data[minIndex][0]))
        self.direction = [np.cos(self.angle), np.sin(self.angle)]
        self.centerJd = (self.data[maxIndex][0]+self.data[minIndex][0])/2.0

    #---assess this tracklet seems to be identical to input tracklet-
    #---input: another tracklet--------------------------------------
    def is_identical_to_another_tracklet(self, anotherTracklet):
        thisPredictedXAtAnotherJd = self.centerXY[0] + self.direction[0] * self.speed * (anotherTracklet.centerJd - self.centerJd)
        thisPredictedYAtAnotherJd = self.centerXY[1] + self.direction[1] * self.speed * (anotherTracklet.centerJd - self.centerJd)
        initXOfAnotherTracklet = anotherTracklet.centerXY[0] - 0.5 * anotherTracklet.length * anotherTracklet.direction[0]
        initYOfAnotherTracklet = anotherTracklet.centerXY[1] - 0.5 * anotherTracklet.length * anotherTracklet.direction[1]
        thisPredictedRelX = thisPredictedXAtAnotherJd - initXOfAnotherTracklet
        thisPredictedRelY = thisPredictedYAtAnotherJd - initYOfAnotherTracklet

        distAlongAnotherTracklet =  anotherTracklet.direction[0] * thisPredictedRelX + anotherTracklet.direction[1] * thisPredictedRelY
        distFromAnotherTracklet  = -anotherTracklet.direction[1] * thisPredictedRelX + anotherTracklet.direction[0] * thisPredictedRelY

        ### condition 1: difference of angle between this and another tracklet is less than 5 degrees
        ### condition 2: difference of speed between this and another tracklet is less than 0.3 arcseconds/min
        ### condition 3: predicted position of this at another tracklet is between another tracklet
        ### condition 4: distance between predicted position from another tracklet is less than 3.6 arcseconds
        ### condition 5: difference of median mag. between this and nother tracklet is less than 0.7 magnitude
        if ( abs(self.angle-anotherTracklet.angle) < 5.0*np.pi/180.0 and
             abs(self.speed-anotherTracklet.speed) < 0.3*MINITS_IN_A_DAY/3600.0 and
             distAlongAnotherTracklet > 0.0 and distAlongAnotherTracklet < anotherTracklet.length and
             abs(distFromAnotherTracklet) < 3.6/3600.0 and
             abs(self.get_median_mag_of_this_tracklet() - anotherTracklet.get_median_mag_of_this_tracklet()) < 0.7 ):
            return True
        else:
            return False
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
    ### suppress warnings ####################################
    if not sys.warnoptions:
        import warnings
        warnings.simplefilter("ignore")
    
    ### read parameters ######################################
    params = readparam.readparam()
    N_DETECT_THRESH = params["nd"]
    readparam.write_used_param("nd", params["nd"])
    VEL_THRESH = params["vt"]
    readparam.write_used_param("vt", params["vt"])
    APARTURE_RADIUS = params["ar"]
    readparam.write_used_param("ar", params["ar"])
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

    if nbinList[0]==4:
        APARTURE_RADIUS = APARTURE_RADIUS / 2.0
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
        magList = np.array(textFNamesList[f]['MAG_BEST'])
        gyou = len(radecList[f])
        tt = np.zeros(gyou) + jdList[f]
        radecbList.append(np.c_[tt, radecList[f], magList])
    #--------------------------------------------------

    #---prepare KDTree---------------------------------
    treeList = []
    for f in range(NImage):
        treeList.append(ss.KDTree(radecList[f], leafsize=10))
    #--------------------------------------------------

    #---count nForLoop for MAIN PART-------------------
    nLoopTotal = 0
    for leftTracId in range(NImage-1):
        for rightTracId in range(leftTracId+1, NImage):
            if 2 + (NImage - rightTracId - 1) < N_DETECT_THRESH:
                continue
            for predictId in range(NImage):
                if leftTracId==predictId or rightTracId==predictId:
                    continue
                nLoopTotal += 1
    #--------------------------------------------------
    ##########################################################

    ### MAIN PART ############################################
    ##########################################################
    trackletListAll = []
    nLoopDone = 0
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
                
                print_progress.print_progress(nCheckPointsForLoop=12, nForLoop=nLoopTotal, currentForLoop=nLoopDone)
                nLoopDone += 1
                #---predict-------------------------------
                detect_points_from_tracklets(trackletClassList, leftTracId, rightTracId, predictId)
                #-----------------------------------------

            trackletListAll.append(trackletClassList)
    ##########################################################
    ##########################################################
    

    ### check: all tracklets really have points > N_DETECT_THRESH ##
    for p in range(len(trackletListAll)):
        for k in range(len(trackletListAll[p])):
            if trackletListAll[p][k].NDetect < N_DETECT_THRESH:
                raise ValueError("Something wrong! Tracklets with NDetect < N_DETECT_THRESH survive! this NDetect={0:d}".format(trackletListAll[p][k].NDetect))
    ################################################################

    
    ### photometry #################################################
    for image in range(NImage):
        print_progress.print_progress(nCheckPointsForLoop=2, nForLoop=NImage, currentForLoop=image)
        
        scidata = fits.open(warpFileNames[image])
    
        for p in range(len(trackletListAll)):
            for k in reversed(range(len(trackletListAll[p]))):
            
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
                bkg_mean = bkgflux_table['aperture_sum'][0] / sap.area
                bkg_sum = bkg_mean * ap.area
                final_sum = nbinList[image]*nbinList[image]*(rawflux_table['aperture_sum'][0] - bkg_sum) #K.S. modified 2022/5/3
                if final_sum <= 0:
                    trackletListAll[p][k].del_data(image)
                    if trackletListAll[p][k].NDetect < 2:
                        del trackletListAll[p][k]
                    continue
                mag = np.round(zmList[image] - 2.5 * np.log10(final_sum), decimals=3)
                # error
                sigma_ron =  4.5*nbinList[image]*nbinList[image] # read out noise of HSC /nobining :4.5e S.U modified 2022/5/4
                gain = 3.0 / nbinList[image] # gain of HSC/nobining :3.0  S.U modified 2022/5/4
                S_star = gain * final_sum  
                Noise = np.sqrt(S_star + ap.area * (gain * bkg_mean + sigma_ron * sigma_ron))  # S.U modified 2022/7/16
                SNR = np.sqrt(S_star/Noise) # S.U modified 2022/7/16
                # error in magnitude m_err = 1.0857/SNR
                # Noise in ADU
                mage = np.round(1.0857 / SNR, decimals=3)

                trackletListAll[p][k].data[image][3] = mag
                trackletListAll[p][k].data[image] = np.append(trackletListAll[p][k].data[image], mage)
    ################################################################

    
    ### remove data with mag. largely different from median mag. of the tracklet#
    for p in range(len(trackletListAll)):
        for k in reversed(range(len(trackletListAll[p]))):
            medianMag = trackletListAll[p][k].get_median_mag_of_this_tracklet()
            for image in range(NImage):
                if trackletListAll[p][k].isDetectedList[image]:
                    if abs(trackletListAll[p][k].data[image][3] - medianMag) > 0.7:
                        trackletListAll[p][k].del_data(image)
            if trackletListAll[p][k].NDetect < 2:
                del trackletListAll[p][k]
    #############################################################################


    ### calculate characteristic properties of tracklets #####
    for p in range(len(trackletListAll)):
        for k in range(len(trackletListAll[p])):
            trackletListAll[p][k].calculate_characteristic_properties()
    ##########################################################


    ### merge likely identical tracklets #####################
    shouldBeDeleted = []
    for p in range(len(trackletListAll)):
        shouldBeDeleted.append( [False]*len(trackletListAll[p]) )

    ### thisp and thisk means self tracklet
    for thisp in range(len(trackletListAll)):
        for thisk in range(len(trackletListAll[thisp])):
            if shouldBeDeleted[thisp][thisk]:
                continue
            ### p and k means opponent tracklet
            for p in range(thisp, len(trackletListAll)):
                if thisp==p:
                    startk = thisk + 1
                else:
                    startk = 0
                for k in range(startk, len(trackletListAll[p])):
                    ### evaluate opponent is identical to self
                    if trackletListAll[thisp][thisk].is_identical_to_another_tracklet(trackletListAll[p][k]) and not shouldBeDeleted[p][k]:
                        trackletListAll[thisp][thisk].merge_another_tracklet_to_this(trackletListAll[p][k])
                        shouldBeDeleted[p][k] = True

    ### delete similar tracklets
    for p in range(len(trackletListAll)):
        for k in reversed(range(len(trackletListAll[p]))):
            if shouldBeDeleted[p][k]:
                del trackletListAll[p][k]
    ##########################################################
    

    ### output result ########################################

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
    for p in range(len(trackletListAll)):
        for k in range(len(trackletListAll[p])):
            for image in range(NImage):
                if not trackletListAll[p][k].isDetectedList[image]:
                    continue

                xypix = wcs0.wcs_world2pix(trackletListAll[p][k].data[image][1], trackletListAll[p][k].data[image][2], 1)
                result.append([idTracklet[p][k], trackletListAll[p][k].data[image][0], trackletListAll[p][k].data[image][1], trackletListAll[p][k].data[image][2], trackletListAll[p][k].data[image][3], trackletListAll[p][k].data[image][4], xypix[0], xypix[1], filList[image], image])


    result2 = np.array(result, dtype='object')  # revised by N.M 2020.12.14
    np.savetxt("listb2.txt", result2, fmt="%d %.9f %.7f %.7f %.3f %.3f %.2f %.2f %s %d")
    subprocess.run("sort -t ' ' -k 1,1n -k 2,2n listb2.txt -o listb2.txt", shell=True)
    ##########################################################

except FileNotFoundError:
    print("Some previous files are not found in astsearch1M2.py!",flush=True)
    print(traceback.format_exc(),flush=True)
    error = 1
    errorReason = 54

except Exception:
    print("Some errors occur in astsearch1M2.py!",flush=True)
    print(traceback.format_exc(),flush=True)
    error = 1
    errorReason = 55

else:
    error = 0
    errorReason = 54

finally:
    errorFile = open("error.txt","a")
    errorFile.write("{0:d} {1:d} 503 \n".format(error,errorReason))
    errorFile.close()

    if error==1:
        print_detailed_log.print_detailed_log(dict(globals()))
