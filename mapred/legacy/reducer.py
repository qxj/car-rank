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
import cmath


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
def deliver(qid, rows):
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
    if ndcg2 > ndcg1:
        better = 1
        sys.stderr.write("reporter:counter:My Counters,Better,1\n")
    else:
        sys.stderr.write("reporter:counter:My Counters,Worse,1\n")
    print "%s\t%f\t%f\t%d" % (qid, ndcg1, ndcg2, better)


def main():
    last_qid = None
    rows = []
    for line in sys.stdin:
        cols = line.strip().split('\t')
        qid, idx = cols[0].split(':')
        idx = int(idx)
        label = cols[1]
        gain = label2gain(label)
        score = float(cols[2])
        if not last_qid:
            last_qid = qid
        if last_qid != qid:
            deliver(last_qid, rows)
            last_qid = qid
            rows = []
        row = (qid, idx, gain, score)
        rows.append(row)


if __name__ == "__main__":
    main()
