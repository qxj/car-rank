#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; -*-
#
# Copyright (C) 2016 Julian Qian
#
# @file      reducer.py
# @author    Julian Qian <junist@gmail.com>
# @created   2016-03-30 08:30:29
#

# OUTPUT:
# pii (impress 0, click 1, precheck 2, order 3)
# index
# qid
# label
# city_code
# user_id
# car_id
# distance

import sys

def deliver_rows(rows):
    has_neg = False
    for cols in rows:
        # cols: qid, idx, label, city_code, user_id, car_id, distance
        qid = cols[0]  # for validation
        idx = cols[1]
        label = cols[2]
        pii = -1
        if not has_neg and label == "impress":
            has_neg = True
        if has_neg:
            if label == "click":
                pii = 3
            elif label == "precheck":
                pii = 2
            elif label == "click":
                pii = 1
            elif label == "impress":
                pii = 0
        if pii != -1:
            line = "%d\t%d\t" % (pii, idx)
            print line + "\t".join(cols[2:]) + "\t" + qid
        else:
            sys.stderr.write("reporter:counter:My Counters,Discard-Head-Clicks,1\n")


def main():
    last_qid = None
    clicked_len = 0
    rows = []
    for line in sys.stdin:
        cols = line.strip().split()
        qid, idx_str = cols[0].split(':')
        label = cols[1]
        idx = int(idx_str)
        if not last_qid:
            last_qid = qid
        if qid != last_qid:  # new qid
            if clicked_len > 0:
                deliver_rows(rows[:clicked_len])
            rows = []
            clicked_len = 0
            last_qid = qid
        row = [qid, idx] + cols[1:]
        rows.append(row)
        if label != "impress":
            clicked_len = len(rows) 
    # trailing rows
    if clicked_len > 0:
        deliver_rows(rows[:clicked_len])

if __name__ == "__main__":
    main()
