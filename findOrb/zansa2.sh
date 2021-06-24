#!/bin/bash

#var1 = 1
#echo $#
#if [$# -lt $var1] ; then
#    echo "you need mpc_format.txt"
#fi

#echo $1

cat result.txt  |awk '$15 > 1.0 ||$15<-1.0 || $16 >1.0 || $16 < -1.0 {print $0}' > tmp.txt
cat tmp.txt |awk '$5 != '2015' {print $0}' > tmp2.txt
cat tmp2.txt |awk '$6 != '2015' {print $0}' > checklist.txt
