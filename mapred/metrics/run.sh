#!/usr/bin/env bash
#
# Copyright (C) 2016 Julian Qian
#
# @file      run.sh
# @author    Julian Qian <junist@gmail.com>
# @created   2016-03-31 02:55:18
#

day=$(date +%Y%m%d -d "yesterday")
if [[ -n $1 ]]; then
    day=$1
fi

input0="rank/query_log/ds=$day"

input=$input0
output="rank/metrics/ds=$day"

echo "INPUT: $input\nOUTPUT: $output"

hadoop fs -rm -r $output

hadoop jar /mnt/cloudera/parcels/CDH/lib/hadoop-mapreduce/hadoop-streaming.jar \
    -D mapreduce.job.reduces=1 \
    -D mapreduce.map.output.compress=true \
    -D mapreduce.map.output.compress.codec=org.apache.hadoop.io.compress.SnappyCodec \
    -D mapreduce.output.fileoutputformat.compress=false \
    -D mapreduce.job.name="jqian:$output" \
    -D map.output.key.field.separator=: \
    -D mapreduce.partition.keypartitioner.options=-k1 \
    -partitioner org.apache.hadoop.mapred.lib.KeyFieldBasedPartitioner \
    -input $input \
    -output $output \
    -mapper mapper.py \
    -reducer reducer.py \
    -file ./mapper.py \
    -file ./reducer.py

hive -hiveconf ds=$day -f add_part.hql
