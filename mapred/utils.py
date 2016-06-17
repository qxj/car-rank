#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; -*-
#
# Copyright (C) 2016 Julian Qian
#
# @file      utils.py
# @author    Julian Qian <junist@gmail.com>
# @created   2016-06-17 12:19:41
#

import sys
import datetime


class TableDesc(object):

    def __init__(self, desc_file):
        self.fields = self._read_desc(desc_file)

    def _read_desc(self, desc_file):
        fields = []
        with open(desc_file) as fp:
            for line in fp:
                cols = line.strip().split()
                if len(cols) != 2:
                    break
                fields.append(cols)
        return fields

    def fields(self, cols):
        rets = {}
        for i, item in enumerate(cols):
            field, ftype = self.fields[i]
            if item in ("\\N", "NULL"):
                item = None
            elif ftype == 'bigint' and 'time' in field:
                item = datetime.datetime.fromtimestamp(int(item) / 1000)
            elif ftype in ('int', 'tinyint', 'bigint'):
                item = int(item)
            elif ftype in ('float', 'double'):
                item = float(item)
            rets[field] = item
        return rets


def main():
    pass

if __name__ == "__main__":
    main()
