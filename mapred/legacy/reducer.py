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
import json

g_ndcg_tolerance = float(os.getenv('ndcg_tolerance', 0.01))


def label2gain(label):
    gain = 0
    if label == "click":
        gain = 2
    elif label == "precheck":
        gain = 7
    elif label == "order":
        gain = 15
    return gain


def cmp_ndcg(ndcg1, ndcg2):
    better = 0
    if ndcg1 - ndcg2 > g_ndcg_tolerance:
        better = -1
        sys.stderr.write("reporter:counter:My Counters,Worse,1\n")
    elif ndcg2 - ndcg1 > g_ndcg_tolerance:
        better = 1
        sys.stderr.write("reporter:counter:My Counters,Better,1\n")
    else:
        sys.stderr.write("reporter:counter:My Counters,Equal,1\n")
    return better


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
    if dn == 0:
        sys.stderr.write("reporter:counter:My Counters,OOPS! Zero divisor,1\n")
        return
    # dcg = \sum_{i=1}^N dcg(i)
    ndcg1 = d1 / dn
    # apply new score
    d2 = 0
    for i, row in enumerate(sorted(
            rows, key=lambda x: x[3], reverse=True)):
        gain = row[2]
        d2 += gain / cmath.log(i + 2, 2).real
    ndcg2 = d2 / dn
    better = cmp_ndcg(ndcg1, ndcg2)
    print "%s\t%f\t%f\t%d\t%s\t%d\t%s" % (qid, ndcg1, ndcg2, better,
                                          city_code, has_date, algo)
    sys.stderr.write("reporter:counter:My Counters,Metrics Counter,1\n")


def main():
    last_info = None
    # decay: some idx do not start from 0?
    decay_qid = None
    rows = []
    for line in sys.stdin:
        cols = line.strip().split('\t')
        qid, idx = cols[0].split(':')
        idx = int(idx)
        data = json.loads(cols[1])
        label = data['label']
        gain = label2gain(label)
        score = float(data['score'])
        city_code = data['city_code']
        has_date = int(data['has_date'])
        algo = data['algo']
        if last_info is None:
            if idx != 0:
                decay_qid = qid
            last_info = (qid, city_code, has_date, algo)
        if last_info[0] != qid:
            deliver(last_info, rows)
            if idx != 0:
                decay_qid = qid
            last_info = (qid, city_code, has_date, algo)
            rows = []
        if decay_qid == qid:
            sys.stderr.write("reporter:counter:My Counters,Decayed Lines,1\n")
            continue
        row = (qid, idx, gain, score)
        rows.append(row)
    if last_info is not None:
        deliver(last_info, rows)


if __name__ == "__main__":
    main()
