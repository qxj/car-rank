#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; -*-
#
# Copyright (C) 2016 Julian Qian
#
# @file      mapper.py
# @author    Julian Qian <junist@gmail.com>
# @created   2016-07-03 17:41:24
#

import sys

import zipimport
imp = zipimport.zipimporter('utils.mod')
utils = imp.load_module('utils')
from utils import table


def label2gain(label):
    gain = 0
    if label == 'click':
        gain = 2
    elif label == 'precheck':
        gain = 7
    elif label == 'order':
        gain = 15
    return gain


def main():
    td = table.TableMeta('corpus_rl.desc')
    feats = {}
    i = 1
    for line in open('feats.txt'):
        feats[line.strip()] = i
        i+=1
    for line in sys.stdin:
        cols = line.strip().split('\t')
        row = td.fields(cols)
        qid = row['qid']
        idx = row['idx']
        output = []
        output.append(label2gain(row['label']))
        output.append("qid:" + row['qid'])
        for f, i in feats.items():
            output.append('%d:%s' % (i, row[f]))
        payload = ' '.join(output)
        print '%s:%d\t%s' % (qid, idx, payload)

if __name__ == "__main__":
    main()
