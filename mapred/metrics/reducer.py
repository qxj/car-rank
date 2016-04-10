#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; -*-
#
# Copyright (C) 2016 Julian Qian
#
# @file      reducer.py
# @author    Julian Qian <junist@gmail.com>
# @created   2016-03-31 07:46:37
#

import sys
import cmath

def process(rows, query):
    patks = 0.0
    d1 = 0.0
    d2 = 0.0
    for i, idx in enumerate(rows):
        # P@k
        patk = (i +1) / (idx +1)
        patks += patk
        # dcg(i)
        d1 += 1.0/cmath.log(idx+2, 2).real
        d2 += 1.0/cmath.log(i+2, 2).real
    # AP = {\sum_k P@k \over relative docs }
    ap = patks / len(rows)
    ap_str = "%.5f" % ap
    # dcg = \sum_{i=1}^N{2^{label(i)}-1 \over \log_2{(i+1)}}
    ndcg = d1/d2
    ndcg_str = "%.5f" % ndcg
    # OUTPUT: qid, ap, ndcg, city_code, algo, visit_time
    query.insert(1, ap_str)
    query.insert(2, ndcg_str)
    print "\t".join(query)
    sys.stderr.write("reporter:counter:My Counters,Metrics Counter,1\n")


def main():
    last_query = None           # (qid, city_code, algo, visit_time)
    rows = []
    for line in sys.stdin:
        cols = line.strip('\n').split()
        qid, idx = cols[0].split(':')
        cols[0] = qid
        if not last_query:
            last_query = cols
        if qid != last_query[0]:
            process(rows, last_query)
            rows = []
            last_query = cols
        rows.append(float(idx))
    process(rows, last_query)

if __name__ == "__main__":
    main()
