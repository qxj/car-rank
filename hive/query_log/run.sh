#!/usr/bin/env bash
# @(#) run.sh  Time-stamp: <Julian Qian 2016-03-31 08:58:55>
# Copyright 2016 Julian Qian
# Author: Julian Qian <junist@gmail.com>
# Version: $Id: run.sh,v 0.1 2016-01-12 11:21:33 jqian Exp $
#

day=$1

if [[ -z $day ]]; then
    day=$(date +%Y%m%d -d yesterday)
fi

# CREATE EXTERNAL TABLE IF NOT EXISTS query_log (
# qid STRING,
# label INT,
# city_code STRING,
# user_id INT,
# car_id INT,
# order_id INT,
# distance FLOAT,
# pos INT,
# page INT,
# visit_time STRING
# )
# PARTITIONED BY (ds STRING)
# ROW FORMAT DELIMITED FIELDS TERMINATED BY '\t';


# SET hivevar:datestr=$datestr;


hive -hiveconf datestr=$day -f query_log.hql

hive -hiveconf datestr=$day -f query_full_log.hql
