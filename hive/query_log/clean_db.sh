#!/bin/bash

tables=(query_log)

ds=$(date +%Y%m%d -d "1 days ago")

for tbl in ${tables[@]};
do
    hive -e "ALTER TABLE $tbl DROP IF EXISTS PARTITION (ds<$ds)"
    prefix="/user/work/rank/$tbl"
    for dir in $(hadoop fs -ls -d $prefix/ds=* | awk '{print $NF}');
    do
        if [[ $dir < "$prefix/ds=$ds" ]]; then
            echo "[REMOVE] "$dir
            hadoop fs -rm -r $dir
        fi
    done
done
