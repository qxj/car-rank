#!/usr/bin/env bash
#
# Copyright (C) 2016 Julian Qian
#
# @file      run.sh
# @author    Julian Qian <junist@gmail.com>
# @created   2016-06-13 16:13:50
#

set -e -o pipefail

day=$(date +%Y%m%d -d "yesterday")
if [[ -n $1 ]]; then
    day=$1
fi

if [[ -z $DB_EXIST ]]; then
    echo "Create temp.legacy in ds=$day ..."

    hive -hiveconf datestr=$day -f temp.legacy.hql

    hive -e "desc temp.legacy" > legacy.desc
fi

input0="/user/hive/temp/legacy"

input=$input0
output="rank/legacy/ds=$day"

echo -e "INPUT: $input\nOUTPUT: $output"

hadoop fs -rm -r -f $output

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
    -file ../utils.mod \
    -file ./legacy.desc \
    -cmdenv ndcg_tolerance=0.01 \
    -partitioner org.apache.hadoop.mapred.lib.KeyFieldBasedPartitioner

hive -hiveconf ds=$day -f add_part.hql
