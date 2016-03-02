#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; -*-
# @(#) car_score_util.py  Time-stamp: <Julian Qian 2016-02-02 14:13:14>
# Copyright 2016 Julian Qian
# Author: Julian Qian <junist@gmail.com>
# Version: $Id: car_score_util.py,v 0.1 2016-02-02 11:11:27 jqian Exp $
#

import sys
import argparse

sys.path.append('./pdlib/py')
import mydb


class CarScoreUtil(object):

    def __init__(self):
        self.db = mydb.get_db("master")

    def get_score(self, car_id):
        sql = """select score, w_manual from
        car_rank_score where car_id={}
        """.format(car_id)
        rows = self.db.exec_sql(sql, resultFormat='tuple')
        if rows:
            return rows[0]
        return None

    def set_score(self, car_id, manual_weight):
        self.db.update('car_rank_feats',
                       {'car_id': car_id},
                       {'manual_weight': manual_weight})

    def close(self):
        self.db.commit()
        self.db.close()


def main():
    parser = argparse.ArgumentParser(description='utils to tweak car_score')
    parser.add_argument('action', type=str, choices=('get', 'set',
                                                     'test'), help='actions')
    parser.add_argument('--weight', type=int, help='add weight')
    args = parser.parse_args()

    util = CarScoreUtil()
    cnt = 0
    for line in sys.stdin:
        cols = line.strip().split()
        car_id = int(cols[0])
        cnt += 1
        if args.action == "get":
            row = util.get_score(car_id)
            if row:
                print "{}\t{}\t{}".format(car_id, row[0], row[1])
            else:
                print >> sys.stderr, "missing car_id ", car_id
        elif args.action == "set":
            weight = int(args.weight)
            if len(cols) > 1:
                weight = int(cols[1])
            util.set_score(car_id, weight)
    util.close()
    print >> sys.stderr, "processed %d cars" % cnt

if __name__ == "__main__":
    main()
