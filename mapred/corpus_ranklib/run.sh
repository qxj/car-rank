#!/usr/bin/env bash
#
# Copyright (C) 2016 Julian Qian
#
# @file      run.sh
# @author    Julian Qian <junist@gmail.com>
# @created   2016-07-03 16:52:49
#


day=$(date +%Y%m%d -d "yesterday")
if [[ -n $1 ]]; then
    day=$1
fi

hive -hiveconf datestr=$day -f temp.corpus_rl.hql

hive -e "desc temp.corpus_rl" > corpus_rl.desc

input0="/user/hive/temp/corpus_rl"

input=$input0
output="rank/corpus_rl/ds=$day"

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
    -file ../utils.mod \
    -file ./corpus_rl.desc \
    -file ./feats.desc \
    -partitioner org.apache.hadoop.mapred.lib.KeyFieldBasedPartitioner
