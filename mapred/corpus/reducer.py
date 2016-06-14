#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; -*-
#
# Copyright (C) 2016 Julian Qian
#
# @file      reducer.py
# @author    Julian Qian <junist@gmail.com>
# @created   2016-03-30 08:30:29
#

from __future__ import division
import sys


def deliver_rows(rows):
    has_neg = False
    for cols in rows:
        # visit_time
        label = cols[2]
        pii = False
        if not has_neg and label == "impress":
            has_neg = True
        if has_neg or label in ("order", "precheck"):
            pii = True
        if pii:
            print "\t".join(cols)
        else:
            sys.stderr.write(
                "reporter:counter:My Counters,Discard-Head-Clicks,1\n")


def filter(clicked_len, clicked_cnt, rows):
    if clicked_len > 0:
        # only deliver items before last clicked one
        items = rows[:clicked_len]
        ctr = clicked_cnt / len(items)
        if ctr > 0.4:
            sys.stderr.write(
                "reporter:counter:My Counters,High Ctr Requests,1\n")
        else:
            deliver_rows(items)
    else:
        sys.stderr.write(
            "reporter:counter:My Counters,No Clicked Requests,1\n")


def main():
    last_qid = None
    clicked_len = 0
    clicked_cnt = 0
    rows = []
    for line in sys.stdin:
        cols = line.strip().split()
        qid, idx_str = cols[0].split(':')
        label = cols[1]
        idx = int(idx_str)
        if not last_qid:
            last_qid = qid
        if qid != last_qid:  # new qid
            filter(clicked_len, clicked_cnt, rows)
            rows = []
            clicked_len = 0
            clicked_cnt = 0
            last_qid = qid
        row = [qid, str(idx)] + cols[1:]
        rows.append(row)
        # only deliver requests which have been clicked
        if label != "impress":
            clicked_len = len(rows)
            clicked_cnt += 1
    # trailing request
    filter(clicked_len, clicked_cnt, rows)

if __name__ == "__main__":
    main()
