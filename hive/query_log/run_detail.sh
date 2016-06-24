#!/usr/bin/env bash
#
# Copyright (C) 2016 Julian Qian
#
# @file      run_detail.sh
# @author    Julian Qian <junist@gmail.com>
# @created   2016-06-24 12:15:37
#


day=$1

if [[ -z $day ]]; then
    day=$(date +%Y%m%d -d yesterday)
fi

hive -hiveconf datestr=$day -f query_detail.hql
