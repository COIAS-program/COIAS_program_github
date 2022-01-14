#!/usr/bin/env python3
# -*- coding: UTF-8 -*

# path_name = os.getcwd()
# detect list
tmp1 = "pre_repo.txt"
tmp2 = "send_mpc.txt"
data1 = open(tmp1, "r")

# all object
lines = data1.readlines()
# identified object

# list of moving object
new_list1 = []
for i in range(len(lines) - 1):
    #    if lines[i][0:12] != lines[i+1][0:12] and lines[i+1][5] == 'H':
    #        print(lines[i])
    # ---K. S. modify 2021/6/17--------------------------------------------------------------------------------------
    if i == 0:
        if lines[i][5:6] == 'H':
            mylist = [word for word in lines[i]]
            mylist[12] = '*'
            newlist = "".join(mylist)
            new_list1.append(newlist)
        else:
            new_list1.append(lines[i])

    if (lines[i][0:12] != lines[i + 1][0:12] and lines[i + 1][5:6] == 'H'):
        #    if lines[i][0:12] != lines[i+1][0:12] and lines[i+1][5:9] == 'H002':

        #        lines[i+1][13].replace(' ','*')
        mylist = [word for word in lines[i + 1]]
        mylist[12] = '*'
        newlist = "".join(mylist)
        new_list1.append(newlist)
    else:
        new_list1.append(lines[i + 1])
#        print(lines[i])
# ---------------------------------------------------------------------------------------------------------------
with open(tmp2, 'wt') as f:
    f.writelines(new_list1)