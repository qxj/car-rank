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
import os

g_strict = True if os.getenv('strict_mode') == "1" else False
g_max_page = int(os.getenv('max_page', 20))
g_max_ctr = float(os.getenv('max_ctr', 0.5))


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
            sys.stderr.write("reporter:counter:My Counters,Output-Rows,1\n")
        else:
            sys.stderr.write(
                "reporter:counter:My Counters,Discard-Head-Clicks,1\n")


def deliver_rows_all(rows):
    for cols in rows:
        print "\t".join(cols)
        sys.stderr.write("reporter:counter:My Counters,Output-Rows,1\n")


def filter(clicked_len, clicked_cnt, rows):
    global g_strict, g_max_ctr, g_max_page
    if clicked_len > 0:
        if g_strict:
            # only deliver items before last clicked one
            rows = rows[:clicked_len]
        ctr = clicked_cnt / len(rows)
        if ctr > g_max_ctr:
            sys.stderr.write(
                "reporter:counter:My Counters,Skip Ctr>%f,1\n" % g_max_ctr)
            return
        if g_strict:
            deliver_rows(rows)
        else:
            deliver_rows_all(rows)
            idx = rows[-1][1]
            idx = int(idx)
            if idx < g_max_page:
                sys.stderr.write(
                    "reporter:counter:My Counters,Trail<%d Pages Requests,1\n"
                    % g_max_page)
            if len(rows) < g_max_page * 15:
                sys.stderr.write(
                    "reporter:counter:My Counters,<%d Pages Requests,1\n"
                    % g_max_page)
        sys.stderr.write("reporter:counter:My Counters,Output Counter,1\n")
    else:
        sys.stderr.write(
            "reporter:counter:My Counters,No Clicked Requests,1\n")


def main():
    last_qid = None
    clicked_len = 0
    clicked_cnt = 0
    rows = []
    for line in sys.stdin:
        cols = line.strip().split('\t')
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
