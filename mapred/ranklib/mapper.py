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
    feats = []
    i = 1
    for line in open('feats.txt'):
        feat = line.strip()
        if feat.startswith("#") or len(feat) == 0:
            continue
        feats.append((feat, i))
        i += 1
    for line in sys.stdin:
        cols = line.strip().split('\t')
        row = td.fields(cols)
        qid = row['qid']
        idx = row['idx']
        output = []
        output.append(label2gain(row['label']))
        output.append("qid:" + row['qid'])
        for feat, i in feats:
            if feat in row:
                output.append('%d:%s' % (i, row[feat]))
            else:
                sys.stderr.write(
                    "reporter:counter:My Counters,Feature Missing,1\n")
        output.append("# idx:%d" % idx)
        payload = ' '.join([str(i) for i in output])
        print '%s:%.10d\t%s' % (qid, idx, payload)

if __name__ == "__main__":
    main()
