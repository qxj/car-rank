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
import datetime


def read_desc(desc_file):
    fields = []
    with open(desc_file) as fp:
        for line in fp:
            cols = line.strip().split()
            if len(cols) != 2:
                break
            fields.append(cols)
    return fields

g_fields = read_desc('query_log.desc')


def cols2fields(cols):
    rets = {}
    for i, item in enumerate(cols):
        field, ftype = g_fields[i]
        if item in ("\\N", "NULL"):
            item = None
        elif ftype in ('int', 'tinyint'):
            item = int(item)
        elif ftype in ('bigint', ):
            item = datetime.datetime.fromtimestamp(int(item) / 1000)
        elif ftype in ('float', 'double'):
            item = float(item)
        rets[field] = item
    return rets


def main():
    strict = os.getenv('strict_filter')
    for line in sys.stdin:
        cols = line.strip().split('\t')
        row = cols2fields(cols)
        qid = row['qid']
        pos = row['pos']        # [0,14]
        page = row['page']      # [1,\inf)
        label = row['label']
        has_date = row['has_date']
        # TODO feature engineering
        others = cols[3:]

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
