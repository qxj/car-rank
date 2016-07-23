#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; -*-
#
# Copyright (C) 2016 Julian Qian
#
# @file      interval_db.py
# @author    Julian Qian <junist@gmail.com>
# @created   2016-05-17 11:28:26
#

"""run mysql query in crontab every interval minutes
"""

import cPickle
import datetime
import logging
import time
import sys
sys.path.append('./pdlib/py')
import mydb


class Throttling(object):

    def __init__(self, limit_per_sec):
        self.limit_per_sec = limit_per_sec
        self.curr_ts = 0
        self.cnt_this_sec = 0
        self.yield_sec = 0.005  # sleep 5 ms

    def check(self):
        if self.limit_per_sec <= 0:
            return
        ts = int(time.time())
        while ts == self.curr_ts and self.cnt_this_sec >= self.limit_per_sec:
            time.sleep(self.yield_sec)
            ts = int(time.time())
        if ts == self.curr_ts:
            self.cnt_this_sec += 1
        else:
            self.curr_ts = ts
            self.cnt_this_sec = 0


class IntervalDb(object):

    def __init__(self, before_mins=0, checkpoint_file=None,
                 throttling_num=0, env_flag=None, db_flag="master"):
        """before_mins(>0) will override checkpoint_file
        """
        # checkpoint properties
        self._current_time = datetime.datetime.now()
        self._checkpoint_file = checkpoint_file

        self.env_flag = env_flag
        self.db = self._get_db(db_flag)
        # yesterday this time
        self.update_time = self._update_time(before_mins)
        self.throttling = Throttling(throttling_num)
        logging.info('[init] update time: %s', self.update_time)

    def _get_db(self, flag):
        db_names = {'master': 'master',
                    'score': 'master',
                    'price': 'price',
                    'slave': 'slave',
                    'sphinx': 'sphinx'}
        if self.env_flag == "test28":
            db_names = {'master': 'test28',
                        'score': 'test28',
                        'price': 'test28_price',
                        'slave': 'test28',
                        'sphinx': 'test28_sphinx'}
        elif self.env_flag == "test38":
            db_names = {'master': 'test38',
                        'score': 'test38',
                        'price': 'test38_price',
                        'slave': 'test38',
                        'sphinx': 'test38_sphinx'}
        return mydb.get_db(db_names[flag])

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.db.commit()
        # sync checkpoint if everything ok
        self._set_checkpoint()
        logging.info('exit car score instance, and set checkpoint.')

    def _set_checkpoint(self):
        if self._checkpoint_file:
            try:
                with open(self._checkpoint_file, 'w') as fp:
                    cPickle.dump(self._current_time, fp)
            except:
                logging.warn('failed to dump checkpoint file: %s',
                             self._checkpoint_file)

    def _update_time(self, before_minutes):
        ts = None
        if before_minutes > 0:
            ts = datetime.datetime.today() - \
                datetime.timedelta(minutes=before_minutes)
        else:
            try:
                with open(self._checkpoint_file) as fp:
                    ts = cPickle.load(fp)
            except:
                logging.warn('no checkpoint file is found: %s',
                             self._checkpoint_file)
            if not isinstance(ts, datetime.datetime):
                ts = datetime.datetime.today() - datetime.timedelta(minutes=10)
                logging.warn('no timestamp is specified, set to %s', ts)
        return ts


def DummyTask(IntervalDb):
    def __init__(self):
        super(DummyTask, self).__init__()

    def task(self):
        db = self._get_db("slave")
        sql = "show tables"
        rows = db.exec_sql(sql)
        for row in rows:
            print row


def main():
    d = DummyTask()
    d.task()

if __name__ == "__main__":
    main()
