#!/usr/bin/env python3
# -*- coding: UTF-8 -*
from astropy.time import Time
from astropy import units as u
from astropy.coordinates import SkyCoord
import re
import numpy as np

#---function: input = asteroid number(str) for numbered asteroid, return = MPC format name--
def get_MPC_format_name_for_numbered_asteroids(ast_num):
    ast_num_int = int(ast_num)
    nameFragmentList = ['0','1','2','3','4','5','6','7','8','9','A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
    ################ over 620000 ####################
    if ast_num_int >= 620000:
        diff = ast_num_int - 620000
        modList = []
        for i in range(4):
            modList.append(diff%62)
            diff = diff//62
        name = "~" + nameFragmentList[modList[3]] + nameFragmentList[modList[2]] + nameFragmentList[modList[1]] + nameFragmentList[modList[0]]
    ################ any other ######################
    else:
        num = ast_num_int
        modList = []
        for i in range(4):
            modList.append(num%10)
            num = num//10
        modList.append(num%62)
        name = nameFragmentList[modList[4]] + nameFragmentList[modList[3]] + nameFragmentList[modList[2]] + nameFragmentList[modList[1]] + nameFragmentList[modList[0]]

    return name
#-------------------------------------------------------------------------------------------

#---function: input = karifugo without space, return = MPC format name----------------------
def get_MPC_format_name_for_karifugo_asteroids(karifugo):
    nameFragmentList = ['0','1','2','3','4','5','6','7','8','9','A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
    if karifugo[4:7]=="P-L" or karifugo[4:7]=="T-1" or karifugo[4:7]=="T-2" or karifugo[4:7]=="T-3":
        name = karifugo[4] + karifugo[6] + "S" + karifugo[0:4]
    else:
        if karifugo[0:2]=="18":
            firstThreeLetters = "I" + karifugo[2:4]
        elif karifugo[0:2]=="19":
            firstThreeLetters = "J" + karifugo[2:4]
        elif karifugo[0:2]=="20":
            firstThreeLetters = "K" + karifugo[2:4]

        if len(karifugo)==6:
            lastFourLetters = karifugo[4] + "00" + karifugo[5]
        elif len(karifugo)==7:
            lastFourLetters = karifugo[4] + "0" + karifugo[6] + karifugo[5]
        elif len(karifugo)==8:
            lastFourLetters = karifugo[4] + karifugo[6] + karifugo[7] + karifugo[5]
        elif len(karifugo)==9:
            num = int(karifugo[6:8])
            lastFourLetters = karifugo[4] + nameFragmentList[num] + karifugo[8] + karifugo[5]

        name = firstThreeLetters + lastFourLetters

    return name
#-------------------------------------------------------------------------------------------

#---function: input = jd(float), return = time in MPC format--------------------------------
def change_jd_to_MPC_format_date(jd):
    ##data modification
    tInTimeObj = Time(jd,format='jd')
    tInIso = tInTimeObj.iso
    rMatch = re.compile("(.*)( )(.*)")
    matchRes = rMatch.match(tInIso)
    matchGro = matchRes.group(1)
    ##get year month day
    tYYYYMMDD = matchGro.replace('-',' ')
    ##get decimal jd
    jdInt = int(jd)
    jdDecimal = jd - jdInt - 0.5
    if jdDecimal < 0.0:
        jdDecimal = jdDecimal + 1.0
    jdDecimal = np.around(jdDecimal,decimals=5)
    jdDecimalStr = str(jdDecimal).lstrip('0').ljust(6,'0')

    mpcFormatDate = 'C' + tYYYYMMDD + jdDecimalStr
    return(mpcFormatDate)
#-------------------------------------------------------------------------------------------

#---function: input = ra(degree), dec(degree), output = ra and dec in MPC format------------
def change_ra_dec_to_MPC_format(raDegree, decDegree):
    coord = SkyCoord(ra = raDegree*u.degree, dec = decDegree*u.degree)

    ##convert ra
    raHour = int(coord.ra.hms[0])
    raHourStr = "{:02d}".format(raHour)
    raMinit = int(coord.ra.hms[1])
    raMinitStr = "{:02d}".format(raMinit)
    raSecond = np.round(coord.ra.hms[2],decimals=2)
    raSecondStr = "{:.2f}".format(raSecond)
    raSecondStr = raSecondStr.rjust(5,'0')

    ##convert dec
    decDegree = coord.dec.dms[0]
    decDegreeInt = int(decDegree)
    decMinit = int(coord.dec.dms[1])
    decSecond = np.round(coord.dec.dms[2],decimals=2)
    
    if decDegree > 0.0:
        decDegreeStr = '+'+"{:02d}".format(decDegreeInt)
    elif decDegree > -1.0 and decDegree < 0.0:
        decDegreeStr = '-0'+"{:01d}".format(decDegreeInt)
        decMinit *= -1
        decSecond *= -1
    else:
        decDegreeStr = "{:03d}".format(decDegreeInt)
        decMinit *= -1
        decSecond *= -1

    decMinitStr = "{:02d}".format(decMinit)
    decSecondStr = "{:.2f}".format(decSecond).rjust(5,'0')

    mpcFormatRaDec = raHourStr + " " + raMinitStr + " " + raSecondStr + " " + decDegreeStr + " " + decMinitStr + " " + decSecondStr
    return mpcFormatRaDec
#-------------------------------------------------------------------------------------------
