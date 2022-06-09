#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re

import numpy as np
from astropy import units as u
from astropy.coordinates import SkyCoord
from astropy.time import Time

############ UNKNOWN  ######################
# Revised SU.2021/7/11
if os.stat("nomatch_manual.txt").st_size == 0:
    empty = []
    np.savetxt('unknown_mpc_m.txt', empty, fmt="%s")
    np.savetxt('unknown_all_m.txt', empty, fmt="%s")
    np.savetxt('unknown_disp_m.txt', empty, fmt="%s")
else:
    data = np.loadtxt("nomatch_manual.txt", usecols=[0, 1, 2, 3, 4, 5, 6, 7])
    fil = np.loadtxt("nomatch_manual.txt", dtype='str', usecols=[8, 9])
    # name change
    tmp = [int(x) for x in data[:, 0]]
    tmp2 = [str(x).zfill(6) for x in tmp]
    name1 = ['     H' + x for x in tmp2]

    # convert to time fmt year month day.decimal
    t = Time(data[:, 1], format='jd')
    t1 = t.iso
    # space kugiri
    r = re.compile("(.*)( )(.*)")
    # match surumonowo bunkatu
    m = [r.match(x) for x in t1]
    # group(1) wo saiyo
    m3 = [m2.group(1) for m2 in m]
    t2 = [x.replace('-', ' ') for x in m3]

    # decimal nukidasi
    tt = [int(x) for x in data[:, 1]]
    ttt = data[:, 1] - tt - 0.5
    t4 = []
    for i in range(len(ttt)):
        if ttt[i] < 0:
            ttt[i] = ttt[i] + 1
            t4.append(ttt[i])
        elif ttt[i] >= 0:
            t4.append(ttt[i])
    t4 = np.around(t4, decimals=5)
    t6 = [str(x) for x in t4]
    t7 = [x.lstrip('0') for x in t6]
    t7b = [x.ljust(6, '0') for x in t7]
    # time mpc
    t8 = [' C' + t2[0] + x for x in t7b]

    # convert to ra dec
    c = SkyCoord(ra=data[:, 2] * u.degree, dec=data[:, 3] * u.degree)
    # list_radec = c.to_string('hmsdms')
    # list_radec2 = [re.sub(r'[a-z]',' ',x) for x in list_radec]

    rah = [int(x) for x in c.ra.hms[0]]
    rah2 = ["{:02d}".format(x) for x in rah]
    ram = [int(x) for x in c.ra.hms[1]]
    ram2 = ["{:02d}".format(x) for x in ram]
    ras = np.round(c.ra.hms[2], decimals=3)
    # decimal=2
    ras2 = ["{:.2f}".format(x) for x in ras]
    ras3 = [x.rjust(5, '0') for x in ras2]
    decd = c.dec.dms[0]
    tmp = [int(x) for x in decd]
    decd2 = []
    # Revised S.U 2021.9.2
    tmpdec = np.array(c.dec)
    # Revised S.U 2021.8.27
    for i in range(len(tmp)):
        if tmpdec[i] >= 0:
            tmp3 = str(tmp[i])
            tmp2 = '+' + tmp3
            decd2.append(tmp2)
        elif tmpdec[i] > -1 and tmpdec[i] < 0:
            tmp2 = '-0' + "{:01d}".format(tmp[i])
            decd2.append(tmp2)
        else:
            tmp2 = "{:03d}".format(tmp[i])
            decd2.append(tmp2)

    # for i in range(len(tmp)):
    #     if tmp[i] > 0:
    #         tmp3 = str(tmp[i])
    #         tmp2 = '+'+tmp3
    #         decd2.append(tmp2)
    #     else:
    #         tmp2 = "{:03d}".format(tmp[i])
    #         decd2.append(tmp2)
    decd3 = []
    for i in range(len(ras3)):
        tmp5 = ras3[i] + ' ' + decd2[i]
        decd3.append(tmp5)

    decm = [int(abs(x)) for x in c.dec.dms[1]]
    decm2 = ["{:02d}".format(x) for x in decm]
    decs = abs(np.round(c.dec.dms[2], decimals=2))
    decs2 = ["{:.2f}".format(x) for x in decs]
    decs3 = [x.rjust(5, '0') for x in decs2]
    filobs = [x + '      568' for x in fil[:, 0]]
    # mag xy pixel
    data[:, 4][np.isnan(data[:, 4])] = 35.0
    mag2 = ['        ' + "{:.1f}".format(x) for x in data[:, 4]]
    temp = np.r_[name1, t8, rah2, ram2, decd3, decm2, decs3, mag2, filobs]
    temp2 = np.r_[name1, t8, rah2, ram2, decd3, decm2, decs3, mag2, filobs, fil[:, 1], data[:, 4], data[:, 5], data[:, 6], data[:,7]]
    temp3 = np.r_[name1, fil[:, 1], data[:, 6], data[:, 7]]
    # temp = np.r_[name1,t8,rah2,ram2,decd3,decm2,decs3,mag2,fil[:,0],fil[:,1],data[:,4],data[:,5],data[:,6],data[:,7]]
    temp = temp.reshape(9, int(len(temp) / 9))
    temp2 = temp2.reshape(14, int(len(temp2) / 14))
    temp3 = temp3.reshape(4, int(len(temp3) / 4))
    temp = temp.T
    temp2 = temp2.T
    temp3 = temp3.T

    np.savetxt('unknown_mpc_m.txt', temp, fmt="%s")
    np.savetxt('unknown_all_m.txt', temp2, fmt="%s")
    np.savetxt('unknown_disp_m.txt', temp3, fmt="%s")

