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

def main():
    for line in sys.stdin:
        cols = line.strip().split()
        qid = cols[0]
        label = cols[1]
        city_code = cols[2]
        pos = int(cols[7])   # [0,14]
        page = int(cols[8])  # [1,\inf)
        algo = cols[9]
        visit_time = cols[10]
        # idx starts from zero
        idx = (page -1) * 15 + pos
        # only clicked items are required
        if label != "impress":
            # gain = 2^label -1
            gain = 3
            if label == "order":
                gain = 15
            elif label == "precheck":
                gain = 7
            print "%s:%.10d\t%d\t%s\t%s\t%s" % (qid, idx, gain, city_code, algo, visit_time)

if __name__ == "__main__":
    main()
