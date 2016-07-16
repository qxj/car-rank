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
import datetime
import argparse
import cPickle

from log import init_log
from interval_db import IntervalDb

logger = init_log('car_price.log')


class RankPrice(IntervalDb):

    def __init__(self, before_mins=0, throttling_num=0,
                 checkpoint_file=None, env_flag=None):
        super(RankPrice, self).__init__(before_mins, checkpoint_file,
                                        throttling_num, env_flag, "price")
        self.dayflag = '/tmp/rank_price.flag'

    def _set_dayflag(self, ds):
        with open(self.dayflag, 'w') as fp:
            cPickle.dump(ds, fp)

    def _get_dayflag(self):
        try:
            with open(self.dayflag) as fp:
                return cPickle.load(fp)
        except:
            logger.error("Failed to open dayflag file %s", self.dayflag)
        return None

    def sync_proportion(self, batch_num=100):
        last_ds = self._get_dayflag()
        ds = datetime.date.today() - datetime.timedelta(1)
        if ds == last_ds:
            logger.debug("date %s has been sync", ds)
            return
        # start to sync
        sql = '''select car_id,
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
        self._set_dayflag(ds)

    def sync_price(self, batch_num=100):
        ds = datetime.date.today()
        sql = '''select car_id, day1 price
        from car_dprice_{}
        '''.format(ds.strftime('%Y%m%d'))
        db_price = self._get_db('sphinx')
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
        set cf.suggest_price=cp.suggest_price,
        cf.price_daily=cp.price
        '''
        db = self._get_db('master')
        updated_cnt = db.exec_sql(sql)
        logger.info('update %s car feats', updated_cnt)


def main():
    parser = argparse.ArgumentParser(description='sync price tables')
    parser.add_argument('--env', type=str,
                        help='deploy on test environment')
    args = parser.parse_args()

    with RankPrice(env_flag=args.env) as obj:
        obj.sync_price()
        obj.sync_proportion()
        obj.update_price_all()

if __name__ == "__main__":
    main()
