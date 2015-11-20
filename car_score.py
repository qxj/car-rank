#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; -*-
# @(#) car_score.py  Time-stamp: <Julian Qian 2015-11-20 17:17:01>
# Copyright 2015 Julian Qian
# Author: Julian Qian <junist@gmail.com>
# Version: $Id: car_score.py,v 0.1 2015-11-18 14:35:36 jqian Exp $
#

from __future__ import division
import sys
import argparse
import datetime
import logging
import pdb
import time

sys.path.append('./pdlib/py')
import mydb
from log import init_log

logger = None


class CarScore(object):
    def __init__(self, interval_minutes=5, throttling_num=0):
        self.db = mydb.get_db('master')
        self.db_score = mydb.get_db('master')
        # yesterday this time
        self.update_time = datetime.datetime.today() - \
                           datetime.timedelta(minutes=interval_minutes)
        logger.info('[init] update time: %s', self.update_time)
        self.throttling = Throttling(throttling_num)

    def commit(self):
        self.db.commit()
        self.db_score.commit()

    def _update(self, car_id, value_dict):
        # TODO anti snow
        self.throttling.check()
        return self.db.update('car_rank_feats', {'car_id': car_id}, value_dict)

    def _write_score(self, value_dict):
        self.throttling.check()
        return self.db_score.insert('car_rank_score', value_dict,
                                    on_duplicate_ignore=False)

    def _write_scores(self, value_dict_list):
        updated_cnt = 0
        dlen = len(value_dict_list)
        idx = 0
        batch_num = 100
        while idx < dlen:
            if idx % batch_num == 0:
                updated_cnt += self.db_score.insert_many(
                    'car_rank_score', value_dict_list[idx:idx+batch_num],
                    on_duplicate_ignore=False)
            idx += 1
        self.db_score.commit()
        return updated_cnt

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
        sql = '''update car_rank_feats cf
            join car_rank cr on cf.car_id=cr.car_id
            set cf.owner_send=cr.owner_can_send,
            cf.owner_send_desc_len=length(cr.owner_can_send_service),
            cf.recommend_level=cr.recommend_level
            where cr.update_time > '{}'
        '''.format(self.update_time)
        updated_cnt = self.db.exec_sql(sql, returnAffectedRows=True)
        self.db.commit()
        logger.info('[can_send] update %d car can_send info', updated_cnt)

    def update_can_send1(self):
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
                tk = irow['tag_keys']
                if tk:
                    keys = tk.split(',')
                    if '29' in keys or '30' in keys:
                        has_tags = 1
                owner_score += (irow['friendly_score'] + irow['punctual_score'])
                car_score += (irow['car_performance_score'] + irow['car_condition_score'])
            if review_cnt:
                os = owner_score/review_cnt/2
                cs = car_score/review_cnt/2
            data = {'owner_send_has_tags': has_tags,
                    'review_owner': os,
                    'review_car': cs}
            logger.debug('[tags] car %d review: %s ', car_id, data)
            updated_cnt += self._update(car_id, data)
        self.db.commit()
        logger.info('[review] update %d car tags info.', updated_cnt)

    # `auto_accept` tinyint(1) DEFAULT NULL COMMENT '是否开启自动接单',
    def update_accept(self):
        sql = '''update car_rank_feats cr
            join car_freetime cf on cr.car_id=cf.car_id
            set cr.auto_accept=if(cf.auto_accept='YES',1,0)
            where cf.last_update_time > '{}'
        '''.format(self.update_time)
        updated_cnt = self.db.exec_sql(sql, returnAffectedRows=True)
        self.db.commit()
        logger.info('[accept] update %d auto_accept', updated_cnt)

    def update_accept1(self):
        db = mydb.get_db('slave')
        sql = '''select car_id, if(auto_accept='YES',1,0) auto_accept
            from car_freetime
            where last_update_time > '{}'
        '''.format(self.update_time)
        rows = db.exec_sql(sql)
        updated_cnt = 0
        for row in rows:
            updated_cnt += self._update(row['car_id'], row)
        self.db.commit()
        logger.info('[accept] update %d auto_accept', updated_cnt)

    # `recent_rejected` int(11) DEFAULT NULL COMMENT '3个月内最近10个单里的拒单数',
    # `recent_accepted` int(11) DEFAULT NULL COMMENT '3个月内最近10个单里的接单数',
    # `recent_cancelled_owner` int(11) DEFAULT NULL COMMENT '最近一个月内车主取消订单数',
    # `recent_cancelled_renter` int(11) DEFAULT NULL COMMENT '1个月内最后10个支付后订单(不包含接收后订单)租客取消数',
    def update_orders(self):
        db = mydb.get_db('slave')
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
        self.db.commit()
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
        self.db.commit()
        logger.info('[car_info] update %d car_info', updated_cnt)

    def _calc_score(self, row):
        car_score = 0
        scores = {}
        # price
        suggest_price = row['suggest_price']
        proportion = row['proportion']
        if suggest_price < 200:
            if 0.8 < proportion < 1.05:
                scores['w_price'] = 30*(1.05-proportion)/(1.05-0.8)
            elif 1.3 < proportion < 1.6:
                scores['w_price'] = 20*(proportion-1.3)/(1.3-1.6)
        else:
            if 0.7 < proportion < 1.15:
                scores['w_price'] = 30*(1.15-proportion)/(1.15-0.7)
            elif 1.3 < proportion < 1.6:
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
        scores['car_id'] = row['car_id']
        scores['score'] = car_score
        return scores

    def update_scores(self):
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
        logger.info('[rank] updated %d car rank score', written)


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


def main():
    global logger

    parser = argparse.ArgumentParser(description='prepare & calc car_score')
    parser.add_argument('action', type=str, choices=('prepare',
                                                     'run'), help='actions')
    parser.add_argument('--init', action='store_true', help='init data')
    parser.add_argument('--throttling', type=int, default=100,
                        help='throttling update num per second')
    parser.add_argument('--interval', type=int, default=10,
                        help='interval minutes to update')
    parser.add_argument('--dry', action='store_true', help='whether dry run')
    parser.add_argument('--verbose', action='store_true', help='verbose log')
    args = parser.parse_args()

    log_level = logging.INFO
    if args.verbose:
        log_level = logging.DEBUG
    logger = init_log(logtofile='car_score.log', level=log_level)

    interval_minutes = args.interval
    if args.init:
        # only consider car actived in the past of half-year
        interval_minutes = 60*24*30*6

    cs = CarScore(interval_minutes, args.throttling)
    if args.action == 'prepare':
        cs.sync_cars()
        cs.update_proportion()
        cs.update_can_send()
        cs.update_review()
        cs.update_orders()
        cs.update_accept()
        cs.update_car_info()
    elif args.action == 'run':
        cs.update_scores()
    cs.commit()

if __name__ == "__main__":
    main()
