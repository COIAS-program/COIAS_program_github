#!/usr/bin/env python3
# -*- coding: UTF-8 -*
import sys
import re
import traceback

try:
    logFile = open("log.txt","a",newline="\n")
    print("prempedit3.py begins")
    logFile.write("prempedit3.py begins\n")

    # cmd = 'cut -b 6-12 mpc2.txt | grep ^H | uniq > hoge.txt'
    # cmd = 'cut -b 6-12 mpc2.txt' 

    # detect list
    tmp1 = "Hlist.txt"
    tmp2 = "mpc2.txt"
    tmp3 = "mpc3.txt"
    data1 = open(tmp1,"r")
    data2 = open(tmp2,"r")

    lines = data1.readlines()
    lines2 = data2.readlines()

    # input first number
    args = sys.argv
    if len(args) <= 1:
        print("Please input the first H number.")
        logFile.write("Please input the first H number.\n")
        raise ValueError
    else:
        # args= [0,0,0]

        # make befor Hlist
        Hlist1 = []
        for i in lines:
            Hlist1.append(i.rstrip('\n'))

        # make after Hlist
        Hlist2 = []
        for k in range(len(lines)):
            k = k + int(args[1])
            Hname = 'H'+str(k).zfill(6)
            Hlist2.append(Hname)

        Hlist3 =[]
        for n in range(len(lines2)):
            for m in range(len(Hlist1)):
                if re.search(Hlist1[m],lines2[n]):
                    tmp = lines2[n].replace(Hlist1[m],Hlist2[m])
                    Hlist3.append(tmp)
    
                    # tmp = lines2[n].replace(Hlist1[m],Hlist2[m])
                    # Hlist3.append()

        # output H conversion list 2022.4.27 K.S.
        fileHConversionList = open("H_conversion_list.txt","w",newline="\n")
        for l in range(len(Hlist1)):
            fileHConversionList.write(Hlist1[l] + ' ' + Hlist2[l] + '\n')
        fileHConversionList.close()


        # kokokara Jan.22.2020
        new_list3 = []
        for l in range(len(lines2)): 
            if re.match('\w',lines2[l]):
                # print(lines[l])
                new_list3.append(lines2[l])
            elif re.match('~',lines2[l]):
                # print(lines[l])
                new_list3.append(lines2[l])
            elif re.match('^     K',lines2[l]):
                # print(lines[l])
                new_list3.append(lines2[l])
            elif re.match('^     J',lines2[l]):
                # print(lines[l])
                new_list3.append(lines2[l])
        
        new_list4 = new_list3 + Hlist3  
        with open(tmp3,'wt') as f:
            f.writelines(new_list4)

        print("prempedit3.py ends")
        logFile.write("prempedit3.py ends\n")
        logFile.close()

except FileNotFoundError:
    print("Some previous files are not found in prempedit3.py!")
    print(traceback.format_exc())
    error = 1
    errorReason = 64

except Exception:
    print("Some errors occur in prempedit3.py!")
    print(traceback.format_exc())
    error = 1
    errorReason = 65

else:
    error = 0
    errorReason = 64

finally:
    errorFile = open("error.txt","a")
    errorFile.write("{0:d} {1:d} 604 \n".format(error,errorReason))
    errorFile.close()
