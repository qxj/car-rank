#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; -*-
#
# Copyright (C) 2016 Julian Qian
#
# @file      mapper.py
# @author    Julian Qian <junist@gmail.com>
# @created   2016-06-13 16:18:23
#

import sys
from rank_legacy import RankLegacy


def main():
    for line in sys.stdin:
        cols = line.strip().split()
        qid = cols[0]
        idx = cols[1]
        label = cols[2]
        rets = RankLegacy.calc_score(cols)
        score = float(rets['quality'] * 100)
        print '%s:%.10d\t%s\t%f' % (qid, idx, label, score)

if __name__ == "__main__":
    main()
