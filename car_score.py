#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; -*-
# @(#) car_score.py  Time-stamp: <Julian Qian 2015-11-19 15:27:20>
# Copyright 2015 Julian Qian
# Author: Julian Qian <junist@gmail.com>
# Version: $Id: car_score.py,v 0.1 2015-11-18 14:35:36 jqian Exp $
#

from __future__ import division
import sys
import argparse
import datetime
import logging
import time

sys.path.append('./pdlib/py')
import mydb
from log import init_log

logger = None


class CarScore(object):
    def __init__(self):
        self.db = mydb.get_db('slave')
        self.db_score = mydb.get_db('master')
        # yesterday this time
        self.update_time = datetime.datetime.today() - datetime.timedelta(1)

    def _update(self, car_id, value_dict):
        # TODO anti snow
        return self.db.update('car_rank_feats', {'car_id': car_id}, value_dict)

    def _write_score(self, value_dict):
        return self.db_score.insert('car_rank_score', value_dict,
                                    on_duplicate_ignore=False)

    def _write_scores(self, value_dict_list):
        return self.db_score.insert_many('car_rank_score', value_dict_list,
                                         on_duplicate_ignore=False)

    def sync_cars(self):
        sql = '''insert into car_rank_feats(car_id)
            select
            c.id as car_id
            from car c
            left join car_rank_feats cr on c.id=cr.car_id
            where cr.car_id is null and c.status='active'
        '''
        affected_rows = self.db.exec_sql(sql, needCommit=True,
                                         returnAffectedRows=True)
        logger.info("[sync] inserted %d new cars", affected_rows)
        # remove inactive cars
        # sql = '''delete cr from car_rank_feats cr
        #     left join car c on c.id=cr.car_id
        #     where c.id is null or c.status!='active'
        # '''
        # affected_rows = self.db.exec_sql(sql, needCommit=True,
        #                                  returnAffectedRows=True)
        # logger.info("[sync] remove %d obsolote cars", affected_rows)
        self.db.commit()

    # `proportion` float DEFAULT NULL COMMENT 'car_owner_price.proportion',
    def update_proportion(self):
        db = mydb.get_db('price')
        sql = '''select car_id, proportion
            from car_owner_price
            where update_time > '{}'
        '''.format(self.update_time)
        rows = db.exec_sql(sql)
        updated_cnt = 0
        for row in rows:
            updated_cnt += self._update(row['car_id'], row)
        self.db.commit()
        logger.info('[price] updated %d car proportion', updated_cnt)

    # `owner_send` tinyint(1) DEFAULT NULL,
    # `owner_send_desc_len` int(11) DEFAULT NULL,
    # `recommend_level` smallint(4) DEFAULT NULL,
    def update_can_send(self):
        db = mydb.get_db('slave')
        sql = '''select car_id, owner_can_send owner_send,
            length(owner_can_send_service) owner_send_desc_len,
            recommend_level from car_rank where update_time > '{}'
        '''.format(self.update_time)
        rows = db.exec_sql(sql)
        updated_cnt = 0
        for row in rows:
            updated_cnt += self._update(row['car_id'], row)
        self.db.commit()
        logger.info('[can_send] update %d car can_send info', updated_cnt)

    # `can_send_has_tags` tinyint(1) DEFAULT NULL,
    # `w_review_owner` float DEFAULT NULL COMMENT '3个月内最近10个订单对车主的评价分均分',
    # `w_review_car` float DEFAULT NULL COMMENT '3个月内最近10个订单对车辆的评价分均分',
    def update_review(self):
        db = mydb.get_db('slave')
        sql = '''select distinct(carid) car_id
            from order_reviews where date_created>'{}'
        '''.format(self.update_time)
        rows = db.exec_sql(sql)
        updated_cnt = 0
        for row in rows:
            car_id = row['car_id']
            sql = '''select tag_keys,
                friendly_score, punctual_score,
                car_performance_score, car_condition_score
                from order_reviews
                where carid={} and date_created>subdate(curdate(), 90)
                order by date_created limit 10
            '''.format(car_id)
            irows = db.exec_sql(sql)
            has_tags = 0
            owner_score = 0
            car_score = 0
            review_cnt = 0
            for irow in irows:
                review_cnt += 1
                tk = irows['tag_keys']
                if tk:
                    keys = tk.split(',')
                    if 29 in keys or 30 in keys:
                        has_tags = 1
                owner_score += (row['friendly_score'] + row['punctual_score'])
                car_score += (row['car_performance_score'] + row['car_condition_score'])
            if review_cnt:
                os = owner_score/review_cnt
                cs = car_score/review_cnt
            updated_cnt += self._update(car_id,
                                        {'can_send_has_tags': has_tags,
                                         'review_owner': os,
                                         'review_car': cs})
        logger.info('[tags] update %d car can_send_has_tags.', updated_cnt)

    # `auto_accept` tinyint(1) DEFAULT NULL COMMENT '是否开启自动接单',
    # `recent_rejected` int(11) DEFAULT NULL COMMENT '3个月内最近10个单里的拒单数',
    # `recent_accepted` int(11) DEFAULT NULL COMMENT '3个月内最近10个单里的接单数',
    # `recent_cancelled_owner` int(11) DEFAULT NULL COMMENT '最近一个月内车主取消订单数',
    # `recent_cancelled_renter` int(11) DEFAULT NULL COMMENT '1个月内最后10个支付后订单(不包含接收后订单)租客取消数',
    def update_accept(self):
        db = mydb.get_db('slave')
        sql = '''select car_id, auto_accept
            from car_freetime
            where last_update_time > '{}'
        '''.format(self.update_time)
        rows = db.exec_sql(sql)
        updated_cnt = 0
        for row in rows:
            updated_cnt += self._update(row['car_id'], row)
        logger.info('[accept] update %d auto_accept', updated_cnt)
        ## ----------------8<----------------
        sql = '''select distinct(carid) car_id
            from orders where mtime> '{}' and status='rejected'
        '''.format(self.update_time)
        rows = db.exec_sql(sql)
        updated_cnt = 0
        for row in rows:
            car_id = row['car_id']
            sql = '''select status
                from orders where carid={} and
                ctime>subdate(curdate(), 90)
                order by ctime desc limit 10
            '''.format(car_id)
            irows = db.exec_sql(sql)
            rejected_cnt = 0
            for irow in irows:
                if irow['status'] == 'rejected':
                    rejected_cnt += 1
            updated_cnt += self._update(car_id,
                                        {'recent_rejected': rejected_cnt})
        logger.info('[accept] update %d recent_rejected', updated_cnt)
        ## ----------------8<----------------
        sql = '''select distinct(carid) car_id
            from orders where mtime>'{}' and status!='rejected' and rtime>0
            and status_ext!=5
        '''.format(self.update_time)
        rows = db.exec_sql(sql)
        updated_cnt = 0
        for row in rows:
            car_id = row['car_id']
            sql = '''select status, status_ext, rtime
                from orders where carid={} and
                ctime>subdate(curdate(), 90)
                order by ctime desc limit 10
            '''.format(car_id)
            irows = db.exec_sql(sql)
            accepted_cnt = 0
            for irow in irows:
                if irow['status'] != 'rejected' and \
                   irow['rtime'] and irow['status_ext'] != 5:
                    accepted_cnt += 1
            updated_cnt += self._update(car_id,
                                        {'recent_accepted': accepted_cnt})
        logger.info('[accept] update %d recent_accepted', updated_cnt)
        ## ----------------8<----------------
        sql = '''select o.carid car_id, count(1) recent_cancelled_owner
            from orders o
            join (
                select distinct(carid) car_id
                from orders where mtime>'{}' and status='cancelled' and
                status_ext=5
            ) oc on o.carid=oc.car_id where o.ctime>subdate(curdate(),30)
                and status='cancelled' and status_ext=5
            group by o.carid
        '''.format(self.update_time)
        rows = db.exec_sql(sql)
        updated_cnt = 0
        for row in rows:
            updated_cnt += self._update(row['car_id'], row)
        logger.info('[accept] update %d recent_cancelled_owner', updated_cnt)
        ## ----------------8<----------------
        sql = '''select o.carid car_id,
            count(if(ptime>0,id,null)) recent_paid,
            count(if(status='cancelled' and status_ext=2,id,null)) recent_cancelled_renter
            from orders o
            join (
                select distinct(carid) car_id
                from orders where mtime>'{}' and status='cancelled' and
                status_ext=2
            ) oc on o.carid=oc.car_id where o.ctime>subdate(curdate(),30)
            group by o.carid
        '''.format(self.update_time)
        rows = db.exec_sql(sql)
        updated_cnt = 0
        for row in rows:
            updated_cnt += self._update(row['car_id'], row)
        logger.info('[accept] update %d recent_cancelled_renter', updated_cnt)

    # `pic_num` int(11) DEFAULT NULL,
    # `desc_len` int(11) DEFAULT NULL,
    def update_car_info(self):
        db = mydb.get_db('slave')
        sql = '''select id car_id,
            photos, length(description) desc_len
            from car
            where updated_on>'{}'
        '''.format(self.update_time)
        rows = db.exec_sql(sql)
        updated_cnt = 0
        for row in rows:
            pic_num = len(filter(lambda x:x, row['photos'].split(',')))
            updated_cnt += self._update(row['car_id'],
                                        {'pic_num': pic_num,
                                         'desc_len': row['desc_len']})
        logger.info('[car_info] update %d car_info', updated_cnt)

    def _calc_score(self, row):
        car_score = 0
        scores = {'car_id': row['car_id']}
        # price
        suggest_price = row['suggest_price']
        proportion = row['proportion']
        if suggest_price < 200:
            if 0.8 < proportion < 1.05:
                scores['w_price'] = 30*(1.05-proportion)/(1.05-0.8)
            if 1.3 < proportion < 1.6:
                scores['w_price'] = 20*(proportion-1.3)/(1.3-1.6)
        else:
            if 0.7 < proportion < 1.15:
                scores['w_price'] = 30*(1.15-proportion)/(1.15-0.7)
            if 1.3 < proportion < 1.6:
                scores['w_price'] = 30*(proportion-1.3)/(1.3-1.6)
        # distance
        if row['owner_send'] and row['owner_send_desc_len'] > 15:
            scores['w_send'] = 1
        if row['owner_send_has_tags']:
            scores['w_send'] = 4
        # accept
        if row['auto_accept']:
            scores['w_accept'] = 15
        else:
            scores['w_accept'] = row['recent_accepted']*1.5
            scores['w_accept'] = row['recent_rejected']*-1.5
        # review
        review_owner = row['review_owner']
        if review_owner > 3:
            scores['w_review_owner'] = 10*(review_owner - 3)/2
        review_car = row['review_car']
        if review_car > 3:
            scores['w_review_car'] = 10*(review_car - 3)/2
        # recommend
        recommend_level = row['recommend_level']
        if recommend_level > 10:
            scores['w_recommend'] = 15
        elif recommend_level > 0:
            scores['w_recommend'] = 10
        elif recommend_level < 0:
            scores['w_recommend'] = -20
        # manual
        scores['w_manual'] = row['manual_weight']
        # punish
        if row['pic_num'] < 4:
            car_score -= 10
        if row['desc_len'] < 100:
            car_score -= 10
        if row['recent_cancelled_owner']:
            car_score -= 20
        recent_paid = row['recent_paid']
        recent_cancelled_renter = row['recent_cancelled_renter']
        if recent_paid > 0 and recent_cancelled_renter/recent_paid > 0.3:
            car_score -= 20
        car_score += reduce(lambda x,y:x+y, scores.itervalues())
        scores['score'] = car_score
        return scores

    def update_rank(self):
        sql = '''select *
            from car_rank_feats
            where update_time>'{}'
        '''.format(self.update_time)
        rows = self.db.exec_sql(sql)
        scores_list = []
        for row in rows:
            scores = self._calc_score(row)
            logger.debug('score: %s', scores)
            scores_list.append(scores)
        written = self._write_scores(scores_list)
        logger.info('[rank] updated %d car rank', written)


