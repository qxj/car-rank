#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; -*-
#
# Copyright (C) 2016 Julian Qian
#
# @file      mapper.py
# @author    Julian Qian <junist@gmail.com>
# @created   2016-03-30 08:21:09
#


# hive> desc query_log;
# OK
# qid                     string
# pos                     int
# page                    int
# label                   string
# city_code               string
# user_id                 int
# car_id                  int
# order_id                int
# distance                float

import sys
import os

import zipimport
imp = zipimport.zipimporter('utils.mod')
utils = imp.load_module('utils')
from utils import table


def main():
    td = table.TableMeta('query_log.desc')
    strict = True if os.getenv('strict_mode') == "1" else False
    max_page = int(os.getenv('max_page', 20))
    for line in sys.stdin:
        cols = line.strip().split('\t')
        row = td.fields(cols)
        qid = row['qid']
        pos = row['pos']        # [0,14]
        page = row['page']      # [1,\inf)
        label = row['label']
        distance = row['distance']
        has_date = row['has_date']
        # TODO feature engineering
        others = cols[3:]

        if page > max_page:
            sys.stderr.write(
                "reporter:counter:My Counters,Skip >%d Pages,1\n" % max_page)
            continue
        if distance is None:
            sys.stderr.write(
                "reporter:counter:My Counters,NoneType Distance,1\n")
            continue
        if strict:
            if label == "impress" and page > 2:
                sys.stderr.write(
                    "reporter:counter:My Counters,Skipped-Impress-Rows,1\n")
                continue
            if has_date != '1':
                sys.stderr.write(
                    "reporter:counter:My Counters,Not Select Date,1\n")
                continue
        idx = (page - 1) * 15 + pos
        new_id = "%s:%.10d" % (qid, idx)
        # OUTPUT: newid, label, city_code, user_id, car_id, distance
        print new_id + "\t" + "\t".join(others)


if __name__ == "__main__":
    main()
