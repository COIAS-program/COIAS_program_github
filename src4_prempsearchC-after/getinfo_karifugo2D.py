#!/usr/bin/env python3
# -*- coding: UTF-8 -*
#Timestamp: 2022/10/08 8:30 sugiura
######################################################################################
# cand4.txtに記載の視野内の仮符号小惑星の精密位置をJPLに問い合わせる.
# ネットに繋がっていないと当然問い合わせできないし, たまに途中でタイムアウトすることもある.
# (ただし, 過去の問い合わせ結果は~/.astropy/cache/astroquery/Horizonsに保存されているらしく
#  これがあるとネットに繋がっていなくても情報を取得できたりする. 多少遅いが...)
# また, このスクリプトの完了でもってこの視野のJPLへの既知天体の問い合わせが終わるので,
# precise_orbit_directories.txtに記載のディレクトリ以下にra_dec_jd_time.txtを作成し,
# この視野の中心のra, decとjdと問い合わせを行った時間を記録する.
#
# 2022/10/8 並列化対応
#   並列化すると全問合わせにかかる時間は反比例して短くなるが, しかし並列してastroquery.jplhorizonzに問い合わせをすると確率でエラーを返される.
#   この確率は並列数を増やしていくと指数関数的に上昇するようである.
#   エラーが返された天体については後から単列で再度問い合わせを行うようにした.
#   そのため現在のアルゴリズムでは全体にかかる時間が最小になるような並列数が存在し, 今のところの調べだと4並列が最も効率が良いことが分かった.
#   従ってPool(4)の並列数は4にしてある.
#
# 入力: cand4.txt (視野内の仮符号小惑星の仮符号の一覧)
# 出力: precise_orbit_directories.txtに記載のディレクトリ/karifugo_new2B.txt
# 　　    cand4.txtに記載の天体の, JPLから得られた精密位置情報など
# 　　    書式: 仮符号 jd ra[degree] dec[degree] mag
# 　　  precise_orbit_directories.txtに記載のディレクトリ/ra_dec_jd_time.txt
# 　　    この視野の中心のra, decとjdと問い合わせを行った時刻.
# 　　    書式: ra[degree] dec[degree] jd unix時間[sec]
######################################################################################
import numpy as np
from astroquery.jplhorizons import Horizons
import time
from astropy.io import fits
import glob
from multiprocessing import Pool
import traceback
import requests.exceptions

#--function: get info from jpl horizons for a known asteroid-------------------------------
def getinfo(args):
    radec =[]
    isLosedAsteroid = False
    # tentative prevention of error (2022.4.8 KS)################################
    try:
        objRadec = Horizons(id=args[0],location='568',epochs=args[1],id_type="smallbody").ephemerides()['targetname','datetime_jd','RA','DEC','V']
    except ValueError:
        if args[3]==1:
            print("missing id="+ args[0] +" probably due to parallelization issue.")
        if args[3]==2:
            print("We cannot get information of id="+ args[0] +" from JPL.")
        isLosedAsteroid = True
    else:
        for i in range(len(args[1])):
            if args[2][i]==0:
                radec.append(objRadec[i])
    ############################################################################

    retDict = {"data":radec, "flag":isLosedAsteroid}
    return retDict
#------------------------------------------------------------------------------------------

