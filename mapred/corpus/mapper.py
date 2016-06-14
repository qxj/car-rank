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


def main():
    strict = os.getenv('strict_filter')
    for line in sys.stdin:
        cols = line.strip().split()
        qid = cols[0]
        pos = int(cols[1])   # [0,14]
        page = int(cols[2])  # [1,\inf)
        label = cols[3]
        has_date = cols[11]
        # TODO feature engineering
        others = cols[3:]
        # station
        try:
            if others[15] in ("NULL", '\N'):
                others[15] = 0
            else:
                others[15] = 1
        except:
            sys.stderr.write(
                "reporter:counter:My Counters,Others 15th Missing,1\n")

        if page > 3:
            sys.stderr.write(
                "reporter:counter:My Counters,Skip Trailing Pages,1\n")
            continue
        if strict and label == "impress" and page > 2:
            sys.stderr.write(
                "reporter:counter:My Counters,Skipped-Impress-Rows,1\n")
            continue
        if strict and has_date != '1':
            sys.stderr.write(
                "reporter:counter:My Counters,Not Select Date,1\n")
            continue
        idx = (page - 1) * 15 + pos
        new_id = "%s:%.10d" % (qid, idx)
        # OUTPUT: newid, label, city_code, user_id, car_id, distance
        print new_id + "\t" + "\t".join(others)


if __name__ == "__main__":
    main()
