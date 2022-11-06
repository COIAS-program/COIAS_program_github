#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Timestamp: 2022/08/06 19:30 sugiura
############################################################################################
# mpc7.txtに記載の検出・測定天体の位置情報を読み込み, findorbにその位置情報から予想される軌道を計算させ,
# その軌道と位置情報の残差(residual)を計算させる.
# これによって各天体の測定が妥当であるかどうかを評価したり, 残差の大きすぎるデータ点を除去したりできる.
# ネットに繋がれている場合はウェブ版のfindorbに位置情報を送って軌道および残差を計算させる.
# この場合は軌道要素の誤差やサイズなどの情報まで返してくれるので,
# 詳細な情報をorbital_elements_summary_web.txtに書き出す.
# 一方でネットに繋がれていない時やウェブ版findorbの使用中にタイムアウトが発生した時などは,
# 10年ほど前にスペースガード協会の方が手を入れたコマンドライン版findorbを使用する.
# これはバージョンが古く軌道の誤差や天体サイズまで出力できないので, 残差のみを計算する.
# (一応軌道情報はorbital_elements_summary.txtに書き出されるが, 誤差が無いので当てにならない)
#
# 入力: mpc7.txt
# 出力: result.txt
# 　　    書式: MPC 80カラムフォーマット | X方向の残差[arcsec] Y方向の残差[arcsec]
# 　　  orbital_elements_summary_web.txt (ウェブ版findorbに正しく問い合わせをできた天体のみ)
# 　　    各天体の軌道長半径a, 離心率e, 傾斜角i, Earth MOIDS, サイズ, 観測アークを書き出したもの
############################################################################################
import requests
from bs4 import BeautifulSoup
from bs4 import Comment
import subprocess
import traceback
import requests.exceptions
import os
import print_progress
from def_coias_data_path import *

### FUNCTIONS #######################################################
def request_find_orb(mpcformat, orbit_type=-2):
    """
    Parameters
    ----------
    mpcformat : list
    list of mpcformat
    orbit_type : int
    integer of orbit type defined in Find_Orb
    (-2:AUTO, -1:Barycentric,3:Geocentric)
    """
    pluto_url = u'https://www.projectpluto.com/cgi-bin/fo/fo_serve.cgi'
    params = dict(
      TextArea="\n".join(mpcformat),
      stepsize="1",
      faint_limit="99",
      ephem_type="0",
      sigmas="on",
      motion="0",
      element_center=orbit_type,
      epoch="default",
      resids="0",
      language="e"
    )
    r = requests.post(pluto_url, data=params)

    return r.text
  
def get_imformation_from_findorb_html(htmlDocument, ndata):
    soup = BeautifulSoup(htmlDocument, features="lxml")

    #---extract a, e, i-------------------------------
    orbElemStrList = soup.find("a",href="https://www.projectpluto.com/mpec_xpl.htm#elems").next_sibling.split("\n")

    ## hyperbolic orbit or insane observations
    if orbElemStrList[3][0]=='q':
        retDict = {"None":None}
        return retDict

    ## large error
    if orbElemStrList[5].split()[2]!="+/-":
        a = orbElemStrList[5].split()[1]
        da = "largeError"
        e = orbElemStrList[6].split()[1]
        de = "largeError"
        i = orbElemStrList[6].split()[3]
        di = "largeError"
    ## small error
    else:
        a = orbElemStrList[5].split()[1]
        da = orbElemStrList[5].split()[3]
        e = orbElemStrList[6].split()[1]
        de = orbElemStrList[6].split()[3]
        i = orbElemStrList[6].split()[5]
        di = orbElemStrList[6].split()[7]
    #-------------------------------------------------

    #---extract MOIDs: Ea-----------------------------
    comments = soup.find_all(string=lambda text: isinstance(text, Comment))
    for c in comments:
        if c.split()[0]=="MOIDs:" and c.split()[1]=="Me":
            MOIDsEa = c.split()[6]
    #-------------------------------------------------

    #---extract size sentence-------------------------
    sizeSentence = soup.find("a",href="https://www.minorplanetcenter.net/iau/lists/Sizes.html")["title"]+"\n"
    #-------------------------------------------------

    #---extract observation arc-----------------------
    ## large error
    if orbElemStrList[5].split()[2]!="+/-":
        obsArcSentence = soup.find("a",href="https://www.minorplanetcenter.net/iau/lists/Sizes.html").next_sibling.split("\n")[1]+"\n"
    ## small error
    else:
        obsArcSentence = soup.find("a",href="https://www.minorplanetcenter.net/iau/lists/Sizes.html").next_sibling.split("\n")[2]+"\n"
    #-------------------------------------------------

    #---extract residuals-----------------------------
    residuals = []
    for n in range(ndata):
        hrefStr = "#o"+str(n+1).rjust(3,'0')
        residOrgs = soup.find("a",href=hrefStr).next_sibling.next_sibling.next_sibling.replace("(", "").replace(")","").split()
        residX = residOrgs[0][len(residOrgs[0])-1]+"{0:.2f}".format(float(residOrgs[0][0:len(residOrgs[0])-1]))
        residY = residOrgs[1][len(residOrgs[1])-1]+"{0:.2f}".format(float(residOrgs[1][0:len(residOrgs[1])-1]))
        residuals.append([residX, residY])
    #-------------------------------------------------

    orbElemSentence = "a=" + a + "+/-" + da + " e=" + e + "+/-" + de + " i=" + i + "+/-" + di + " MOIDs:Ea=" + MOIDsEa + "\n"
    retDict = {"orbElemSentence":orbElemSentence, "sizeSentence":sizeSentence, "obsArcSentence":obsArcSentence, "residuals":residuals}
    return(retDict)