try:
    if __name__ == "__main__":
        #---main--------------------------------------------------------------------------------
        t1 = time.time()
        # if have_all_precise_orbits.txt has 1, then known objects in all warp files were already searched,
        # so we skip all process in this script
        haveAllPreciseOrbitsFile = open("have_all_precise_orbits.txt","r")
        haveAllPreciseOrbits = int(haveAllPreciseOrbitsFile.readline().rstrip("\n"))
        haveAllPreciseOrbitsFile.close()

        if(haveAllPreciseOrbits==0):
            #---read precise_orbit_directories.txt---------------------------------------
            NShouldGetPreciseOrbit = 0
            directoryNames = []
            isCorrectDirectory = []
            preciseOrbitDirectoriesFile = open("precise_orbit_directories.txt","r")
            lines = preciseOrbitDirectoriesFile.readlines()
            Ndata = len(lines)
            i = 0
            for line in lines:
                content = line.split()
                directoryNames.append(content[0])
                isCorrectDirectory.append(int(content[1]))
                if isCorrectDirectory[i]==0:
                    NShouldGetPreciseOrbit += 1
                i += 1
            preciseOrbitDirectoriesFile.close()
            #----------------------------------------------------------------------------
    
            # read scidata
            img_list = sorted(glob.glob('warp*_bin.fits'))
            if len(img_list)==0:
                raise FileNotFoundError
            if len(img_list)!=Ndata:
                print("something wrong! len(img_list)={0:d} Ndata={1:d}".format(len(img_list), Ndata))
                raise Exception

            presentTimeStamp = time.time()
            time_list = []
            ra_list = []
            dec_list = []
            for i in range(len(img_list)):
                scidata = fits.open( img_list[i] )
                jd = scidata[0].header['JD']
                time_list.append( jd )
                ra = scidata[0].header['CRVAL1']
                ra_list.append( ra )
                dec = scidata[0].header['CRVAL2']
                dec_list.append( dec )
        
            # time_list
            time_list2 = [np.round(float(time_list[i]),decimals=8) for i in range(len(time_list))]  
        
            # karifugo name_list
            tmp2 = str("cand4.txt")
            tmp4 = open(tmp2,"r")
            name1 = tmp4.readlines()
            name_list =[]
            for i in name1:
                name_list.append(i.rstrip('\n'))
            
            # number of name
            nn = len(name_list)
            
            ## number of data we cannot get information from JPL (2022.4.8 KS)#############
            NLoseAsteroids = 0
            ###############################################################################

            args = [(name_list[i], time_list2, isCorrectDirectory, 1) for i in range(len(name_list))]
            with Pool(4) as p:
                recvDictList = list(p.map(getinfo, args))

            ### second trial for errored query with one thread ########
            second_name_list = []
            for i in reversed(range(nn)):
                if recvDictList[i]["flag"]==True:
                    second_name_list.append(name_list[i])
                    del recvDictList[i]

            secondArgs = [(second_name_list[i], time_list2, isCorrectDirectory, 2) for i in range(len(second_name_list))]
            for i in range(len(second_name_list)):
                recvDict = getinfo(secondArgs[i])
                recvDictList.append(recvDict)
            ###########################################################
            
            tmp10 = []
            for i in range(nn):
                if len(recvDictList[i]["data"])!=0:
                    tmp10.append(recvDictList[i]["data"])
                if recvDictList[i]["flag"]==True:
                    NLoseAsteroids += 1
                    
            nn = nn - NLoseAsteroids
            tmp5 = np.array(tmp10)
            tmp5.reshape(nn,1,NShouldGetPreciseOrbit)
            ###############################################################################
                    
            # K.S. modifies 2022/4/13###########################
            temporary = np.ndarray((nn, NShouldGetPreciseOrbit, 5),dtype=object)
            for i1 in range(nn):
                for i2 in range (NShouldGetPreciseOrbit):
                    for i3 in range(5):
                        temporary[i1, i2, i3] = tmp5[i1][i2][i3]
                                    
            tmp6 = temporary.reshape(nn*NShouldGetPreciseOrbit,5)
            ####################################################
            tmp7 = np.empty(0)
                                    
            for i in range(len(img_list)):
                for k in range(len(tmp6)):
                    if tmp6[k,1] - 0.0000001 <time_list2[i] and tmp6[k,1] +0.000001 > time_list2[i]:
                        tmp7 = np.append(tmp7,tmp6[k])
                        tmp7 = np.append(tmp7, str(i)) # NM 2021.07.08
            tmp8 = tmp7.reshape(int(len(tmp7)/6),6)
                                                
            # remove name and karifugo from numberd
            for l in range(len(tmp8)):
                tmp8[l,0] = tmp8[l,0].replace("(","").replace(")","").replace(" ","")
        
            fList = np.ndarray((Ndata),dtype=object)
            for i in range(Ndata):
                if isCorrectDirectory[i]==0:
                    fList[i] = open(directoryNames[i]+"/karifugo_new2B.txt","w",newline="\n")

            for i in range(len(tmp8)):
                fList[int(tmp8[i,5])].write(tmp8[i,0]+" "+str(tmp8[i,1])+" "+str(tmp8[i,2])+" "+str(tmp8[i,3])+" "+str(tmp8[i,4])+"\n")

            for i in range(Ndata):
                if isCorrectDirectory[i]==0:
                    fList[i].close()

            for i in range(Ndata):
                if isCorrectDirectory[i]==0:
                    raDecJdTimeFile = open(directoryNames[i]+"/ra_dec_jd_time.txt","w",newline="\n")
                    raDecJdTimeFile.write("{0:.5f} {1:.5f} {2:.7f} {3:.1f}".format(ra_list[i],dec_list[i],time_list[i],presentTimeStamp))
                    raDecJdTimeFile.close()
        
            t2 = time.time()    
            elapsed_time = t2 -t1
            print("getinfo karifugo, Elapsed time:", elapsed_time)

except requests.exceptions.ConnectionError:
    print("You do not connect to the internet in getinfo_karifugo2D.py!")
    print(traceback.format_exc())
    error = 1
    errorReason = 42

except (requests.exceptions.ConnectTimeout, requests.exceptions.ReadTimeout):
    print("Connection timeout to NASA JPL in getinfo_karifugo2D!")
    print(traceback.format_exc())
    error = 1
    errorReason = 43

except FileNotFoundError:
    print("Some previous files are not found in getinfo_karifugo2D.py!")
    print(traceback.format_exc())
    error = 1
    errorReason = 44

except Exception:
    print("Some errors occur in getinfo_karifugo2D.py!")
    print(traceback.format_exc())
    error = 1
    errorReason = 45

else:
    error = 0
    errorReason = 44

finally:
    errorFile = open("error.txt","a")
    errorFile.write("{0:d} {1:d} 402 \n".format(error,errorReason))
    errorFile.close()
