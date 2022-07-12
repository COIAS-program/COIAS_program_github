#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Access to online Find_Orb.
timestamp: 2022/6/16 08:00 sugiura
"""
import requests
from bs4 import BeautifulSoup
from bs4 import Comment
import subprocess
import traceback
import requests.exceptions
import os

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

    #---extract obsercation arc-----------------------
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

    if os.stat("mpc7.txt").st_size != 0:
        prevObsName = lines[0].split()[0]
        obsList = []
        for l in range(len(lines)):
            if lines[l].split()[0]!= prevObsName or len(lines[l].split())==0 or l==len(lines)-1:
          
                if l==len(lines)-1:
                    obsList.append(lines[l].rstrip("\n"))
                
                findOrbResult = get_imformation_from_findorb_html(request_find_orb(obsList), len(obsList))
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
    completed_process = subprocess.run("dos_find mpc7.txt -k | cut -c 2- > result.txt 2>&1 | tee -a log.txt", shell=True)
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
