#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; -*-
#
# Copyright (C) 2016 Julian Qian
#
# @file      reducer.py
# @author    Julian Qian <junist@gmail.com>
# @created   2016-07-03 17:43:25
#

import sys

def main():
    for line in sys.stdin:
        cols = line.strip().split('\t')
        print cols[1]

if __name__ == "__main__":
    main()
