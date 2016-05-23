#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; -*-
#
# Copyright (C) 2016 Julian Qian
#
# @file      rank_score.py
# @author    Julian Qian <junist@gmail.com>
# @created   2016-05-18 11:17:59
#

from __future__ import division
import argparse
import datetime
from log import init_log
from interval_db import IntervalDb

logger = init_log(logtofile='rank_score.log')


class RankScore(IntervalDb):

    def __init__(self, before_mins=0, throttling_num=0,
                 checkpoint_file=None, cars=[], env_flag=None):
        super(RankScore, self).__init__(before_mins, checkpoint_file,
                                        throttling_num, env_flag)
        self.cars = cars

    def _and_cars(self, field):
        return ' and {} in ({})'.format(field, ','.join(self.cars)) if self.cars else ''

    def _write_score(self, value_dict, table_name='car_rank_score'):
        self.throttling.check()
        return self.db.insert(table_name, value_dict,
                              on_duplicate_ignore=False)

    def _write_scores(self, value_dict_list, table_name='car_rank_score'):
        updated_cnt = 0
        dlen = len(value_dict_list)
        idx = 0
        batch_num = 100
        while idx < dlen:
            if idx % batch_num == 0:
                updated_cnt += self.db.insert_many(
                    table_name, value_dict_list[idx:idx + batch_num],
                    on_duplicate_ignore=False)
            idx += 1
        self.db.commit()
        return updated_cnt

    def _calc_score(self, row):
        scores = {}
        # price
        scores['w_price'] = 0
        suggest_price = row['suggest_price']
        proportion = row['proportion']

        if suggest_price <= 200:
            low = (30, -20)
            lot = (0.8, 1.1, 1.3, 1.6)
            if proportion < lot[0]:
                scores['w_price'] = low[0]
            elif lot[0] <= proportion <= lot[1]:
                scores['w_price'] = low[0] * \
                    (lot[1] - proportion) / (lot[1] - lot[0])
            elif lot[1] < proportion < lot[2]:
                scores['w_price'] = 0
            elif lot[2] <= proportion <= lot[3]:
                scores['w_price'] = low[1] * \
                    (proportion - lot[2]) / (lot[3] - lot[2])
            else:
                scores['w_price'] = low[1]
        else:
            hiw = (30, -30)
            hit = (0.7, 1.15, 1.25, 1.6)
            if proportion < hit[0]:
                scores['w_price'] = hiw[0]
            elif hit[0] <= proportion <= hit[1]:
                scores['w_price'] = hiw[0] * \
                    (hit[1] - proportion) / (hit[1] - hit[0])
            elif hit[1] < proportion < hit[2]:
                scores['w_price'] = 0
            elif hit[2] <= proportion <= hit[3]:
                scores['w_price'] = hiw[1] * \
                    (proportion - hit[2]) / (hit[3] - hit[2])
            else:
                scores['w_price'] = hiw[1]
            scores['w_price'] += -5
        # price tuning
        tuning = 0.1 * row['price_tuning']
        scores['w_price'] += tuning
        # accept
        if row['auto_accept']:
            scores['w_accept'] = 15
        else:
            scores['w_accept'] = row['recent_accepted'] * 1.5
            scores['w_accept'] -= row['recent_rejected'] * 1.5
        # review
        scores['w_review_owner'] = 0
        scores['w_review_car'] = 0
        review_owner = row['review_owner']
        if review_owner > 0:
            scores['w_review_owner'] = 8 * (review_owner - 3) / 2
        review_car = row['review_car']
        if review_car > 0:
            scores['w_review_car'] = 7 * (review_car - 3) / 2
        # recommend
        recommend_level = row['recommend_level']
        scores['w_recommend'] = 0
        if recommend_level > 10:
            scores['w_recommend'] = 15
        elif recommend_level > 0:
            scores['w_recommend'] = 7.5
        elif recommend_level < 0:
            scores['w_recommend'] = -20
        # manual
        scores['w_manual'] = row['manual_weight']
        # punish
        punish = 0
        days = 0
        if row['verified_time']:
            ddays = datetime.datetime.today() - row['verified_time']
            days = ddays.days
        if days > 30:
            if row['pic_num'] < 2:
                punish += 10
            if row['desc_len'] < 50:
                punish += 10
        if row['recent_cancelled_owner']:
            punish += 20
        # recent_paid = row['recent_paid']
        # recent_cancelled_renter = row['recent_cancelled_renter']
        # if recent_paid > 0 and recent_cancelled_renter / recent_paid > 0.3:
        #     punish += 20
        scores['w_punish'] = -punish
        # calc car score
        car_score = reduce(lambda x, y: x + y, scores.itervalues())
        # generate mysql row data
        rows = {}
        for k, v in scores.items():
            rows[k] = round(v, 2)
        rows['score'] = round(car_score, 2)
        rows['car_id'] = row['car_id']
        # distance
        rows['w_send'] = 0
        if row['owner_send'] and row['owner_send_desc_len'] > 15:
            rows['w_send'] = 0.5
        if row['owner_send_has_tags']:
            rows['w_send'] += 1
        if row['owner_send_distance'] >= 5:
            rows['w_send'] += 0.5
        return rows

    def update(self):
        sql = '''select *
            from car_rank_feats
            where update_time>'{}'
        '''.format(self.update_time)
        sql += self._and_cars('car_id')
        rows = self.db.exec_sql(sql)
        scores_list = []
        for row in rows:
            scores = self._calc_score(row)
            logger.debug('[rank] score: %s', scores)
            scores_list.append(scores)
        written = self._write_scores(scores_list)
        logger.info('[rank] updated %d car rank score', written)


def main():
    parser = argparse.ArgumentParser(description='calc car_score')
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
    parser.add_argument('--env', type=str,
                        help='deploy on test environment')
    parser.add_argument('--verbose', action='store_true', help='verbose log')
    args = parser.parse_args()

    before_minutes = args.before

    cars = []
    if args.cars:
        cars = args.cars.strip().split(',')

    logger.info('[start] rank_feats args: %s', args)

    with RankScore(before_mins=before_minutes,
                   throttling_num=args.throttling,
                   checkpoint_file=args.checkpoint,
                   cars=cars, env_flag=args.env) as obj:
        obj.update()

    logger.info('================')

if __name__ == "__main__":
    main()
