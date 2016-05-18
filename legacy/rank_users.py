#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; -*-
#
# Copyright (C) 2016 Julian Qian
#
# @file      rank_users.py
# @author    Julian Qian <junist@gmail.com>
# @created   2016-05-12 17:52:20
#


from __future__ import division
import datetime
import collections
import argparse
import sys
sys.path.append('./pdlib/py')
from log import init_log

from interval_db import IntervalDb

logger = init_log('car_users.log')


class CarUsers(IntervalDb):

    def __init__(self):
        super(CarUsers, self).__init__()

    def _update(self, user_id, value_dict):
        # TODO anti snow
        self.throttling.check()
        return self.db.update('car_rank_users', {'user_id': user_id}, value_dict)

    def update_collect(self):
        max_collect_size = 200
        db = self._get_db("slave")
        sql = """select uid user_id, car_id, status
        from car_collect
        where utime>'{}'
        """.format(self.update_time)
        rows = db.exec_sql(sql)
        users = collections.defaultdict(list)
        for row in rows:
            car_id = row['car_id']
            user_id = row['user_id']
            if row['status'] == 0:
                car_id = - car_id
            if len(users[user_id]) < max_collect_size:
                users[user_id].append(car_id)
        logger.info('[collect] fetch %d rows, and %d users',
                    len(rows), len(users))

        cntr = collections.Counter()
        for user_id, updates in users.iteritems():
            sql = """select collected_cars
            from car_rank_users where user_id={}
            """.format(user_id)
            rows = db.exec_sql(sql)
            if len(rows) > 0:
                row = rows[0]
                cars = set([int(i) for i in row['collected_cars'].split(',')])
                for i in updates:
                    if i > 0:
                        cars.add(i)
                    else:
                        cars.discard(-i)
                new_cars = ','.join([str(i) for i in cars])
                self._update(user_id, new_cars)
                cntr['update'] += 1
            else:
                sql = """select car_id
                from car_collect where uid={} and status=1
                order by id limit {}
                """.format(user_id, max_collect_size)
                rows = db.exec_sql(sql)
                cars = ','.join([str(i) for i in rows['car_id']])
                self._update(user_id, cars)
                cntr['add'] += 1
        logger.info('[collect] update %d, add %d', cntr['update'], cntr['add'])

    def update_orders(self):
        max_order_size = 50
        db = self._get_db("slave")
        sql = """select uid user_id, carid car_id
        from orders
        where ctime>'{}'
        """.format(self.update_time)
        rows = db.exec_sql(sql)
        users = collections.defaultdict(list)
        for row in rows:
            car_id = row['car_id']
            user_id = row['user_id']
            if len(users[user_id]) < max_order_size:
                users[user_id].append(car_id)
        logger.info('[orders] fetch %d rows, and %d users',
                    len(rows), len(users))

        cntr = collections.Counter()
        for user_id, updates in users.iteritems():
            sql = """select ordered_cars
            from car_rank_users where user_id={}
            """.format(user_id)
            rows = db.exec_sql(sql)
            if len(rows) > 0:
                row = rows[0]
                cars = set([int(i) for i in row['ordered_cars'].split(',')])
                for i in updates:
                    cars.add(i)
                new_cars = ','.join([str(i) for i in cars])
                self._update(user_id, new_cars)
                cntr['update'] += 1
            else:
                sql = """select carid car_id
                from orders where uid={}
                order by id limit {}
                """.format(user_id, max_order_size)
                rows = db.exec_sql(sql)
                cars = ','.join([str(i) for i in rows['car_id']])
                self._update(user_id, cars)
                cntr['add'] += 1
        logger.info('[orders] update %d, add %d', cntr['update'], cntr['add'])

    def update(self):
        self.update_collect()
        self.update_orders()


def main():
    parser = argparse.ArgumentParser(description='users preference')
    # parser.add_argument('action', type=str, choices=('run', 'prepare',
    #                                                  'test'), help='actions')
    parser.add_argument('--throttling', type=int, default=200,
                        help='throttling update num per second')
    parser.add_argument('--checkpoint', type=str,
                        help='checkpoint file to save latest update timestamp')
    parser.add_argument('--before', type=int,
                        help='before minutes to update, OVERRIDE checkpoint')
    parser.add_argument('--cars', type=str,
                        help='test car ids, splited by comma')
    parser.add_argument('--test', action='store_true',
                        help='deploy on test environment')
    parser.add_argument('--verbose', action='store_true', help='verbose log')
    args = parser.parse_args()

    before_minutes = args.before

    logger.info('[start] car_users args: %s', args)
    with CarUsers(before_mins=before_minutes,
                  throttling_num=args.throttling,
                  checkpoint_file=args.checkpoint,
                  is_test=args.test) as cu:
        cu.update()

    logger.info('================')


if __name__ == "__main__":
    main()
