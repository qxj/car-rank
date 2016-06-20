#!/usr/bin/env bash
#
# Copyright (C) 2016 Julian Qian
#
# @file      get_feats.sh
# @author    Julian Qian <junist@gmail.com>
# @created   2016-06-20 09:50:05
#

cd $(dirname $0)

car_id=$1
ds=$2
if [[ -z $ds ]]; then
    ds=$(date +%Y%m%d -d yesterday)
fi

test -z $car_id && echo "car_id is missing" || exit 1

beeline -u jdbc:hive2://stats-hadoop11:10000 \
        --outputformat=vertical \
        --hiveconf ds=$ds \
        --hiveconf car_id=$car_id \
        -f ./get_feats.hql
