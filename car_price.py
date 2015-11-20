#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; -*-
# @(#) car_price.py  Time-stamp: <Julian Qian 2015-11-20 14:09:14>
# Copyright 2015 Julian Qian
# Author: Julian Qian <junist@gmail.com>
# Version: $Id: car_price.py,v 0.1 2015-11-19 13:13:25 jqian Exp $
#


'''sync car price from price.stats_daily_price_snapshot
run in midnight at crontab
'''

from __future__ import division
import sys
import datetime

sys.path.append('./pdlib/py')
import mydb
from log import init_log

logger = init_log('car_price.log')


class CarPrice(object):
    def sync(self, batch_num=100):
        ds = datetime.date.today() - datetime.timedelta(1)
        sql = '''select car_id,
        price,
        suggest_price,
        base_price,
        owner_proportion proportion
        from stats_daily_price_snapshot
        where date='{}'
        '''.format('%s' % ds)
        db_price = mydb.get_db('price')
        rows = db_price.exec_sql(sql)
        db = mydb.get_db('master')
        batch = []
        updated_cnt = 0
        for row in rows:
            batch.append(row)
            if len(batch) == batch_num:
                updated_cnt += db.insert_many('car_rank_price', batch,
                                              on_duplicate_ignore=False)
                del batch[:]
        if len(batch):
            updated_cnt += db.insert_many('car_rank_price', batch,
                                          on_duplicate_ignore=False)
        logger.info('update %d car price', updated_cnt)

    def update_price(self):
        ds = datetime.datetime.now() - datetime.timedelta(0.5)
        sql = '''select car_id,
        suggest_price
        from car_rank_price
        where update_time> '{}'
        '''.format(ds)
        db = mydb.get_db('master')
        rows = db.exec_sql(sql)
        updated_cnt = 0
        for row in rows:
            updated_cnt += db.update('car_rank_feats',
                                     {'car_id': row['car_id']}, row)
        logger.info('update %d car feats', updated_cnt)


def main():
    cp = CarPrice()
    cp.sync()
    cp.update_price()

if __name__ == "__main__":
    main()
