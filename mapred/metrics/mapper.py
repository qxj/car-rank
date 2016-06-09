#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; -*-
#
# Copyright (C) 2016 Julian Qian
#
# @file      mapper.py
# @author    Julian Qian <junist@gmail.com>
# @created   2016-03-31 07:42:48
#

import sys


def main():
    for line in sys.stdin:
        cols = line.strip().split()
        qid = cols[0]
        label = cols[1]
        city_code = cols[2]
        pos = int(cols[7])   # [0,14]
        page = int(cols[8])  # [1,\inf)
        algo = cols[9]
        visit_time = cols[10]
        if page > 5:
            sys.stderr.write(
                "reporter:counter:My Counters,Skip Trailing Pages,1\n")
            continue
        # idx starts from zero
        idx = (page - 1) * 15 + pos
        # only clicked items are required
        if label != "impress":
            if label == 'click':
                sys.stderr.write("reporter:counter:My Counters,CV-Click,1\n")
            elif label == 'precheck':
                sys.stderr.write(
                    "reporter:counter:My Counters,CV-Precheck,1\n")
            elif label == 'order':
                sys.stderr.write("reporter:counter:My Counters,CV-Order,1\n")
            else:
                sys.stderr.write("reporter:counter:My Counters,CV-Unknown,1\n")
            print "%s:%.10d\t%s\t%s\t%s\t%s" % (
                qid, idx, label, city_code, algo, visit_time)

if __name__ == "__main__":
    main()
