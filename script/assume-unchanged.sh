#!/bin/bash
array=(`ls -ald $(find "$1") | awk '$1 !~ /d/ {print $9 }'`)
for var in ${array[@]}
do
    var=`printf ${var}`
    echo $var
    git update-index --assume-unchanged $var
done

# https://qiita.com/yakimeron/items/f308368c5949b485e50f