#!/usr/bin/env bash
# @(#) run.sh  Time-stamp: <Julian Qian 2016-06-14 11:23:05>
# Copyright 2016 Julian Qian
# Author: Julian Qian <junist@gmail.com>
# Version: $Id: run.sh,v 0.1 2016-01-12 11:21:33 jqian Exp $
#

day=$1

if [[ -z $day ]]; then
    day=$(date +%Y%m%d -d yesterday)
fi

# SET hivevar:datestr=$datestr;

if (($day>20160616)); then
    hive -hiveconf datestr=$day -f query_log.hql
else
    echo "before 20160616, apply query_log_0616.hql"
    hive -hiveconf datestr=$day -f query_log_0616.hql
fi

# hive -hiveconf datestr=$day -f query_full_log.hql
