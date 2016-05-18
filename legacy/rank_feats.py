#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; -*-
# @(#) car_score.py  Time-stamp: <Julian Qian 2016-05-18 11:28:32>
# Copyright 2015, 2016 Julian Qian
# Author: Julian Qian <junist@gmail.com>
# Version: $Id: car_score.py,v 0.1 2015-11-18 14:35:36 jqian Exp $
#

'''
http://wiki.dzuche.com/pages/viewpage.action?pageId=16319251
'''

from __future__ import division
import argparse
import datetime
import logging
import sys
sys.path.append('./pdlib/py')
from log import init_log

from interval_db import IntervalDb

logger = None


class RankFeats(IntervalDb):

    def __init__(self, before_mins=0, throttling_num=0,
                 checkpoint_file=None,
                 cars=[], is_test=False):
        super(RankFeats, self).__init__(before_mins, checkpoint_file,
                                        throttling_num, is_test)
        self.cars = cars

    def _update(self, car_id, value_dict):
        # TODO anti snow
        self.throttling.check()
        return self.db.update('car_rank_feats', {'car_id': car_id}, value_dict)

    def _and_cars(self, field):
        return ' and {} in ({})'.format(field, ','.join(self.cars)) if self.cars else ''

    def sync_cars(self):
        sql = '''insert into car_rank_feats
            (car_id, city_code, verified_time)
            select
            c.id as car_id,
            c.city_code,
            c.verified_time
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

    # `pic_num` int(11) DEFAULT NULL,
    # `desc_len` int(11) DEFAULT NULL,
    def update_cars(self):
        sql = '''update car_rank_feats cf
            join car c on c.id=cf.car_id
            set cf.verified_time=c.verified_time,
                cf.city_code=c.city_code
            where c.updated_on > '{}'
        '''.format(self.update_time)
        sql += self._and_cars('c.id')
        updated_cnt = self.db.exec_sql(sql, returnAffectedRows=True)
        self.db.commit()
        logger.info('[can_send] update %d car info', updated_cnt)
        # update photo number and desc length
        db = self._get_db('slave')
        sql = '''select id car_id,
            photos, char_length(description) desc_len
            from car
            where updated_on>'{}'
        '''.format(self.update_time)
        sql += self._and_cars('id')
        rows = db.exec_sql(sql)
        updated_cnt = 0
        for row in rows:
            pic_num = len(filter(lambda x: x, row['photos'].split(',')))
            updated_cnt += self._update(row['car_id'],
                                        {'pic_num': pic_num,
                                         'desc_len': row['desc_len']})
            logger.debug('[accept] car %d pic_num %d, desc_len %d',
                         row['car_id'], pic_num, row['desc_len'])
        self.db.commit()
        logger.info('[car_info] update %d car_info, affected %d rows',
                    len(rows), updated_cnt)

    def update_price_tuning(self):
        sql = '''update car_rank_feats cf
        join price_tools_rank pt on cf.car_id=pt.car_id
        set cf.price_tuning=pt.score
        where pt.update_time > '{}'
        '''.format(self.update_time)
        sql += self._and_cars('pt.car_id')
        updated_cnt = self.db.exec_sql(sql, returnAffectedRows=True)
        self.db.commit()
        logger.info('[price_tools] update %d price tunning', updated_cnt)

    # `proportion` float DEFAULT NULL COMMENT 'car_owner_price.proportion',
    def update_proportion(self):
        db = self._get_db('price')
        sql = '''select car_id, proportion
            from car_owner_price
            where update_time > '{}'
        '''.format(self.update_time)
        sql += self._and_cars('car_id')
        rows = db.exec_sql(sql)
        updated_cnt = 0
        for row in rows:
            updated_cnt += self._update(row['car_id'], row)
            logger.debug('[price] update car %d proportion %f',
                         row['car_id'], row['proportion'])
        self.db.commit()
        logger.info('[price] updated %d car proportion, affected %d rows',
                    len(rows), updated_cnt)

    # `owner_send` tinyint(1) DEFAULT NULL,
    # `owner_send_desc_len` int(11) DEFAULT NULL,
    # `recommend_level` smallint(4) DEFAULT NULL,
    def update_can_send(self):
        sql = '''update car_rank_feats cf
            join car_rank cr on cf.car_id=cr.car_id
            set cf.owner_send=cr.owner_can_send,
            cf.owner_send_desc_len=char_length(cr.owner_can_send_service),
            cf.owner_send_distance=cr.owner_can_send_distance,
            cf.recommend_level=cr.recommend_level
            where cr.update_time > '{}'
        '''.format(self.update_time)
        sql += self._and_cars('cr.car_id')
        updated_cnt = self.db.exec_sql(sql, returnAffectedRows=True)
        self.db.commit()
        logger.info('[can_send] update %d car can_send info', updated_cnt)

    # `can_send_has_tags` tinyint(1) DEFAULT NULL,
    # `w_review_owner` float DEFAULT NULL COMMENT '3个月内最近10个订单对车主的评价分均分',
    # `w_review_car` float DEFAULT NULL COMMENT '3个月内最近10个订单对车辆的评价分均分',
    def update_review(self):
        db = self._get_db('slave')
        sql = '''select distinct(carid) car_id
            from order_reviews where date_created>'{}'
        '''.format(self.update_time)
        sql += self._and_cars('carid')
        logger.debug('[review] sql: %s', sql)
        rows = db.exec_sql(sql)
        updated_cnt = 0
        for row in rows:
            car_id = row['car_id']
            sql = '''select is_send_car,
                friendly_score, punctual_score,
                car_performance_score, car_condition_score
                from order_reviews
                where carid={} and date_created>subdate(curdate(), 60)
                order by date_created desc limit 4
            '''.format(car_id)
            irows = db.exec_sql(sql)
            owner_score = 0
            car_score = 0
            review_cnt = 0
            has_tags = 0
            for i, irow in enumerate(irows):
                review_cnt += 1
                if i < 2 and irow['is_send_car'] > 0:  # only consider recent two tags
                    has_tags = 1
                owner_score += (irow['friendly_score'] +
                                irow['punctual_score'])
                car_score += (irow['car_performance_score'] +
                              irow['car_condition_score'])
            os = cs = 0
            if review_cnt > 0:
                os = owner_score / review_cnt / 2
                cs = car_score / review_cnt / 2
            data = {'owner_send_has_tags': has_tags,
                    'review_owner': os,
                    'review_car': cs}
            updated_cnt += self._update(car_id, data)
            logger.debug('[review] car %d review: %s ', car_id, data)
        logger.info('[review] update %d car tags info, affected %d rows.',
                    len(rows), updated_cnt)
        # review count
        sql = '''update car_rank_feats cf
            join (
                select o.carid, count(id) cnt
                from order_reviews o join
                (
                    select distinct(carid) carid
                    from order_reviews where date_created>'{}'
                ) oo on oo.carid=o.carid
                group by o.carid
            ) r on r.carid=cf.car_id
            set cf.review_cnt=r.cnt
        '''.format(self.update_time)
        updated_cnt = self.db.exec_sql(sql, returnAffectedRows=True)
        logger.info('[review] update %d review cnt', updated_cnt)
        self.db.commit()

    # `collect_cnt` int(11) DEFAULT '0' COMMENT '收藏数',
    def update_collect(self):
        sql = '''update car_rank_feats cf
           join (
               select cc.car_id, count(id) cnt
               from car_collect cc
               where cc.status=1
               group by cc.car_id
           ) r on r.car_id=cf.car_id
           set cf.collect_cnt=r.cnt
        '''
        updated_cnt = self.db.exec_sql(sql, returnAffectedRows=True)
        logger.info('[collect] update %d collect cnt', updated_cnt)
        self.db.commit()

    # `auto_accept` tinyint(1) DEFAULT NULL COMMENT '是否开启自动接单',
    # `available_days` int(11) DEFAULT 0 COMMENT '最近一个月内可见可租天数',
    def update_accept(self):
        sql = '''update car_rank_feats cr
            join car_freetime cf on cr.car_id=cf.car_id
            set cr.auto_accept=if(cf.auto_accept='YES',1,0),
            cr.quick_accept=if(cf.quick_accept='YES',1,0),
            cr.available_days=if(cf.status=1,
                length(replace(substring(cf.freetime,1,30),'0','')),
                0)
            where cf.last_update_time > '{}'
        '''.format(self.update_time)
        sql += self._and_cars('cf.car_id')
        updated_cnt = self.db.exec_sql(sql, returnAffectedRows=True)
        self.db.commit()
        logger.info('[accept] update %d auto_accept', updated_cnt)
        # ================8<================
        # sql = '''update car_rank_feats cr
        #     join (
        #         select carid, sum(timestampdiff(day,
        #         if(begin<now(),now(),begin),
        #         if(end>adddate(now(),30),adddate(now(),30),end))) days
        #         from orders
        #         where ctime>'{}' and
        #         ctime>subdate(now(),30) and
        #         status in ('started','paid','paid_offence','confirmed')
        #         {}
        #         group by carid
        #     ) o on cr.car_id=o.carid
        #     set available_days=available_days-o.days
        # '''.format(self.update_time, self._and_cars('carid'))
        # updated_cnt = self.db.exec_sql(sql, returnAffectedRows=True)
        # logger.debug('[accept] sql: %s', sql)
        # self.db.commit()
        # logger.info('[accept] update %d avaiable days', updated_cnt)

    # `recent_rejected` int(11) DEFAULT NULL COMMENT '3个月内最近10个单里的拒单数',
    # `recent_accepted` int(11) DEFAULT NULL COMMENT '3个月内最近10个单里的接单数',
    # `recent_cancelled_owner` int(11) DEFAULT NULL COMMENT '最近一个月内车主取消订单数',
    # `recent_cancelled_renter` int(11) DEFAULT NULL COMMENT '1个月内最后10个支付后订单(不包含接收后订单)租客取消数',
    def update_orders(self):
        db = self._get_db('slave')
        # recent action (rejected/accepted)
        sql = '''select distinct(carid) car_id
            from orders where mtime> '{}' and rtime>0
        '''.format(self.update_time)
        sql += self._and_cars('carid')
        rows = db.exec_sql(sql)
        updated_cnt = 0
        today = datetime.datetime.now()
        for row in rows:
            car_id = row['car_id']
            sql = '''select id order_id, status, status_ext, uid, rtime,
                ifnull(timestampdiff(day, begin, end),0) days
                from orders where carid={} and
                ctime>subdate(curdate(), 90) and rtime>0
                order by ctime desc limit 10
            '''.format(car_id)
            irows = db.exec_sql(sql)
            rejected_cnt = accepted_cnt = 0
            rejected_today_cnt = 0
            users = set()
            for irow in irows:
                if irow['status'] == 'rejected' and \
                   irow['uid'] not in users:
                    rejected_cnt += 1
                    users.add(irow['uid'])
                    if irow['rtime']:
                        dd = today - irow['rtime']
                        if dd.days == 0:
                            rejected_today_cnt += 1
                elif irow['status'] != 'rejected' and \
                        irow['rtime'] and irow['status_ext'] != 5:
                    accepted_cnt += 1
                    days = min(int(irow['days'] / 3), 3)
                    if days > 0:
                        accepted_cnt += days
                        logger.debug('[accept] car %d long order %d (%d) add extra %d days',
                                     car_id, irow['order_id'], irow['days'], days)
            # rejected_cnt = max(rejected_cnt, (rejected_today_cnt - 1) * 100)
            rejected_cnt = rejected_cnt
            accepted_cnt = min(accepted_cnt, 10)
            updated_cnt += self._update(car_id,
                                        {'recent_rejected': rejected_cnt,
                                         'recent_accepted': accepted_cnt})
            logger.debug('[accept] car %d recent rejected %d, accepted %d',
                         car_id, rejected_cnt, accepted_cnt)
        logger.info('[accept] update %d recent_rejected, affected %d rows',
                    len(rows), updated_cnt)
        # recent cancelled (owner/renter)
        sql = '''select o.carid car_id,
            count(if(ptime>0 and o.ctime>subdate(curdate(),30),id,null)) recent_paid,
            count(if(ptime>0 and o.ctime>subdate(curdate(),60),id,null)) recent_paid1,
            count(if(ptime>0 and o.ctime>subdate(curdate(),7),id,null)) recent_paid2,
            count(if(status='completed' and o.ctime>subdate(curdate(),30),id,null)) recent_completed,
            count(if(status='completed' and o.ctime>subdate(curdate(),60),id,null)) recent_completed1,
            count(if(status='completed' and o.ctime>subdate(curdate(),7),id,null)) recent_completed2,
            count(if(status='cancelled' and status_ext=2 and o.ctime>subdate(curdate(),30),id,null)) recent_cancelled_renter,
            count(if(status='cancelled' and status_ext=5 and o.ctime>subdate(curdate(),30),id,null)) recent_cancelled_owner,
            count(if(status='cancelled' and status_ext=15 and o.ctime>subdate(curdate(),30),id,null)) recent_paid_cancelled_owner
            from orders o
            join (
                select distinct(carid) car_id
                from orders where mtime>'{}' and
                ( (status='cancelled' and status_ext in (2,5,15)) or
                  ptime>0)
                    {}
            ) oc on o.carid=oc.car_id
            where o.ctime>subdate(curdate(),60)
            group by o.carid
        '''.format(self.update_time, self._and_cars('carid'))
        rows = db.exec_sql(sql)
        updated_cnt = 0
        for row in rows:
            updated_cnt += self._update(row['car_id'], row)
            logger.debug('[accept] car %d recent cancelled, owner %d',
                         row['car_id'], row['recent_cancelled_owner'])
        logger.info('[accept] update %d recent cancelled, affected %d rows',
                    len(rows), updated_cnt)
        self.db.commit()

    def update_sales(self):
        db = self._get_db("slave")
        sql = """select carid, favourable
        from car_discount
        where update_time> '{}'
        """.format(self.update_time)
        sql += self._and_cars('carid')
        rows = db.exec_sql(sql)
        updated_cnt = 0
        for row in rows:
            try:
                data = {}
                favo = json.loads(row['favourable'])
                if "discount" in favo['sales']:
                    data['discount'] = 1
                if "vip" in favo['sales']:
                    data['vip'] = 1
                if "new_car_special" in favo['sales']:
                    data['new'] = 1
                updated_cnt += self._update(row['car_id'], data)
            except:
                logger.warn('invalid json from favourable')
        logger.info('[sales] update %d sales discount cars, affected % rows',
                    len(rows), updated_cnt)
        self.db.commit()

    def update(self):
        self.sync_cars()
        self.update_cars()
        self.update_proportion()
        self.update_price_tuning()
        self.update_can_send()
        self.update_review()
        self.update_collect()
        self.update_orders()
        self.update_accept()
        self.update_sales()
        self.db.commit()


def main():
    global logger

    parser = argparse.ArgumentParser(description='collect rank features')
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

    log_level = logging.INFO
    logtostderr = False
    if args.verbose:
        log_level = logging.DEBUG
        logtostderr = True
    logger = init_log(logtofile='rank_feats.log', level=log_level,
                      logtostderr=logtostderr)

    before_minutes = args.before

    cars = []
    if args.cars:
        cars = args.cars.strip().split(',')

    logger.info('[start] rank_feats args: %s', args)

    with RankFeats(before_mins=before_minutes,
                   throttling_num=args.throttling,
                   checkpoint_file=args.checkpoint,
                   cars=cars, is_test=args.test) as obj:
        obj.update()

    logger.info('================')

if __name__ == "__main__":
    main()
