#!/usr/bin/env bash
#
# Copyright (C) 2016 Julian Qian
#
# @file      report.sh
# @author    Julian Qian <junist@gmail.com>
# @created   2016-08-16 16:05:29
#

cd $(dirname $0)

START_DS=$1
END_DS=$2

if [[ -z $END_DS ]]; then
    END_DS=$(date +%Y%m%d -d yesterday)
fi

if [[ -z $START_DS ]]; then
    START_DS=$(date +%Y%m%d -d "today -7 days")
fi

TO=qianxiaojun@ppzuche.com

PYTHONPATH=/home/work/pdlib/py python report.py --start $START_DS --end $END_DS --to $TO