class Throttling(object):
    def __init__(self, limit_per_sec):
        self.limit_per_sec = limit_per_sec
        self.curr_ts = 0
        self.cnt_this_sec = 0
        self.yield_sec = 0.005  # sleep 5 ms

    def check(self):
        ts = int(time.time())
        while ts == self.curr_ts and self.cnt_this_sec >= self.limit_per_sec:
            time.sleep(self.yield_sec)
            ts = int(time.time())
        if ts == self.curr_ts:
            self.cnt_this_sec += 1
        else:
            self.curr_ts = ts
            self.cnt_this_sec = 0


def main():
    global logger

    parser = argparse.ArgumentParser(description='prepare & calc car_score')
    parser.add_argument('action', type=str, choices=('prepare',
                                                     'run',
                                                     'test'), help='actions')
    parser.add_argument('--dry', action='store_true', help='whether dry run')
    parser.add_argument('--verbose', action='store_true', help='verbose log')
    args = parser.parse_args()

    if args.verbose:
        log_level = logging.DEBUG
    logger = init_log(logtofile='car_score.log', level=log_level)

    cs = CarScore()
    if args.action == 'prepare':
        cs.sync_cars()
        cs.update_proportion()
        cs.update_can_send()
        cs.update_review()
        cs.update_accept()
        cs.update_car_info()
    elif args.action == 'run':
        cs.update_rank()

if __name__ == "__main__":
    main()