###
# temp = np.r_[name1,t8,rah2,ram2,decd3,decm2,decs3,mag2,fil[:,0],fil[:,1],data[:,4],data[:,5],data[:,6],data[:,7]]
# temp = temp.reshape(14,int(len(temp)/14))
# temp = temp.T

# np.savetxt('hoge.txt',hoge,fmt=["%s" "%s""%s" "%s""%s" "%s""%s" "%s""%s""%s" "%s""%s" "%s""%s" "%s"])
# np.savetxt('unknown1.txt',temp,fmt="%s")
############# KNOWN ##################
# Revised SU.2021/7/12
if os.stat("match_manual.txt").st_size == 0:
    empty = []
    np.savetxt("karifugo_mpc_m.txt", empty, fmt="%s")
    np.savetxt("karifugo_all_m.txt", empty, fmt="%s")
    np.savetxt("karifugo_disp_m.txt", empty, fmt="%s")
else:
    name = np.loadtxt("match_manual.txt", dtype='str', usecols=[0])
    data = np.loadtxt("match_manual.txt", usecols=[1, 2, 3, 4, 5, 6, 7])
    fil = np.loadtxt("match_manual.txt", dtype='str', usecols=[8, 9])

    result1 = []
    result2 = []
    result3 = []
    for i in range(len(name)):
        ############## karifugo #####################
        name2 = []
        if re.search(r'[a-zA-Z]', str(name[i])):
            # name change to mpc format
            name1 = [x for x in name[i]]
            if len(name1) == 6 and name1[0] == '2':
                name2 = 'K' + name1[2] + name1[3] + name1[4] + '00' + name1[5]
            if len(name1) == 7 and name1[0] == '2':
                name2 = 'K' + name1[2] + name1[3] + name1[4] + '0' + name1[6] + name1[5]
            if len(name1) == 8 and name1[0] == '2':
                name2 = 'K' + name1[2] + name1[3] + name1[4] + name1[6] + name1[7] + name1[5]
            if len(name1) == 9 and name1[0] == '2':
                name3 = name1[6] + name1[7]
                name3 = re.sub(r'^10', 'A', str(name3))
                name3 = re.sub(r'^11', 'B', str(name3))
                name3 = re.sub(r'^12', 'C', str(name3))
                name3 = re.sub(r'^13', 'D', str(name3))
                name3 = re.sub(r'^14', 'E', str(name3))
                name3 = re.sub(r'^15', 'F', str(name3))
                name3 = re.sub(r'^16', 'G', str(name3))
                name3 = re.sub(r'^17', 'H', str(name3))
                name3 = re.sub(r'^18', 'I', str(name3))
                name3 = re.sub(r'^19', 'J', str(name3))
                name3 = re.sub(r'^20', 'K', str(name3))
                name3 = re.sub(r'^21', 'L', str(name3))
                name3 = re.sub(r'^22', 'M', str(name3))
                name3 = re.sub(r'^23', 'N', str(name3))
                name3 = re.sub(r'^24', 'O', str(name3))
                name3 = re.sub(r'^25', 'P', str(name3))
                name3 = re.sub(r'^26', 'Q', str(name3))
                name3 = re.sub(r'^27', 'R', str(name3))
                name3 = re.sub(r'^28', 'S', str(name3))
                name3 = re.sub(r'^29', 'T', str(name3))
                name3 = re.sub(r'^30', 'U', str(name3))
                name3 = re.sub(r'^31', 'V', str(name3))
                name3 = re.sub(r'^32', 'W', str(name3))
                name3 = re.sub(r'^33', 'X', str(name3))
                name3 = re.sub(r'^34', 'Y', str(name3))
                name3 = re.sub(r'^35', 'Z', str(name3))
                name3 = re.sub(r'^36', 'a', str(name3))
                name3 = re.sub(r'^37', 'b', str(name3))
                name3 = re.sub(r'^38', 'c', str(name3))
                name3 = re.sub(r'^39', 'd', str(name3))
                name3 = re.sub(r'^40', 'e', str(name3))
                name3 = re.sub(r'^41', 'f', str(name3))
                name3 = re.sub(r'^42', 'g', str(name3))
                name3 = re.sub(r'^43', 'h', str(name3))
                name3 = re.sub(r'^44', 'i', str(name3))
                name3 = re.sub(r'^45', 'j', str(name3))
                name3 = re.sub(r'^46', 'k', str(name3))
                name3 = re.sub(r'^47', 'l', str(name3))
                name3 = re.sub(r'^48', 'm', str(name3))
                name3 = re.sub(r'^49', 'n', str(name3))
                name3 = re.sub(r'^50', 'o', str(name3))
                name3 = re.sub(r'^51', 'p', str(name3))
                name3 = re.sub(r'^52', 'q', str(name3))
                name3 = re.sub(r'^53', 'r', str(name3))
                name3 = re.sub(r'^54', 's', str(name3))
                name3 = re.sub(r'^55', 't', str(name3))
                name3 = re.sub(r'^56', 'u', str(name3))
                name3 = re.sub(r'^57', 'v', str(name3))
                name3 = re.sub(r'^58', 'w', str(name3))
                name3 = re.sub(r'^59', 'x', str(name3))
                name3 = re.sub(r'^60', 'y', str(name3))
                name3 = re.sub(r'^61', 'z', str(name3))
                name2 = 'K' + name1[2] + name1[3] + name1[4] + name3 + name1[8] + name1[5]
            # print(name2)
            t = Time(data[i, 0], format='jd')
            t1 = t.iso
            # space kugiri
            r = re.compile("(.*)( )(.*)")
            # match surumonowo bunkatu
            m = r.match(t1)
            # group(1) wo saiyo
            m2 = m.group(1)
            t2 = m2.replace('-', ' ')
            # print(name[i],t2)
            # decimal nukidasi
            tt = int(data[i, 0])
            ttt = data[i, 0] - tt - 0.5
            if ttt < 0:
                t4 = ttt + 1
            elif ttt >= 0:
                t4 = ttt
            t4 = np.around(t4, decimals=5)
            t6 = str(t4)
            t7 = t6.lstrip('0')
            t7b = t7.ljust(6, '0')
            # time mpc
            t8 = ' C' + t2 + t7b
            # convert to ra dec
            c = SkyCoord(ra=data[i, 1] * u.degree, dec=data[i, 2] * u.degree)
            # list_radec = c.to_string('hmsdms')
            # list_radec2 = [re.sub(r'[a-z]',' ',x) for x in list_radec]

            rah = int(c.ra.hms[0])
            rah2 = "{:02d}".format(rah)
            ram = int(c.ra.hms[1])
            ram2 = "{:02d}".format(ram)
            ras = np.round(c.ra.hms[2], decimals=3)
            # decimal=2
            # ras2 = "{:.3f}".format(ras)
            ras2 = "{:.2f}".format(ras)
            # ras3 = ras2.rjust(6,'0')
            ras3 = ras2.rjust(5, '0')
            decd = c.dec.dms[0]
            decm = int(c.dec.dms[1])
            decs = np.round(c.dec.dms[2], decimals=2)
            tmp = int(decd)
            # Revised S.U 2021.8.27
            dec = np.array(c.dec)

            if dec > 0:
                tmp3 = str(tmp)
                decd2 = '+' + tmp3
            elif dec > -1 and dec < 0:
                decd2 = '-0' + "{:01d}".format(tmp)
                decm = -1 * decm
                decs = -1 * decs
            else:
                decd2 = "{:03d}".format(tmp)
                decm = -1 * decm
                decs = -1 * decs

            # if tmp > 0:
            #     tmp3 = str(tmp)
            #     decd2 = '+' + tmp3
            # else:
            #     decd2 = "{:03d}".format(tmp)
            #     decm = -1*decm
            #     decs = -1*decs
            # decd3 = ras3+decd2
            decd3 = ras3 + ' ' + decd2
            decm2 = "{:02d}".format(decm)
            decs2 = "{:.2f}".format(decs)
            decs3 = decs2.rjust(5, '0')
            filobs = fil[i, 0] + '      568'

            # mag xy pixel
            mag2 = '        ' + "{:.1f}".format(data[i, 3])
            name3 = '     ' + name2
            temp1 = [name3, t8, rah2, ram2, decd3, decm2, decs3, mag2, filobs]
            temp2 = [name3, t8, rah2, ram2, decd3, decm2, decs3, mag2, filobs, fil[i, 1], data[i, 3], data[i, 4],
                     data[i, 5], data[i, 6]]
            temp3 = [name3, fil[i, 1], data[i, 5], data[i, 6]]
            temp1 = np.r_[temp1]
            temp2 = np.r_[temp2]
            temp3 = np.r_[temp3]
            result1.append(temp1)
            result2.append(temp2)
            result3.append(temp3)
        np.savetxt("karifugo_mpc_m.txt", result1, fmt="%s")
        np.savetxt("karifugo_all_m.txt", result2, fmt="%s")
        np.savetxt("karifugo_disp_m.txt", result3, fmt="%s")
