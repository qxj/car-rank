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
# label                   string
# city_code               string
# user_id                 int
# car_id                  int
# order_id                int
# distance                float
# pos                     int
# page                    int

import sys

def main():
    for line in sys.stdin:
        cols = line.strip().split()
        qid = cols[0]
        label = cols[1]
        pos = int(cols[7])   # [0,14]
        page = int(cols[8])  # [1,\inf)
        if label == "impress" and page > 1:
            sys.stderr.write("reporter:counter:My Counters,Skipped-Impress-Rows,1\n")
            continue
        idx = (page -1) * 15 + pos
        new_id = "%s:%.10d" % (qid, idx)
        # OUTPUT: newid, label, city_code, user_id, car_id, distance
        print new_id + "\t" + "\t".join(cols[1:5]) + "\t" + cols[6]


if __name__ == "__main__":
    main()
