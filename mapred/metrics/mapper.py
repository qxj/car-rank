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
import os

import zipimport
imp = zipimport.zipimporter('utils.mod')
utils = imp.load_module('utils')
from utils import table


def main():
    td = table.TableMeta('query_log.desc')
    max_page = int(os.getenv('max_page', 20))

    for line in sys.stdin:
        cols = line.strip().split('\t')
        row = td.fields(cols)
        qid = row['qid']
        label = row['label']
        city_code = row['city_code']
        page = row['page']      # [1,\inf)
        idx = row['idx']
        algo = row['algo']
        visit_time = row['visit_time']
        if page > max_page:
            sys.stderr.write(
                "reporter:counter:My Counters,Skip >%dPages,1\n" % max_page)
            continue
        # only clicked items are required
        if label == 'impress':
            sys.stderr.write("reporter:counter:My Counters,CV-Impress,1\n")
            continue
        elif label == 'click':
            sys.stderr.write("reporter:counter:My Counters,CV-Click,1\n")
        elif label == 'precheck':
            sys.stderr.write("reporter:counter:My Counters,CV-Precheck,1\n")
        elif label == 'order':
            sys.stderr.write("reporter:counter:My Counters,CV-Order,1\n")
        else:
            sys.stderr.write("reporter:counter:My Counters,CV-Unknown,1\n")
            continue
        print "%s:%.10d\t%s\t%s\t%s\t%s" % (
            qid, idx, label, city_code, algo, visit_time)

if __name__ == "__main__":
    main()
