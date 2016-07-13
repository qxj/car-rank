#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; -*-
#
# Copyright (C) 2016 Julian Qian
#
# @file      reducer.py
# @author    Julian Qian <junist@gmail.com>
# @created   2016-07-04 15:31:06
#

import sys


def main():
    for line in sys.stdin:
        cols = line.strip().split('\t')
        if len(cols) == 2:
            print cols[1]
        else:
            sys.stderr.write(
                "reporter:counter:My Counters,Unknown Error,1\n")

if __name__ == "__main__":
    main()
