#!/bin/sh
array=(`ls -ald $(find "$1") | awk '$1 !~ /d/ {print $9 }'`)
for var in ${array[@]}
do
    var=`printf ${var}`
    echo $var
    git update-index --assume-unchanged $var
done