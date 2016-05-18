#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; -*-
#
# Copyright (C) 2016 Julian Qian
#
# @file      rank_price.py
# @author    Julian Qian <junist@gmail.com>
# @created   2016-05-18 11:31:07
#

'''sync car price from price.stats_daily_price_snapshot
run in midnight at crontab
'''

from __future__ import division
import sys
import datetime
import argparse

sys.path.append('./pdlib/py')
import mydb
from log import init_log

logger = init_log('car_price.log')


class RankPrice(object):

    def __init__(self, is_test):
        self.is_test = is_test

    def _get_db(self, flag, is_test=False):
        db_names = {'master': 'master',
                    'price': 'price',
                    'slave': 'slave'}
        if self.is_test:
            db_names = {'master': 'test28',
                        'price': 'test28',
                        'slave': 'test28'}
        return mydb.get_db(db_names[flag])

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
        db_price = self._get_db('price')
        rows = db_price.exec_sql(sql)
        db = self._get_db('master')
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

    def update_price_all(self):
        sql = '''update car_rank_feats cf
        join car_rank_price cp on cf.car_id=cp.car_id
        set cf.suggest_price=cp.suggest_price
        '''
        db = self._get_db('master')
        updated_cnt = db.exec_sql(sql)
        logger.info('update %d car feats', updated_cnt)

    def update_price(self):
        ds = datetime.datetime.now() - datetime.timedelta(0.5)
        sql = '''select car_id,
        suggest_price
        from car_rank_price
        where update_time> '{}'
        '''.format(ds)
        db = self._get_db('master')
        rows = db.exec_sql(sql)
        updated_cnt = 0
        for row in rows:
            updated_cnt += db.update('car_rank_feats',
                                     {'car_id': row['car_id']}, row)
        logger.info('update %d car feats', updated_cnt)


def main():
    parser = argparse.ArgumentParser(description='sync price tables')
    parser.add_argument('--test', action='store_true',
                        help='deploy on test environment')
    args = parser.parse_args()

    cp = RankPrice(args.test)
    cp.sync()
    cp.update_price_all()

if __name__ == "__main__":
    main()
