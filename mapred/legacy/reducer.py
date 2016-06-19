#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; -*-
#
# Copyright (C) 2016 Julian Qian
#
# @file      reducer.py
# @author    Julian Qian <junist@gmail.com>
# @created   2016-06-14 12:14:56
#

from __future__ import division
import sys
import os
import cmath

g_ndcg_tolerance = float(os.getenv('ndcg_tolerance'))


def label2gain(label):
    gain = 0
    if label == "click":
        gain = 1
    elif label == "precheck":
        gain = 7
    elif label == "order":
        gain = 15
    return gain


# qid for debug
def deliver(info, rows):
    qid, city_code, has_date, algo = info
    d1 = 0
    dn = 0
    for i, row in enumerate(rows):
        idx = row[1]
        gain = row[2]
        # dcg(i) = gain_i / discount_i
        d1 += gain / cmath.log(idx + 2, 2).real
    for i, row in enumerate(sorted(
            rows, key=lambda x: x[2], reverse=True)):
        gain = row[2]
        # idcg(i)
        dn += gain / cmath.log(i + 2, 2).real
    # dcg = \sum_{i=1}^N dcg(i)
    ndcg1 = d1 / dn
    # apply new score
    d2 = 0
    for i, row in enumerate(sorted(
            rows, key=lambda x: x[3], reverse=True)):
        gain = row[2]
        d2 += gain / cmath.log(i + 2, 2).real
    ndcg2 = d2 / dn
    better = 0
    if ndcg1 - ndcg2 > g_ndcg_tolerance:
        better = -1
        sys.stderr.write("reporter:counter:My Counters,Worse,1\n")
    elif ndcg2 - ndcg1 > g_ndcg_tolerance:
        better = 1
        sys.stderr.write("reporter:counter:My Counters,Better,1\n")
    else:
        sys.stderr.write("reporter:counter:My Counters,Equal,1\n")
    print "%s\t%f\t%f\t%d\t%s\t%d\t%s" % (qid, ndcg1, ndcg2, better,
                                          city_code, has_date, algo)


def main():
    last_info = None
    rows = []
    for line in sys.stdin:
        cols = line.strip().split('\t')
        qid, idx = cols[0].split(':')
        idx = int(idx)
        label = cols[1]
        gain = label2gain(label)
        score = float(cols[2])
        city_code = cols[3]
        has_date = cols[4]
        algo = cols[5]
        if not last_info:
            last_info = (qid, city_code, has_date, algo)
        if last_info[0] != qid:
            deliver(last_info, rows)
            last_info = (qid, city_code, has_date, algo)
            rows = []
        row = (qid, idx, gain, score)
        rows.append(row)
    deliver(last_info, rows)


if __name__ == "__main__":
    main()
