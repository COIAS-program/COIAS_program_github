#!/usr/bin/env python3
# -*- coding: UTF-8 -*
import itertools
import re
import traceback

try:
    # detect list
    tmp1 = "mpc.txt"
    tmp2 = "memo.txt"
    tmp3 = "mpc2.txt"
    data1 = open(tmp1,"r")
    data2 = open(tmp2,"r")

    # all object
    lines = data1.readlines()
    # identified object
    lines2 = data2.readlines()

    # list of moving object
    name_list1 = []
    for i in range(len(lines2)):
        # print(lines[i].strip())
        Hname = 'H'+str(lines2[i].strip()).zfill(6)
        # print(Hname)
        name_list1.append(Hname)

    # remove empty & uniq 
    name_list2 = list(set([x for x in name_list1 if x]))  
    # kokomade Nov.15

    # kensaku name_list2
    new_list =[]
    for j in range(len(name_list2)):
        new_list.append([line for line in lines if name_list2[j] in line])


    # 1jigenka
    new_list2 = list(itertools.chain.from_iterable(new_list))
    new_list2.sort()
    # kokokara Jan.22.2020
    new_list3 = []
    for l in range(len(lines)): 
        if re.match('\w',lines[l]):
            # print(lines[l])
            new_list3.append(lines[l])
        elif re.match('~',lines[l]):
            # print(lines[l])
            new_list3.append(lines[l])
        elif re.match('^     K',lines[l]):
            # print(lines[l])
            new_list3.append(lines[l])
        elif re.match('^     J',lines[l]):
            # print(lines[l])
            new_list3.append(lines[l])
        
    new_list4 = new_list3 + new_list2   
    with open(tmp3,'wt') as f:
        f.writelines(new_list4)

except FileNotFoundError:
    print("Some previous files are not found in prempedit2.py!")
    print(traceback.format_exc())
    error = 1
    errorReason = 64

except Exception:
    print("Some errors occur in prempedit2.py!")
    print(traceback.format_exc())
    error = 1
    errorReason = 65

else:
    error = 0
    errorReason = 64

finally:
    errorFile = open("error.txt","a")
    errorFile.write("{0:d} {1:d} 602 \n".format(error,errorReason))
    errorFile.close()
