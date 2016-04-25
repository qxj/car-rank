#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; -*-
# @(#) car_score.py  Time-stamp: <Julian Qian 2016-03-02 14:50:09>
# Copyright 2015, 2016 Julian Qian
# Author: Julian Qian <junist@gmail.com>
# Version: $Id: car_score.py,v 0.1 2015-11-18 14:35:36 jqian Exp $
#

'''
http://wiki.dzuche.com/pages/viewpage.action?pageId=16319251
'''

from __future__ import division
import argparse
import cPickle
import datetime
import logging
import pdb
import sys
import time

sys.path.append('./pdlib/py')
import mydb
from log import init_log

logger = None


class CarScore(object):

    def __init__(self, before_mins=0, throttling_num=0,
                 checkpoint_file=None,
                 cars=[], is_test=False):
        self.is_test = is_test
        self.db = self._get_db('master')
        # yesterday this time
        self.update_time = self._update_time(checkpoint_file, before_mins)
        logger.info('[init] update time: %s', self.update_time)
        self.throttling = Throttling(throttling_num)
        # checkpoint properties
        self.current_time = datetime.datetime.now()
        self.checkpoint_file = checkpoint_file
        self.cars = cars

    def _get_db(self, flag):
        db_names = {'master': 'master',
                    'score': 'master',
                    'price': 'price',
                    'slave': 'slave'}
        if self.is_test:
            db_names = {'master': 'test28',
                        'score': 'test28',
                        'price': 'test28',
                        'slave': 'test28'}
        return mydb.get_db(db_names[flag])

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.db.commit()
        # sync checkpoint if everything ok
        self.set_checkpoint()
        logger.info('exit car score instance, and set checkpoint.')

    def set_checkpoint(self):
        try:
            with open(self.checkpoint_file, 'w') as fp:
                cPickle.dump(self.current_time, fp)
        except:
            logger.warn('failed to dump checkpoint file: %s',
                        self.checkpoint_file)

    def _update_time(self, checkpoint_file, before_minutes):
        ts = None
        if before_minutes > 0:
            ts = datetime.datetime.today() - \
                datetime.timedelta(minutes=before_minutes)
        else:
            try:
                with open(checkpoint_file) as fp:
                    ts = cPickle.load(fp)
            except:
                logger.warn('no checkpoint file is found: %s', checkpoint_file)
            if not isinstance(ts, datetime.datetime):
                ts = datetime.datetime.today() - datetime.timedelta(minutes=10)
                logger.warn('no timestamp is specified, set to %s', ts)
        return ts

    def _update(self, car_id, value_dict):
        # TODO anti snow
        self.throttling.check()
        return self.db.update('car_rank_feats', {'car_id': car_id}, value_dict)

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

    def _calc_score_old(self, row):
        recommend_weight = 18
        confirm_weight = 20
        rented_weight = 8
        review_weight = 18
        price_weight = 15
        newbie_weight = 18 * 2

        scores = {}

        recommend_level = row['recommend_level']
        if recommend_level == 1:
            scores['recommend'] = recommend_weight * 0.6
        elif recommend_level == 2:
            scores['recommend'] = recommend_weight
        elif recommend_level == 11:
            scores['recommend'] = recommend_weight * 2
        elif recommend_level == -1:
            scores['recommend'] = recommend_weight * (-2)

        ppnum = row['recent_paid1']
        pcnum = row['recent_completed1']
        past_confirm_score = 0
        mpnum = row['recent_paid']
        mcnum = row['recent_completed1']
        month_confirm_score = 0
        wpnum = row['recent_paid2']
        wcnum = row['recent_completed2']

        if ppnum < 1:
            past_confirm_score = 0
        elif ppnum < 3:
            past_confirm_score = (pcnum / ppnum) * 0.4 + (ppnum / 30) * 0.6
        elif ppnum < 6:
            past_confirm_score = (pcnum / ppnum) * 0.7 + (ppnum / 30) * 0.3
        else:
            past_confirm_score = (pcnum / ppnum) * 0.9 + (ppnum / 30) * 0.1
        if mpnum < 1:
            month_confirm_score = 0
        elif mpnum < 3:
            month_confirm_score = (mcnum / mpnum) * 0.4 + (mpnum / 15) * 0.6
        elif mpnum < 5:
            month_confirm_score = (mcnum / mpnum) * 0.7 + (mpnum / 15) * 0.3
        else:
            month_confirm_score = (mcnum / mpnum) * 0.9 + (mpnum / 15) * 0.1

        reco_punish_weight = 1
        past_reject_punish = 0
        if recommend_level > 0:
            reco_punish_weight = 0.6
        if ppnum == 0:
            past_reject_punish = 8
        elif ppnum == 1 and pcnum == 0:
            past_reject_punish = 10
        elif ppnum == 2 and pcnum == 0:
            past_reject_punish = 12
        elif ppnum == 2 and pcnum == 1:
            past_reject_punish = 4
        elif ppnum > 2 and ppnum <= 4 and pcnum / ppnum < 0.6:
            past_reject_punish = (0.6 - pcnum / ppnum) * 18
        elif ppnum > 4 and pcnum / ppnum < 0.6 and pcnum / ppnum >= 0.5:
            past_reject_punish = (0.6 - pcnum / ppnum) * 30
        elif ppnum > 4 and pcnum / ppnum < 0.5 and pcnum / ppnum >= 0.35:
            past_reject_punish = (0.6 - pcnum / ppnum) * 50 - 2
        elif ppnum > 4 and pcnum / ppnum < 0.35:
            past_reject_punish = (0.6 - pcnum / ppnum) * 80 - 9.5
        past_reject_punish = round(past_reject_punish, 2)
        week_reject_punish = 0
        wrnum = wpnum - wcnum
        if wrnum > 0:
            week_reject_punish = 7 * wrnum - 4
        scores['confirm'] = (past_confirm_score * 0.4 +
                             month_confirm_score * 0.6) * confirm_weight - (
            past_reject_punish +
            week_reject_punish) * reco_punish_weight

        # mth_time=row['month_rented_time']
        # reco_rented_weight=1
        # if recommend_level>0:
        #     reco_rented_weight=2
        # if mth_time<20:
        #     scores['rented']=(20-mth_time)/20 *rented_weight *reco_rented_weight

        pd = row['proportion'] * row['suggest_price']
        sp = row['suggest_price']
        if pd > 0 and sp > 0:
            if sp - pd >= 0:
                scores['price'] = round(
                    (((sp - pd) / sp) * 0.5 + (min((sp - pd), 200) / 200) * 0.5) * price_weight, 2)
            else:
                scores['price'] = round(
                    (((sp - pd) / sp) * 0.5 + (max((sp - pd), -200) / 200) * 0.5) * price_weight, 2)

        days = 0
        if row['verified_time']:
            ddays = datetime.datetime.today() - row['verified_time']
            days = ddays.days
        if days < 30:
            scores['newbie'] = newbie_weight

        rp = row['review_car']
        rc = row['review_cnt']
        if rc < 1:
            scores['review'] = 0
        elif rc < 3:
            scores['review'] = round(
                (((rp - 4) / 4) * 0.4 + (rc / 30) * 0.6) * review_weight, 2)
        elif rc < 5:
            scores['review'] = round(
                (((rp - 4) / 4) * 0.7 + (rc / 30) * 0.3) * review_weight, 2)
        else:
            scores['review'] = round(
                (((rp - 4) / 4) * 0.9 + (rc / 30) * 0.1) * review_weight, 2)

        scores['manual'] = row['manual_weight']
        final_score = reduce(lambda x, y: x + y, scores.itervalues())

        rows = {'final_score': final_score,
                'car_id': row['car_id']}
        return rows

    def update_scores_old(self):
        sql = '''select *
            from car_rank_feats
            where update_time>'{}'
        '''.format(self.update_time)
        sql += self._and_cars('car_id')
        rows = self.db.exec_sql(sql)
        for row in rows:
            scores = self._calc_score_old(row)
            logger.debug('[rank] score: %s', scores)
            sql = '''update car_rank
            set update_time=update_time, final_score={}
            where car_id={}
            '''.format(scores['final_score'], scores['car_id'])
            self.throttling.check()
            self.db.exec_sql(sql)
        self.db.commit()
        logger.info('[rank] updated %d car rank score old', written)

    def update_scores(self):
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
    parser.add_argument('action', type=str, choices=('run', 'prepare',
                                                     'test'), help='actions')
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
    logger = init_log(logtofile='car_score.log', level=log_level,
                      logtostderr=logtostderr)

    before_minutes = args.before

    logger.info('[start] car_score args: %s', args)

    cars = []
    if args.cars:
        cars = args.cars.strip().split(',')

    with CarScore(before_mins=before_minutes,
                  throttling_num=args.throttling,
                  checkpoint_file=args.checkpoint,
                  cars=cars, is_test=args.test) as cs:
        if args.action == 'prepare':
            cs.sync_cars()
            cs.update_cars()
            cs.update_proportion()
            cs.update_price_tuning()
            cs.update_can_send()
            cs.update_review()
            cs.update_collect()
            cs.update_orders()
            cs.update_accept()
        elif args.action == 'run':
            cs.update_scores()

    logger.info('================')

if __name__ == "__main__":
    main()