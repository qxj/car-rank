#!/usr/bin/env bash
#
# Copyright (C) 2016 Julian Qian
#
# @file      run.sh
# @author    Julian Qian <junist@gmail.com>
# @created   2016-03-30 08:32:54
#

day=$(date +%Y%m%d -d "yesterday")
if [[ -n $1 ]]; then
    day=$1
fi

input0="rank/query_log/ds=$day"

input=$input0
output="rank/corpus/ds=$day"

echo -e "INPUT: $input\nOUTPUT: $output"

hadoop fs -rm -r $output

hadoop jar /mnt/cloudera/parcels/CDH/lib/hadoop-mapreduce/hadoop-streaming.jar \
    -D mapreduce.job.reduces=1 \
    -D mapreduce.map.output.compress=true \
    -D mapreduce.map.output.compress.codec=org.apache.hadoop.io.compress.SnappyCodec \
    -D mapreduce.output.fileoutputformat.compress=false \
    -D mapreduce.job.name=jqian:corpus:$day \
    -D map.output.key.field.separator=: \
    -D mapreduce.partition.keypartitioner.options=-k1 \
    -input $input \
    -output $output \
    -mapper mapper.py \
    -reducer reducer.py \
    -file ./mapper.py \
    -file ./reducer.py \
    -partitioner org.apache.hadoop.mapred.lib.KeyFieldBasedPartitioner

hive -hiveconf ds=$day -f add_parts.hql