#######################################################################


### MAIN PART #########################################################
try:
    f = open("mpc7.txt","r")
    lines = f.readlines()
    f.close()

    fResult  = open("result.txt","w",newline="\n")
    fOrbElem = open("orbital_elements_summary_web.txt","w",newline="\n")

    errorCount=0
    if os.stat("mpc7.txt").st_size != 0:
        prevObsName = lines[0].split()[0]
        obsList = []
        for l in range(len(lines)):
            print_progress.print_progress(nCheckPointsForLoop=9, nForLoop=len(lines), currentForLoop=l)
            
            if lines[l].split()[0]!= prevObsName or len(lines[l].split())==0 or l==len(lines)-1:
          
                if l==len(lines)-1:
                    obsList.append(lines[l].rstrip("\n"))

                while True:
                    try:
                        findOrbResult = get_imformation_from_findorb_html(request_find_orb(obsList), len(obsList))
                    except requests.exceptions.ConnectionError:
                        print("Failed to access to online findOrb. Ntry={0:d}. Try again.".format(errorCount))
                        errorCount+=1
                        if errorCount>=20:
                            raise requests.exceptions.ConnectionError
                    except Exception:
                        raise Exception
                    else:
                        break
                        
                if "None" not in findOrbResult:

                    if len(prevObsName)==5:
                        fOrbElem.write(prevObsName.ljust(12) + ": " + findOrbResult["orbElemSentence"])
                        fOrbElem.write("              " + findOrbResult["sizeSentence"])
                        fOrbElem.write("              " + findOrbResult["obsArcSentence"])
                        
                    elif len(prevObsName)==7:
                        fOrbElem.write(prevObsName.ljust(7) + ": " + findOrbResult["orbElemSentence"])
                        fOrbElem.write("         " + findOrbResult["sizeSentence"])
                        fOrbElem.write("         " + findOrbResult["obsArcSentence"])
                
                    for o in range(len(obsList)):
                        fResult.write(obsList[o] + " |" + findOrbResult["residuals"][o][0].rjust(10) + findOrbResult["residuals"][o][1].rjust(10) + "\n")

                    obsList = [lines[l].rstrip("\n")]
                    
            else:
                obsList.append(lines[l].rstrip("\n"))

            prevObsName = lines[l].split()[0]

        fResult.close()
        fOrbElem.close()

except requests.exceptions.ConnectionError:
    print("You do not connect to the internet in findorb.py. We try desktop findorb.")
    completed_process = subprocess.run(f"dos_find mpc7.txt -k {coiasDataPath} | cut -c 2- > result.txt 2>&1 | tee -a log.txt", shell=True)
    if completed_process.returncode!=0:
        error = 1
    else:
        error = 0
    errorReason = 75

except FileNotFoundError:
    print("Some previous files are not found in findorb.py!")
    print(traceback.format_exc())
    error = 1
    errorReason = 74

except Exception:
    print("Some errors occur in findorb.py!")
    print(traceback.format_exc())
    error = 1
    errorReason = 75

else:
    error = 0
    errorReason = 74

finally:
    errorFile = open("error.txt","a")
    errorFile.write("{0:d} {1:d} 704 \n".format(error,errorReason))
    errorFile.close()
#######################################################################
