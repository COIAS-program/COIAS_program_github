#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re

import numpy as np
from astropy import units as u
from astropy.coordinates import SkyCoord
from astropy.time import Time

############# KNOWN ##################
# Revised SU. 2021/7/12
if os.stat("match_manual.txt").st_size == 0:
    empty = []
    np.savetxt('numbered_mpc_m.txt', empty, fmt="%s")
    np.savetxt('numbered_all_m.txt', empty, fmt="%s")
    np.savetxt('numbered_disp_m.txt', empty, fmt="%s")
else:
    name = np.loadtxt("match_manual.txt", dtype='str', usecols=[0])
    data = np.loadtxt("match_manual.txt", usecols=[1, 2, 3, 4, 5, 6, 7])
    # nan <= 35.0
    data[:, 3][np.isnan(data[:, 3])] = 35.0
    fil = np.loadtxt("match_manual.txt", dtype='str', usecols=[8, 9])

    result1 = []
    result2 = []
    result3 = []
    for i in range(len(name)):
        ############## karifugo #####################
        name2 = []
        if re.search(r'[a-zA-Z]', str(name[i])):
            pass
        ################# numbered ##################
        else:
            name1 = int(name[i])
            ################ over 100000 ####################
            if name1 >= 100000:
                #        print(re.findall(r'^..',str(name1[i])))
                #        tmp1 = re.findall(r'^..',str(name[i][i]))
                name[i] = re.sub(r'^10', 'A', str(name[i]))
                name[i] = re.sub(r'^11', 'B', str(name[i]))
                name[i] = re.sub(r'^12', 'C', str(name[i]))
                name[i] = re.sub(r'^13', 'D', str(name[i]))
                name[i] = re.sub(r'^14', 'E', str(name[i]))
                name[i] = re.sub(r'^15', 'F', str(name[i]))
                name[i] = re.sub(r'^16', 'G', str(name[i]))
                name[i] = re.sub(r'^17', 'H', str(name[i]))
                name[i] = re.sub(r'^18', 'I', str(name[i]))
                name[i] = re.sub(r'^19', 'J', str(name[i]))
                name[i] = re.sub(r'^20', 'K', str(name[i]))
                name[i] = re.sub(r'^21', 'L', str(name[i]))
                name[i] = re.sub(r'^22', 'M', str(name[i]))
                name[i] = re.sub(r'^23', 'N', str(name[i]))
                name[i] = re.sub(r'^24', 'O', str(name[i]))
                name[i] = re.sub(r'^25', 'P', str(name[i]))
                name[i] = re.sub(r'^26', 'Q', str(name[i]))
                name[i] = re.sub(r'^27', 'R', str(name[i]))
                name[i] = re.sub(r'^28', 'S', str(name[i]))
                name[i] = re.sub(r'^29', 'T', str(name[i]))
                name[i] = re.sub(r'^30', 'U', str(name[i]))
                name[i] = re.sub(r'^31', 'V', str(name[i]))
                name[i] = re.sub(r'^32', 'W', str(name[i]))
                name[i] = re.sub(r'^33', 'X', str(name[i]))
                name[i] = re.sub(r'^34', 'Y', str(name[i]))
                name[i] = re.sub(r'^35', 'Z', str(name[i]))
                name[i] = re.sub(r'^36', 'a', str(name[i]))
                name[i] = re.sub(r'^37', 'b', str(name[i]))
                name[i] = re.sub(r'^38', 'c', str(name[i]))
                name[i] = re.sub(r'^39', 'd', str(name[i]))
                name[i] = re.sub(r'^40', 'e', str(name[i]))
                name[i] = re.sub(r'^41', 'f', str(name[i]))
                name[i] = re.sub(r'^42', 'g', str(name[i]))
                name[i] = re.sub(r'^43', 'h', str(name[i]))
                name[i] = re.sub(r'^44', 'i', str(name[i]))
                name[i] = re.sub(r'^45', 'j', str(name[i]))
                name[i] = re.sub(r'^46', 'k', str(name[i]))
                name[i] = re.sub(r'^47', 'l', str(name[i]))
                name[i] = re.sub(r'^48', 'm', str(name[i]))
                name[i] = re.sub(r'^49', 'n', str(name[i]))
                name[i] = re.sub(r'^50', 'o', str(name[i]))
                name[i] = re.sub(r'^51', 'p', str(name[i]))
                name[i] = re.sub(r'^52', 'q', str(name[i]))
                name[i] = re.sub(r'^53', 'r', str(name[i]))
                name[i] = re.sub(r'^54', 's', str(name[i]))
                name[i] = re.sub(r'^55', 't', str(name[i]))
                name[i] = re.sub(r'^56', 'u', str(name[i]))
                name[i] = re.sub(r'^57', 'v', str(name[i]))
                name[i] = re.sub(r'^58', 'w', str(name[i]))
                name[i] = re.sub(r'^59', 'x', str(name[i]))
                name[i] = re.sub(r'^60', 'y', str(name[i]))
                name[i] = re.sub(r'^61', 'z', str(name[i]))
                #           print(name[i])

                t = Time(data[i, 0], format='jd')
                t1 = t.iso
                # space kugiri
                r = re.compile("(.*)( )(.*)")
                # match surumonowo bunkatu
                m = r.match(t1)
                # group(1) wo saiyo
                m2 = m.group(1)
                t2 = m2.replace('-', ' ')
                #        print(name[i][i],t2)
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
                t8 = '        C' + t2 + t7b

                # convert to ra dec
                c = SkyCoord(ra=data[i, 1] * u.degree, dec=data[i, 2] * u.degree)
                # list_radec = c.to_string('hmsdms')
                # list_radec2 = [re.sub(r'[a-z]',' ',x) for x in list_radec]

                rah = int(c.ra.hms[0])
                rah2 = "{:02d}".format(rah)
                ram = int(c.ra.hms[1])
                ram2 = "{:02d}".format(ram)
                ras = np.round(c.ra.hms[2], decimals=2)
                # decimal=2
                ras2 = "{:.2f}".format(ras)
                ras3 = ras2.rjust(5, '0')
                #            ras3 = ras2.rjust(4,'0')
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

                #                if tmp > 0:
                #                    tmp3 = str(tmp)
                #                    decd2 = '+' + tmp3
                #                else:
                #                    decd2 = "{:03d}".format(tmp)
                #                    decm = -1*decm
                #                    decs = -1*decs
                decd3 = ras3 + ' ' + decd2
                decm2 = "{:02d}".format(decm)
                decs2 = "{:.2f}".format(decs)
                decs3 = decs2.rjust(5, '0')
                filobs = fil[i, 0] + '      568'

                #            decm = int(c.dec.dms[1])
                #            decs = np.round(c.ra.dms[2],decimals=2)
                #            decs2 =  "{:.2f}".format(decs)

                # mag xy pixel
                mag2 = '        ' + "{:.1f}".format(data[i, 3])
                temp1 = [name[i], t8, rah2, ram2, decd3, decm2, decs3, mag2, filobs]
                temp2 = [name[i], t8, rah2, ram2, decd3, decm2, decs3, mag2, filobs, fil[i, 1], data[i, 3], data[i, 4],
                         data[i, 5], data[i, 6]]
                temp3 = [name[i], fil[i, 1], data[i, 5], data[i, 6]]
                temp1 = np.r_[temp1]
                temp2 = np.r_[temp2]
                temp3 = np.r_[temp3]

            ################ under 100000 over 10000 ####################
            ###########revised 2020.2.5 #####################
            if name1 < 100000 and name1 >= 10000:
                t = Time(data[i, 0], format='jd')
                t1 = t.iso
                # space kugiri
                r = re.compile("(.*)( )(.*)")
                # match surumonowo bunkatu
                m = r.match(t1)
                # group(1) wo saiyo
                m2 = m.group(1)
                t2 = m2.replace('-', ' ')
                #        print(name[i][i],t2)
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
                t8 = '        C' + t2 + t7b

                # convert to ra dec
                c = SkyCoord(ra=data[i, 1] * u.degree, dec=data[i, 2] * u.degree)
                # list_radec = c.to_string('hmsdms')
                # list_radec2 = [re.sub(r'[a-z]',' ',x) for x in list_radec]

                rah = int(c.ra.hms[0])
                rah2 = "{:02d}".format(rah)
                ram = int(c.ra.hms[1])
                ram2 = "{:02d}".format(ram)
                ras = np.round(c.ra.hms[2], decimals=2)
                # decimal=2
                ras2 = "{:.2f}".format(ras)
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

                #               if tmp > 0:
                #                   tmp3 = str(tmp)
                #                   decd2 = '+' + tmp3
                #               else:
                #                   decd2 = "{:03d}".format(tmp)
                #                   decm = -1*decm
                #                   decs = -1*decs
                decd3 = ras3 + ' ' + decd2
                decm2 = "{:02d}".format(decm)
                decs2 = "{:.2f}".format(decs)
                decs3 = decs2.rjust(5, '0')
                filobs = fil[i, 0] + '      568'

                #            decm = int(c.dec.dms[1])
                #            decs = np.round(c.ra.dms[2],decimals=2)
                #            decs2 =  "{:.2f}".format(decs)

                # mag xy pixel
                mag2 = '        ' + "{:.1f}".format(data[i, 3])
                temp1 = [name[i], t8, rah2, ram2, decd3, decm2, decs3, mag2, filobs]
                temp2 = [name[i], t8, rah2, ram2, decd3, decm2, decs3, mag2, filobs, fil[i, 1], data[i, 3], data[i, 4],
                         data[i, 5], data[i, 6]]
                temp3 = [name[i], fil[i, 1], data[i, 5], data[i, 6]]
                temp1 = np.r_[temp1]
                temp2 = np.r_[temp2]
                temp3 = np.r_[temp3]

            # revised 2020.2.5
            ############### under 10000 over 1000 ####################
            if name1 < 10000 and name1 >= 1000:
                t = Time(data[i, 0], format='jd')
                t1 = t.iso
                # space kugiri
                r = re.compile("(.*)( )(.*)")
                # match surumonowo bunkatu
                m = r.match(t1)
                # group(1) wo saiyo
                m2 = m.group(1)
                t2 = m2.replace('-', ' ')
                #        print(name[i][i],t2)
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
                t8 = '         C' + t2 + t7b

                # convert to ra dec
                c = SkyCoord(ra=data[i, 1] * u.degree, dec=data[i, 2] * u.degree)
                # list_radec = c.to_string('hmsdms')
                # list_radec2 = [re.sub(r'[a-z]',' ',x) for x in list_radec]

                rah = int(c.ra.hms[0])
                rah2 = "{:02d}".format(rah)
                ram = int(c.ra.hms[1])
                ram2 = "{:02d}".format(ram)
                ras = np.round(c.ra.hms[2], decimals=2)
                # decimal=2
                ras2 = "{:.2f}".format(ras)
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

                #                if tmp > 0:
                #                    tmp3 = str(tmp)
                #                    decd2 = '+' + tmp3
                #                else:
                #                    decd2 = "{:03d}".format(tmp)
                #                    decm = -1*decm
                #                    decs = -1*decs
                decd3 = ras3 + ' ' + decd2
                decm2 = "{:02d}".format(decm)
                decs2 = "{:.2f}".format(decs)
                decs3 = decs2.rjust(5, '0')
                filobs = fil[i, 0] + '      568'

                #            decm = int(c.dec.dms[1])
                #            decs = np.round(c.ra.dms[2],decimals=2)
                #            decs2 =  "{:.2f}".format(decs)

                # mag xy pixel
                mag2 = '        ' + "{:.1f}".format(data[i, 3])
                temp1 = [name[i], t8, rah2, ram2, decd3, decm2, decs3, mag2, filobs]
                temp2 = [name[i], t8, rah2, ram2, decd3, decm2, decs3, mag2, filobs, fil[i, 1], data[i, 3], data[i, 4],
                         data[i, 5], data[i, 6]]
                temp3 = [name[i], fil[i, 1], data[i, 5], data[i, 6]]
                temp1 = np.r_[temp1]
                temp2 = np.r_[temp2]
                temp3 = np.r_[temp3]
            ############### under 10000 over 1000 ####################
            if name1 < 1000 and name1 >= 100:
                t = Time(data[i, 0], format='jd')
                t1 = t.iso
                # space kugiri
                r = re.compile("(.*)( )(.*)")
                # match surumonowo bunkatu
                m = r.match(t1)
                # group(1) wo saiyo
                m2 = m.group(1)
                t2 = m2.replace('-', ' ')
                #        print(name[i][i],t2)
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
                t8 = '          C' + t2 + t7b

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
                ras2 = "{:.3f}".format(ras)
                ras3 = ras2.rjust(6, '0')
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

                #                if tmp > 0:
                #                    tmp3 = str(tmp)
                #                    decd2 = '+' + tmp3
                #                else:
                #                    decd2 = "{:03d}".format(tmp)
                #                    decm = -1*decm
                #                    decs = -1*decs
                decd3 = ras3 + decd2
                decm2 = "{:02d}".format(decm)
                decs2 = "{:.2f}".format(decs)
                decs3 = decs2.rjust(5, '0')
                filobs = fil[i, 0] + '      568'

                #            decm = int(c.dec.dms[1])
                #            decs = np.round(c.ra.dms[2],decimals=2)
                #            decs2 =  "{:.2f}".format(decs)

                # mag xy pixel
                mag2 = '        ' + "{:.1f}".format(data[i, 3])
                temp1 = [name[i], t8, rah2, ram2, decd3, decm2, decs3, mag2, filobs]
                temp2 = [name[i], t8, rah2, ram2, decd3, decm2, decs3, mag2, filobs, fil[i, 1], data[i, 3], data[i, 4],
                         data[i, 5], data[i, 6]]
                temp3 = [name[i], fil[i, 1], data[i, 5], data[i, 6]]
                temp1 = np.r_[temp1]
                temp2 = np.r_[temp2]
                temp3 = np.r_[temp3]

            # negligible under 100

            result1.append(temp1)
            result2.append(temp2)
            result3.append(temp3)
        np.savetxt('numbered_mpc_m.txt', result1, fmt="%s")
        np.savetxt('numbered_all_m.txt', result2, fmt="%s")
        np.savetxt('numbered_disp_m.txt', result3, fmt="%s")