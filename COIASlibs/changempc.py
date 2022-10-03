#!/usr/bin/env python3
# -*- coding: UTF-8 -*
#Timestamp: 2022/08/28 13:00 sugiura
#########################################################################
# 小惑星の名前やjd, ra, decをMPCフォーマットに整形する関数群を記載したスクリプト.
#
# get_MPC_format_name_for_numbered_asteroids()関数:
#     確定番号付きの小惑星の小惑星番号 (e.g.,イトカワなら25143) を引数に取り,
#     それをMPCフォーマットの5桁の文字列に整形して返す.
#     100000番未満なら単に0を左詰めして5桁で表現.
#     100000番以上620000番未満なら上2桁を[0-9A-Za-z]の62進数に変換する.
#     620000番以上なら頭に~をつけ残りの4桁を全て[0-9A-Za-z]の62進数で表現する.
#
# get_MPC_format_name_for_karifugo_asteroids()関数:
#     仮符号小惑星の仮符号からスペースを除いた文字列 (e.g., 1995XA) を引数に取り,
#     それをMPCフォーマットの7桁の文字列に整形して返す.
#     詳しい変換規則はこちらを参照:
#     https://www.minorplanetcenter.net/iau/info/PackedDes.html#prov
#     なお, P-L, T-1, T-2, T-3を含むものは過去4回の特別な掃天観測で観測された
#     小惑星であり, 通常の仮符号とは違った形式で仮符号が与えられた.
#
# change_jd_to_MPC_format_date()関数:
#     julian date (jd) を CYYYY MM DD.dddd の形式のMPCフォーマットの文字列に変換して返す.
#     CはCCDを表しており, HSCである限り固定である.
#     注意点としては, jdのUTCの正午から測られている一方で,
#     DD.dddd の小数点以下は深夜0時からの経過日数なので, 半日ずらさないといけない.
#
# change_ra_dec_to_MPC_format()関数:
#     第一引数にdegree単位での赤経(Right Ascension: ra),
#     第二引数にdegree単位での赤緯(DEClination: dec)を取り, MPCフォーマットの
#     (ra)HH MM SS.ss (dec)±DD MM SS.ss の文字列に変換して返す.
#     単位がraとdecで違うことに注意:
#     ra のHH: hour   -> 1週の(1/24)
#     ra のMM: minit  -> 1週の(1/24*60)
#     ra のSS: second -> 1週の(1/24*60*60)
#     decのDD: degree -> 1週の(1/360), ただし範囲は-90 ~ +90
#     decのMM: minit  -> 1週の(1/360*60) = 分角
#     decのSS: second -> 1週の(1/360*60*60) = 秒角
#
# change_datetime_in_MPC_to_jd()関数:
#     MPCフォーマットでの時刻(CYYYY MM DD.dddd)の文字列を引数に取り,
#     それをjdに変換して返す.
#
# change_ra_in_MPC_to_degree()関数:
#     MPCフォーマットでのra(HH MM SS.ss)の文字列を引数に取り,
#     それをdegree単位に変換して返す.
#
# change_dec_in_MPC_to_degree()関数:
#     MPCフォーマットでのdec(±DD MM SS.ss)の文字列を引数に取り,
#     それをdegree単位に変換して返す.
#########################################################################
from astropy.time import Time
from astropy import units as u
from astropy.coordinates import SkyCoord
import datetime
import julian
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
def change_ra_dec_to_MPC_format(raDegreeOrg, decDegreeOrg):
    coord = SkyCoord(ra = raDegreeOrg*u.degree, dec = decDegreeOrg*u.degree)

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
    
    if decDegreeOrg > 0.0:
        decDegreeStr = '+'+"{:02d}".format(decDegreeInt)
    elif decDegreeOrg > -1.0 and decDegreeOrg < 0.0:
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

#---function: input=time in MPC format (CYYYY MM DD.dddd), output=jd------------------------
def change_datetime_in_MPC_to_jd(datetimeInMPC):
    contents = datetimeInMPC.split()
    if len(contents)!=3 or len(contents[2].split("."))!=2:
        raise ValueError("invalid input for change_datetime_in_MPC_to_jd. input=" + datetimeInMPC)

    year = int(contents[0].lstrip("C"))
    month = int(contents[1])
    day = int(contents[2].split(".")[0])
    dayDecimal = float("0." + contents[2].split(".")[1])
    hour = int(dayDecimal * 24.0)
    minute = int( (dayDecimal * 24.0 - hour) * 60.0 )
    second = int( (dayDecimal * 24.0 * 60.0 - hour * 60.0 - minute) * 60.0 )
    
    dt = datetime.datetime(year, month, day, hour=hour, minute=minute, second=second)
    jd = julian.to_jd(dt, fmt="jd")

    return jd
#-------------------------------------------------------------------------------------------

#---function: input=ra in MPC format(HH MM SS.ss), output=ra in degree----------------------
def change_ra_in_MPC_to_degree(raInMPC):
    contents = raInMPC.split()
    if len(contents)!=3:
        raise ValueError("invalid input for change_ra_in_MPC_to_degree. input=" + raInMPC)

    raDegree = (360.0/24.0) * ( int(contents[0]) + int(contents[1])/60.0 + float(contents[2])/3600.0 )

    return raDegree
#-------------------------------------------------------------------------------------------

#---function: input=dec in MPC format(±DD MM SS.ss), output=dec in degree-------------------
def change_dec_in_MPC_to_degree(decInMPC):
    contents = decInMPC.split()
    if len(contents)!=3 or not (contents[0][0]=="+" or contents[0][0]=="-"):
        raise ValueError("invalid input for change_dec_in_MPC_to_degree. input=" + decInMPC)

    if contents[0][0]=="+":
        decDegree = int(contents[0]) + int(contents[1])/60.0 + float(contents[2])/3600.0
    if contents[0][0]=="-":
        decDegree = int(contents[0]) - int(contents[1])/60.0 - float(contents[2])/3600.0

    return decDegree
#-------------------------------------------------------------------------------------------
