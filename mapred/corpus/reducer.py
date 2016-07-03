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
import json

import zipimport
imp = zipimport.zipimporter('utils.mod')
utils = imp.load_module('utils')
from utils import table

g_max_page = int(os.getenv('max_page', 20))
g_max_ctr = float(os.getenv('max_ctr', 0.5))
g_td = table.TableMeta('corpus.desc')


def print1(row):
    global g_td
    print '\t'.join(g_td.convert(row, process_fn=lambda _, x: str(x)))


def filter(clicked_cnt, rows):
    global g_strict, g_max_ctr, g_max_page
    if clicked_cnt == 0:
        sys.stderr.write(
            "reporter:counter:My Counters,No Clicked Queries,1\n")
        return
    # TODO only deliver items before last clicked one
    # rows = rows[:clicked_len]
    ctr = clicked_cnt / len(rows)
    if ctr > g_max_ctr:
        sys.stderr.write(
            "reporter:counter:My Counters,Skip Ctr>%f,1\n" % g_max_ctr)
        return
    for i, row in enumerate(rows):
        idx = row['idx']
        if i != idx:
            sys.stderr.write(
                "reporter:counter:My Counters,Missing Indices,1\n")
            return
    for row in rows:
        print1(row)
        sys.stderr.write("reporter:counter:My Counters,Output Corpus,1\n")
    sys.stderr.write("reporter:counter:My Counters,Output Queries,1\n")


def main():
    last_qid = None
    clicked_cnt = 0
    rows = []
    for line in sys.stdin:
        cols = line.strip().split('\t')
        qid, _ = cols[0].split(':')
        row = json.loads(cols[1])
        label = row['label']
        if last_qid is None:
            last_qid = qid
        if qid != last_qid:  # new qid
            filter(clicked_cnt, rows)
            rows = []
            clicked_cnt = 0
            last_qid = qid
        rows.append(row)
        # only deliver requests which have been clicked
        if label != "impress":
            clicked_cnt += 1
    # trailing request
    filter(clicked_cnt, rows)

if __name__ == "__main__":
    main()
