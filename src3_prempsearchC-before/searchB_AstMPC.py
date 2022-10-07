#!/usr/bin/env python3
# -*- coding: UTF-8 -*
#Timestamp: 2022/08/04 14:30 sugiura
##############################################################################
# ~/.coias/param/AstMPC.edbに記載の明るい既知小惑星の一覧から,
# 視野内(tract中心から±1.8度以内, cf.HSCの視野直径1.5度)にあるものを探してくる.
#
# 入力: ~/.coias/param/AstMPC.edb
# 　　  warp01_bin.fits (jd, ra, decを取得するのに使用)
# 出力: cand_bright.txt
# 　　    視野内の明るい既知小惑星の大雑把な情報を記載したもの(整形前).
# 　　    書式: jd 天体名 ra[degree] dec[degree] mag
# 　　  bright_asteroid_raw_names_in_the_field.txt
# 　　    上の天体名だけをリストにしたもの.
##############################################################################
import numpy as np

from astropy.io import fits
import ephem
import julian
import time
import traceback

# multiprocessing
import multiprocessing

#---function-------------------------------------------------------------------
# mp.ra value is radian
def search(args):
    # site information
    subaru = ephem.Observer()
    subaru.lon =  '-155.4767'
    subaru.lat = '19.8256'
    subaru.elevation = 4139
    subaru.date = args[1]["date"]
    
    retList = []
    mp = ephem.readdb(args[0])
    mp.compute(subaru)
    ra2 = mp.ra*180/np.pi
    dec2 = mp.dec*180/np.pi
    if ra2 > args[1]["raMin"] and ra2 < args[1]["raMax"] and dec2 > args[1]["decMin"] and dec2 < args[1]["decMax"]:
        retList.append( [args[1]["jd"],mp.name,ra2,dec2,mp.mag] )
        
    return retList
#------------------------------------------------------------------------------

try:
    if __name__ == "__main__":
        nthread = multiprocessing.cpu_count()
    
        # ast list
        f = open("AstMPC_tmp.edb","r")
        data1 = f.readlines()
        f.close()

        # read scidata
        scidata1 = fits.open('warp01_bin.fits')
        jd1 = scidata1[0].header['JD']

        # ra dec
        ra = scidata1[0].header['CRVAL1']
        dec = scidata1[0].header['CRVAL2']
        # search region
        ra_min = ra-1.8
        ra_max = ra+1.8
        dec_min =  dec-1.8
        dec_max =  dec+1.8

        dt = julian.from_jd(float(jd1),fmt='jd')
        d = ephem.Date(dt)
    
        argDict = {"raMin":ra_min, "raMax":ra_max, "decMin":dec_min, "decMax":dec_max, "date":d, "jd":jd1}
        args = [(data1[i], argDict) for i in range(len(data1))]
        with multiprocessing.Pool(nthread) as p:
            tmp10 = p.map(search,args)
            
        tmp11 = [l for l in tmp10 if l]
        tmp12 = np.array(tmp11)
        tmp12 = tmp12.reshape(len(tmp12),5)
        np.savetxt('cand_bright.txt',tmp12,fmt='%s')

        #---save name of bright asteroids in the field------
        fileBrightAsteriods = open("bright_asteroid_raw_names_in_the_field.txt","w")
        for i in range(len(tmp12)):
            fileBrightAsteriods.write(tmp12[i][1]+"\n")
        fileBrightAsteriods.close()
        #---------------------------------------------------

except FileNotFoundError:
    if __name__ == "__main__":
        print("Some previous files are not found in searchB_AstMPC.py!")
        print(traceback.format_exc())
        error = 1
        errorReason = 34

except Exception:
    if __name__ == "__main__":
        print("Some errors occur in searchB_AstMPC.py!")
        print(traceback.format_exc())
        error = 1
        errorReason = 35

else:
    if __name__ == "__main__":
        error = 0
        errorReason = 34

finally:
    if __name__ == "__main__":
        errorFile = open("error.txt","a")
        errorFile.write("{0:d} {1:d} 306 \n".format(error,errorReason))
        errorFile.close()
