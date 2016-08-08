#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; -*-
#
# Copyright (C) 2016 Julian Qian
#
# @file      reducer.py
# @author    Julian Qian <junist@gmail.com>
# @created   2016-03-31 07:46:37
#

from __future__ import division
import sys
import cmath
import os

g_max_page = int(os.getenv('max_page', 20))
g_max_ctr = float(os.getenv('max_ctr', 0.5))


def label2gain(label):
    # gain = 2^label -1
    gain = 2
    if label == 'precheck':
        gain = 7
    elif label == 'order':
        gain = 15
    return gain


def gain2label(gain):
    label = 'click'
    if gain == 7:
        label = 'precheck'
    elif gain == 15:
        label = 'order'
    return label


def process(rows, query):
    global g_max_ctr
    patks = 0.0
    d1 = 0.0
    d2 = 0.0
    # TODO skip, if too many clicks
    # FIXME the last doc is always clicked
    # ctr = len(rows) / (rows[-1][0] + 1)
    # if ctr > g_max_ctr:
    #     sys.stderr.write(
    #         "reporter:counter:My Counters,Skip CTR>%f,1\n" % g_max_ctr)
    #     return
    if len(rows) == 0:
        sys.stderr.write(
            "reporter:counter:My Counters,Empty rows,1\n")
        return
    row_max_gain = max(rows, key=lambda x: x[-1])
    query_label = gain2label(row_max_gain[-1])
    impress_cnt = rows[-1][0] + 1
    click_cnt = 0
    precheck_cnt = 0
    order_cnt = 0
    for i, (idx, label, gain) in enumerate(rows):
        # P@k
        patk = (i + 1) / (idx + 1)
        patks += patk
        # dcg(i) = gain_i / discount_i
        d1 += gain / cmath.log(idx + 2, 2).real
        # count
        if label in ("click", "precheck", "order"):
            click_cnt += 1
        elif label in ("precheck", "order"):
            precheck_cnt += 1
        elif label == "order":
            order_cnt += 1
    for i, (_, _, gain) in enumerate(sorted(
            rows, key=lambda x: x[-1], reverse=True)):
        # idcg(i)
        d2 += gain / cmath.log(i + 2, 2).real
    # AP = {\sum_k P@k \over relative docs }
    ap = patks / len(rows)
    ap_str = "%.5f" % ap
    # dcg = \sum_{i=1}^N dcg(i)
    ndcg = d1 / d2
    ndcg_str = "%.5f" % ndcg
    # ctr
    ctr = click_cnt / impress_cnt
    cvr = order_cnt / impress_cnt
    cvr1 = precheck_cnt / click_cnt
    cvr2 = order_cnt / click_cnt
    # OUTPUT: qid, label, ap, ndcg, city_code, algo, visit_time
    query.insert(1, query_label)
    query.insert(2, ap_str)
    query.insert(3, ndcg_str)
    # cvr
    extra = [impress_cnt, click_cnt, precheck_cnt,
             order_cnt, ctr, cvr, cvr1, cvr2]
    query += ["%s" % i for i in extra]
    print "\t".join(query)
    sys.stderr.write("reporter:counter:My Counters,Metrics Counter,1\n")


def main():
    last_query = None           # (qid, city_code, algo, visit_time)
    rows = []
    for line in sys.stdin:
        cols = line.strip('\n').split('\t')
        qid, idx_str = cols[0].split(':')
        idx = int(idx_str)
        label = cols[1]
        gain = label2gain(label)
        query = [qid] + cols[2:]  # qid, city_code, algo, visit_time
        if not last_query:
            last_query = query
        if qid != last_query[0]:
            process(rows, last_query)
            rows = []
            last_query = query
        rows.append((idx, label, gain))
    process(rows, last_query)

if __name__ == "__main__":
    main()
