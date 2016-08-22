#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; -*-
#
# Copyright (C) 2016 Julian Qian
#
# @file      report.py
# @author    Julian Qian <junist@gmail.com>
# @created   2016-08-16 15:22:48
#

import argparse
import sys
from impala.dbapi import connect

import mymail
import htmlUtil


class Report(object):

    def __init__(self):
        pass

    def get(self, start, end):
        conn = connect(host="stats-hadoop21")
        cur = conn.cursor()
        cur.execute("refresh rank.metrics")
        sql = """select ds, dayname(to_timestamp(ds,"yyyyMMdd")) dn,
        algo,avg(ndcg) ndcg,count(1) cnt,
        sum(n_impress) imp, sum(n_click) clk, sum(n_precheck) pck, sum(n_order) odr,
        sum(n_click)/sum(n_impress) ctr, sum(n_order)/sum(n_impress) cvr
        from rank.metrics
        where ds between '{}' and '{}' and algo!='None'
        group by ds,algo
        order by ds,algo
        """.format(start, end)
        print sql
        cur.execute(sql)
        head = ("Date",
                "DayofWeek",
                "Strategy",
                "NDCG",
                "Queries",
                "Impress",
                "Click",
                "Precheck",
                "Order",
                "CTR",
                "CVR")
        data = []
        data.append(head)
        for row in cur:
            data.append(row)
        return htmlUtil.matrix2HtmlTable(data,
                                         u'Rank Metrics %s~%s' % (start, end))


def main():
    parser = argparse.ArgumentParser(description='some task')
    parser.add_argument('--start', type=str, help='start date')
    parser.add_argument('--end', type=str, help='end date')
    parser.add_argument('--to', type=str, help='mail to')
    parser.add_argument('--dry', action='store_true', help='whether dry run')
    parser.add_argument('--verbose', action='store_true',
                        help='print verbose log')
    args = parser.parse_args()

    content = Report().get(args.start, args.end)

    mymail.sendMail(args.to, 'Rank Metrics %s~%s' %
                    (args.start, args.end), content)


if __name__ == "__main__":
    main()
