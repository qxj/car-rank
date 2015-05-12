#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; -*-
# @(#) car_rank.py  Time-stamp: <Julian Qian 2015-05-12 15:46:23>
# Copyright 2015 Julian Qian
# Author: Julian Qian <junist@gmail.com>
# Version: $Id: car_rank.py,v 0.1 2015-01-16 15:07:34 jqian Exp $
#

'''pms7651
【需求背景】
现在平台上不仅有私家车主运营的车辆，还有全部委托给平台进行运营的全委托车辆，以及即将上线的半委托车辆（和全委托不同点：车主可反租自己的车，共用车主车位，共享车主人力资源进行送车）。而现在，一方面，全委托车辆的排序并不是使用大部分私家车主运营的车辆的rank模型进行排序的，而是直接根据一定规则做置顶处理；另一方面，即将上线的半委托车辆也需要考虑一种排序逻辑。所以希望以后不管是何种类型的车辆，都沿用统一的一套rank模型，这样不仅逻辑统一且清晰，而且为以后不同运营需求，提供更加灵活的调节空间。

【需求描述】
1. 现在rank模型的逻辑wiki为：http://pms.icarsclub.com/projects/website-cn/wiki/Car_rank_rule

2. 新的排序逻辑是：所有类型车辆都沿用rank模型的框架，但是不同类型车辆在“使用具体final_score的维度权重分配上”和“distance_score计算逻辑”会有所不同

3. 委托车辆&半委托车辆final_score考虑维度
（1）车辆接受率（f_score）：只要现在该车辆为委托车辆，那么不论是否带着时间搜索的排序，都认为接受率是100%

（2）车辆价格（ f_score）：只要现在该车辆为委托车辆，就取该车的“半委托期平日价”作为价格依据，得出价格得分权重

（3）车辆评价（ f_score）：使用实际车辆评价进行计算

（4）车辆级别（ f_score）：
a. 计算逻辑：可以区分全委托，半委托做不同的加权处理。以后会有计划把所有全委托迁移到半委托，所以迁移后需要识别车辆的委托期长短
b. 特殊处理：实现“随着委托期越长，该部分得分越高或者越低”，可见通过调节rank逻辑，从而实现相悖的效果

（5）自然月已出租天数（ f_score）：仍沿用现在的逻辑即可

（6）未来七天可出租天数（ f_score）：仍沿用现在的计算逻辑即可

——委托车辆（全委托&半委托）6个指标的重要性排序：（4）>（6）>（2）>（1）>（3）>（5）

4. dist_score计算逻辑：
（1）天春已经做了“全委托和免费送车逻辑解耦”需求，所以以后不再根据是否是全委托车辆来影响排序，而是根据是否免费送车
（2） distance_score在现有计算逻辑下（车辆取车位置和用户距离）得分基础上，若可以提供免费送车的车辆得到一个得分加权，加权到一定程度效果等价于置顶。并且要考虑如何实现“免费送车车辆之间的相对排序”和“免费送车和非免费送车之间的相对排序”两个目标

5. 体验性提升：
（1）品牌&车型去重：若排序中前5条/前10条/前20条/前50条结果汇总，存在超过相同品牌&车型的车辆超过3条/6条/12条/30条时，对相同车型里面的最后1条/2条/4条/10条做降权处理
（2）连续拒单立即降权处理：若一周内有n笔拒单（不连续也可以）则对该车做降权处理，n从2开始，n越大降权越厉害，并且该降权生效时间越长


rules:
## recommend_level in (1,2)
## recommend_level in (11,12)
## price score
## confirmed score
## review score
'''

from __future__ import division
import os
import sys
import argparse
import datetime
import time
import subprocess
import collections
import select
import logging

sys.path.append('./pdlib/py')
import mydb
from utils import SingletonLock, sign
from log import init_log

if SingletonLock("/tmp/_{}.lck".format(os.path.basename(sys.argv[0]))).locked():
    print >> sys.stderr, "another {} instance is running".format(sys.argv[0])
    sys.exit(-1)

logger = None

class RankTable(object):
    def __init__(self, dbhost, exp=False, dry=False, cars=[]):
        self.dry = dry
        self.exp = exp
        self.dbw = mydb.get_db(dbhost, conv=True)
        if dbhost == 'master':
            self.dbr = mydb.get_db('slave', conv=True)
        else:
            self.dbr = mydb.get_db(dbhost, conv=True)
        if len(cars):
            cars.append(0)
        self.cars = tuple(cars)

    def sync_cars(self):
        sql = '''insert into car_rank(car_id)
        select
        distinct c.id as car_id
        from car c
        left join car_rank cr on c.id=cr.car_id
        where cr.car_id is null and c.status='active'
        '''
        affected_rows = self.dbw.exec_sql(sql, needCommit=True, returnAffectedRows=True)
        logger.info("inserted {} new cars".format(affected_rows))
        # remove inactive cars
        sql = '''delete cr from car_rank cr
        left join car c on c.id=cr.car_id
        where c.id is null or c.status!='active'
        '''
        affected_rows = self.dbw.exec_sql(sql, needCommit=True, returnAffectedRows=True)
        logger.info("remove {} obsolote cars".format(affected_rows))
        self.dbw.commit()

    def update_car_info(self):
        sql = '''select
            c.id as car_id, c.price_daily, cs.suggest_price, cs.review as review_point, cs.review_cnt,
            if(locate('1',cf.freetime)>0,locate('1',cf.freetime)-1,length(cf.freetime)) as recent_rentday,
            length(replace(left(cf.freetime,7),'1','xx'))-7 week_freetime
        from car c
        join car_rank cr on c.id=cr.car_id
        join car_stats cs on c.id=cs.cid
        join car_freetime cf on c.id=cf.car_id
        '''
        if len(self.cars):
            sql += '''
            where cr.car_id in {}
            '''.format(self.cars)
        rows = self.dbr.exec_sql(sql)
        updated_cnt = 0
        for row in rows:
            updated_cnt += self.dbw.update('car_rank', {'car_id': row['car_id']}, row)
        self.dbw.commit()
        logger.info('updated {} car info'.format(updated_cnt))

    def update_car_hosted_info(self):
        sql = '''select cr.car_id, ch.hosted_price,
        if(hosted_end<now(),0,timestampdiff(hour,
            if(hosted_start<now(),now(),hosted_start),hosted_end))/24 as hosted_days
        from car_rank cr
        join car_hosted ch on cr.car_id=ch.car_id
        '''
        if len(self.cars):
            sql += '''
            where cr.car_id in {}
            '''.format(self.cars)
        rows = self.dbr.exec_sql(sql)
        updated_cnt = 0
        for row in rows:
            updated_cnt += self.dbw.update('car_rank', {'car_id': row['car_id']}, row)
        self.dbw.commit()
        logger.info('updated {} car hosted info'.format(updated_cnt))

    def update_car_order_info(self):
        sql = '''select car_id,
            count(distinct 60_paid) as past_paid_order_cnt,
            count(distinct 60_confirm) as past_confirm_order_cnt,
            count(distinct 30_paid) as month_paid_order_cnt,
            count(distinct 30_confirm) as month_confirm_order_cnt,
            count(distinct 30_reject_m) as month_reject_m_cnt,
            count(distinct 30_reject_a) as month_reject_a_cnt,
            count(distinct 30_owner_cancel) as month_owner_cancel_cnt,
            count(distinct 7_paid) as week_paid_order_cnt,
            count(distinct 7_confirm) as week_confirm_order_cnt,
            round(sum((30_rent div 24) + if((30_rent mod 24)>=8, 1, (30_rent mod 24)/8)),2) as month_rented_time
        from
        (select o.carID as car_id,
            (case when timestampdiff(day, o.ctime, now())<=60 and
                (o.status in ('rejected', 'confirmed','paid_offence','started','completed')
                or (o.status='cancelled' and o.status_ext not in(0,1,2,3) and UNIX_TIMESTAMP(o.ptime)<>0))
                then o.id else null end) as 60_paid,
            (case when timestampdiff(day, o.ctime, now())<=60 and
                (o.status in ('confirmed','paid_offence','started','completed')
                or (o.status='cancelled' and o.status_ext not in(0,1,2,3) and UNIX_TIMESTAMP(o.ptime)<>0))
                then o.id else null end) as 60_confirm,
            (case when timestampdiff(day, o.ctime, now())<=30 and
                (o.status in ('rejected', 'confirmed','paid_offence','started','completed')
                or (o.status='cancelled' and o.status_ext not in(0,1,2,3) and UNIX_TIMESTAMP(o.ptime)<>0))
                then o.id else null end) as 30_paid,
            (case when timestampdiff(day, o.ctime, now())<=30 and
                (o.status in ('confirmed','paid_offence','started','completed')
                or (o.status='cancelled' and o.status_ext not in(0,1,2,3) and UNIX_TIMESTAMP(o.ptime)<>0))
                then o.id else null end) as 30_confirm,
            (case when timestampdiff(day, o.ctime, now())<=30 and
                o.status='rejected' and o.status_ext=0
                then o.id else null end) as 30_reject_m,
            (case when timestampdiff(day, o.ctime, now())<=30 and
                o.status='rejected' and o.status_ext=13
                then o.id else null end) as 30_reject_a,
            (case when timestampdiff(day, o.ctime, now())<=30 and
                o.status='cancelled' and o.status_ext in (5,15) and UNIX_TIMESTAMP(o.ptime)<>0
                then o.id else null end) as 30_owner_cancel,
            (case when timestampdiff(day, o.ctime, now())<=7 and
                (o.status in ('rejected', 'confirmed','paid_offence','started','completed')
                or (o.status='cancelled' and o.status_ext not in(0,1,2,3) and UNIX_TIMESTAMP(o.ptime)<>0))
                then o.id else null end) as 7_paid,
            (case when timestampdiff(day, o.ctime, now())<=7 and
                (o.status in ('confirmed','paid_offence','started','completed')
                or (o.status='cancelled' and o.status_ext not in(0,1,2,3) and UNIX_TIMESTAMP(o.ptime)<>0))
                then o.id else null end) as 7_confirm,
            (case when o.status in ('confirmed','paid_offence','started','completed') and not
                    (o.begin>month_end or o.end<month_begin)
                then (case when o.begin<month_begin and o.end<month_end then timestampdiff(hour,month_begin,o.end)
                        when o.begin<month_begin and o.end>month_end then timestampdiff(hour,month_begin,month_end)
                        when o.begin>month_begin and o.end<month_end then timestampdiff(hour,o.begin,o.end)
                        when o.begin>month_begin and o.end>month_end then timestampdiff(hour,o.begin,month_end)
                        else null end)
                else null end) as 30_rent
        from orders o
        join car_rank cr on cr.car_id=o.carID
        join
        (select o.id,
            date_add(curdate(),interval-day(curdate())+1 day) as month_begin,
            date_add(curdate()-day(curdate())+1,interval 1 month) as month_end
        from orders o
        ) t1 on t1.id=o.id
        ) t2
        '''
        if len(self.cars):
            sql += '''
            where car_id in {}
            '''.format(self.cars)
        sql += '''
        group by car_id
        '''
        rows = self.dbr.exec_sql(sql)
        updated_cnt = 0
        for row in rows:
            updated_cnt += self.dbw.update('car_rank', {'car_id': row['car_id']}, row)
        self.dbw.commit()
        logger.info('update {} car order info'.format(updated_cnt))

    def update_car_score(self):
        signed_weight    = 5
        recommend_weight = 18
        confirm_weight   = 20
        rented_weight    = 8
        review_weight    = 18
        price_weight     = 15
        sql = '''select * from car_rank
        '''
        if len(self.cars):
            sql += '''
            where car_id in {}
            '''.format(self.cars)
        rows = self.dbr.exec_sql(sql)
        updated_cnt = 0
        for row in rows:
            car_id = row['car_id']
            scores = collections.defaultdict(lambda:0)
            if row['signed_level']>0:
                scores['signed']=signed_weight

            recommend_level=row['recommend_level']
            if recommend_level==1:
                scores['recommend']=recommend_weight*0.6
            elif recommend_level==2:
                scores['recommend']=recommend_weight
            elif recommend_level==11:
                scores['recommend']=recommend_weight*2.5
            elif recommend_level==-1:
                scores['recommend']=recommend_weight*(-2)

            ppnum=row['past_paid_order_cnt']
            pcnum=row['past_confirm_order_cnt']
            past_confirm_score=0
            mpnum=row['month_paid_order_cnt']
            mcnum=row['month_confirm_order_cnt']
            month_confirm_score=0
            wpnum=row['week_paid_order_cnt']
            wcnum=row['week_confirm_order_cnt']

            if ppnum<1:
                past_confirm_score=0
            elif ppnum<3:
                past_confirm_score=(pcnum/ppnum)*0.4+(ppnum/30)*0.6
            elif ppnum<6:
                past_confirm_score=(pcnum/ppnum)*0.7+(ppnum/30)*0.3
            else:
                past_confirm_score=(pcnum/ppnum)*0.9+(ppnum/30)*0.1
            if mpnum<1:
                month_confirm_score=0
            elif mpnum<3:
                month_confirm_score=(mcnum/mpnum)*0.4+(mpnum/15)*0.6
            elif mpnum<5:
                month_confirm_score=(mcnum/mpnum)*0.7+(mpnum/15)*0.3
            else:
                month_confirm_score=(mcnum/mpnum)*0.9+(mpnum/15)*0.1

            reco_punish_weight=1
            if recommend_level>0:
                reco_punish_weight=0.6
            past_reject_punish=0
            if ppnum==0:
                past_reject_punish=8
            elif ppnum==1 and pcnum==0:
                past_reject_punish=10
            elif ppnum==2 and pcnum==0:
                past_reject_punish=12
            elif ppnum==2 and pcnum==1:
                past_reject_punish=4
            elif ppnum>2 and ppnum<=4 and pcnum/ppnum<0.6:
                past_reject_punish=(0.6-pcnum/ppnum)*18
            elif ppnum>4 and pcnum/ppnum<0.6 and pcnum/ppnum>=0.5:
                past_reject_punish=(0.6-pcnum/ppnum)*30
            elif ppnum>4 and pcnum/ppnum<0.5 and pcnum/ppnum>=0.35:
                past_reject_punish=(0.6-pcnum/ppnum)*50-2
            elif ppnum>4 and pcnum/ppnum<0.35:
                past_reject_punish=(0.6-pcnum/ppnum)*80-9.5
            past_reject_punish=round(past_reject_punish,2)
            week_reject_punish=0
            wrnum=wpnum-wcnum
            if wrnum>0:
                week_reject_punish=7*wrnum-4
            scores['confirm']=(past_confirm_score*0.4+
                               month_confirm_score*0.6 )*confirm_weight - (
                                   past_reject_punish+
                                   week_reject_punish)*reco_punish_weight

            mth_time=row['month_rented_time']
            wek_free=row['week_freetime']
            reco_rented_weight=1
            if recommend_level>0:
                reco_rented_weight=2
            if mth_time<20 or wek_free>0:
                scores['rented']=(((20-mth_time)/20)*0.2 +
                                  (wek_free/7)*0.8)*rented_weight *reco_rented_weight
            if wek_free<=2:
                scores['rented']-=(3-wek_free)*6

            if self.exp:
                recent_rentday = row['recent_rentday']
                recent_weight = -15
                if recent_rentday > 0:
                    if recent_rentday >= 1:
                        scores['recent'] += 2
                    if recent_rentday >= 3:
                        scores['recent'] += 3
                    if recent_rentday >= 7:
                        scores['recent'] += 1
                    scores['recent'] *= recent_weight

            pd=row['price_daily']
            if recommend_level in (11,12) and row['hosted_price']>0:
                pd = row['hosted_price']
            sp=row['suggest_price']
            if pd>0 and sp>0:
                if sp-pd>=0:
                    scores['price']=round((((sp-pd)/sp)*0.5+(min((sp-pd),200)/200)*0.5)*price_weight,2)
                else:
                    scores['price']=round((((sp-pd)/sp)*0.5+(max((sp-pd),-200)/200)*0.5)*price_weight,2)

            rp=row['review_point']
            rc=row['review_cnt']
            if rc<1:
                scores['review']=0
            elif rc<3:
                scores['review']=round((((rp-4)/4)*0.4+(rc/30)*0.6)*review_weight,2)
            elif rc<5:
                scores['review']=round((((rp-4)/4)*0.7+(rc/30)*0.3)*review_weight,2)
            else:
                scores['review']=round((((rp-4)/4)*0.9+(rc/30)*0.1)*review_weight,2)

            # hosted cars
            if self.exp and recommend_level in (11,12):
                if recommend_level == 11: # full hosted
                    hosted_weight = 15
                elif recommend_level == 12: # half hosted
                    hosted_weight = 5
                hosted_days = row['hosted_days']
                scores['hosted'] = 20 + hosted_weight*(1-min(hosted_days,7)/7)
                # scores['hosted'] = 20 + hosted_weight*min(
                #     max(pow(min(abs(hosted_days-3),0.5),-0.2),
                #         2),
                #     0.5)

            # can_send cars
            if self.exp and row['can_send'] > 0:
                scores['send'] = 0

            scores['manual'] = row['manual_weight']
            final_score = reduce(lambda x,y:x+y, scores.itervalues())
            if self.cars and self.dry:
                print '#'*80
                print '''car_id: %d\tfinal_score: %f
                ''' % (car_id, final_score)
                for k, v in row.iteritems():
                    if 'score' not in k and k not in ('email', 'head_uin', 'car_id'):
                        print '{}: {}'.format(k, v)
                print '-'*10
                for k, v in scores.iteritems():
                    print '{}: {}'.format(k, v)
            if self.dry:
                continue
            updated_cnt += self.dbw.update('car_rank', {'car_id': car_id},
                                          {'final_score': final_score,
                                           'signed_score': scores['signed'],
                                           'recommend_score': scores['recommend'],
                                           'confirm_score': scores['confirm'],
                                           'rented_score': scores['rented'],
                                           'price_score': scores['price'],
                                           'review_score': scores['review']})

        self.dbw.commit()
        logger.info('updated {} car score'.format(updated_cnt))

    def update_holiday_price(self, weight):
        if self.dry:
            sql = '''select cr.car_id, cr.manual_weight
            from car_rank cr
            join car_holiday_price chp on cr.car_id=chp.carid
            where chp.holiday_price>0 and chp.holiday_type=9
            '''
            rows = self.dbr.exec_sql(sql, resultFormat='tuple')
            for row in rows:
                print row[0], row[1]
            print >> sys.stderr, "affected %d rows" % len(rows)
        else:
            sql = '''update car_rank cr
            join car_holiday_price chp on cr.car_id=chp.carid
            set cr.manual_weight=%d
            where chp.holiday_price>0 and chp.holiday_type=9
            ''' % weight
            affected_rows = self.dbw.exec_sql(sql, returnAffectedRows=True)
            self.dbw.commit()
            logger.info('update {} car manual weight'.format(affected_rows))

    def sync_hosted(self):
        dbc = mydb.db_conf('entrust', writable=True)
        cmd = '/home/work/mysql/bin/mysqldump -h{} -u{} -p{} --opt {} car_hosted car_extend car_park > /tmp/p7651.sql'.format(
            dbc['host'], dbc['user'], dbc['passwd'], dbc['dbname'])
        ret = subprocess.call(cmd, shell=True)
        if ret!= 0:
            logger.error(("failed to dump car_hosted from agent, ret: {}\n{}".format(ret, cmd)))
            return -1
        logger.info("dump car_hosted from agent, ret: {}".format(ret))
        dbc = mydb.db_conf('slave', writable=True)
        cmd = 'cat /tmp/p7651.sql | /home/work/mysql/bin/mysql -h{} -u{} -p{} {}'.format(
            dbc['host'], dbc['user'], dbc['passwd'], dbc['dbname'])
        ret = subprocess.call(cmd, shell=True)
        if ret != 0:
            logger.info("failed to import car_hosted to icars_zh, ret: {}\n{}".format(ret, cmd))
            return -1
        logger.info("import car_hosted to icars_zh, ret: {}".format(ret))

    def fix_suggest_price(self):
        db = mydb.get_db('entrust', conv=True)
        update_cnt = db.update('car_hosted', {'hosted_price': 0},
                               {'hosted_price': 399,
                                'hosted_holiday_price': 499})
        db.commit()
        logger.info("fixed {} cars' suggest price".format(update_cnt))

    def holiday_workaround_price(self):
        """downvote car if it's rented in 2015-02-19
        expect final_score: [30, 70]
        """
        sql = '''select
        chp.carid,
        chp.holiday_price,
        cr.suggest_price,
        cr.final_score
        from car_holiday_price chp
        join car_rank cr on cr.car_id=chp.carid
        where chp.id is not null and chp.holiday_price>0 and chp.holiday_type=9
            and cr.can_send=0
        group by chp.carid
        '''
        rows = self.dbw.exec_sql(sql)
        if self.dry:
            print >> sys.stderr, 'there are {} holiday cars'.format(len(rows))
        updated_cnt = 0
        price_punish_weight = 20
        for row in rows:
            car_id = row['carid']
            hp = row['holiday_price']
            sp = row['suggest_price']
            if sp == 0: continue
            final_score = 0
            if sp>0:
                # expect [-1, 2.5]
                punish_score = (min((hp-sp)/sp,1)*0.5 + min(pow(hp/500,3),2)*1)*price_punish_weight
                final_score = min(max(80 - punish_score, 30), 70)
                if final_score < row['final_score']:
                    final_score = row['final_score']
                if self.dry:
                    print '{}\t{}\t{}\t{}\t{:.0f}'.format(car_id, final_score, hp, sp, row['holiday_rented'])
                else:
                    updated_cnt += self.dbw.update('car_rank',
                                                  {'car_id': car_id},
                                                  {'final_score': final_score})
        self.dbw.commit()
        logger.info('[workaround] update {} holiday cars'.format(updated_cnt))

    def holiday_workaround_unavailable(self):
        '''downvote car if it is unrented in 2015-02-19'''
        sql = '''select
        car_id,
        final_score,
        length(replace(7_holiday,'0','xx'))-7 7_unava_day,
        length(replace(3_holiday,'0','xx'))-3 3_unava_day
        from
        (
        select
        cr.car_id,
        cr.final_score,
        substring(cf.freetime,timestampdiff(day,date(now()),'2015-02-18'),7) 7_holiday,
        substring(cf.freetime,timestampdiff(day,date(now()),'2015-02-18'),3) 3_holiday
        from car_rank cr
        join car_freetime cf on cr.car_id=cf.car_id
        ) t where locate('0', 7_holiday)>0
        '''
        rows = self.dbw.exec_sql(sql)
        updated_cnt = 0
        unavailable_punish_weight=40
        for row in rows:
            final_score = row['final_score']-((pow(row['7_unava_day']/7,2)+
                                               pow(row['3_unava_day']/3,2)*5))*unavailable_punish_weight
            if self.dry:
                print '{}\t{:.2f}\t{:.2f}\t{}\t{}'.format(row['car_id'],
                                                          row['final_score'],
                                                          final_score,
                                                          row['7_unava_day'],
                                                          row['3_unava_day'])
            else:
                updated_cnt += self.dbw.update('car_rank',
                                              {'car_id': row['car_id']},
                                              {'final_score': final_score})
        if not self.dry:
            self.dbw.commit()
            logger.info('[workaround] downvot {} holiday unavailable cars'.format(updated_cnt))

    def holiday_workaround_hosted(self):
        '''
        置顶半托管车辆
        expected score: [50, 90]
        '''
        sql = '''select
        cr.car_id,
        cr.suggest_price,
        cr.final_score,
        ch.hosted_price,
        ch.min_duration,
        sum(if(do.status in ('confirmed','started') and
            '2015-02-19' between date(do.begin) and date(do.end),1,0)) holiday_rented
        from car_rank cr
        join car_hosted ch on ch.car_id=cr.car_id
        left join orders do on do.carid=cr.car_id
        where cr.recommend_level=12 and cr.can_send=0
        group by cr.car_id
        '''
        rows = self.dbw.exec_sql(sql)
        updated_cnt = 0
        price_punish_weight = 20
        for row in rows:
            car_id = row['car_id']
            final_score = 0
            if row['min_duration'] < 480:
                sp = row['suggest_price']
                hp = row['hosted_price']
                if row['holiday_rented'] == 0 and sp>0:
                    # expect [-1, 1]
                    punish_score = (min((hp-sp)/sp,1) + min((hp-sp)/500,1))*price_punish_weight
                    final_score = min(max(100 - punish_score, 50), 90)
                    if final_score < row['final_score']:
                        final_score = row['final_score']
                else:
                    final_score = -30
            else:
                final_score = -100
            if self.dry:
                print '{}\t{}\t{}\t{}\t{:.0f}'.format(car_id, final_score, hp, sp, row['holiday_rented'])
            else:
                updated_cnt += self.dbw.update('car_rank',
                                              {'car_id': car_id},
                                              {'final_score': final_score})
        self.dbw.commit()
        logger.info('[workaround] update {} hosted cars'.format(updated_cnt))

    def holiday_workaround_sanya(self):
        '''更新三亚全托管车辆manual_weight权重 +200
        '''
        sql = '''select
        cr.car_id,
        cr.final_score
        from car_rank cr
        join car c on cr.car_id=c.id
        where c.city_code='460200' and cr.recommend_level=11
        '''
        rows = self.dbw.exec_sql(sql) # avoid master/slave inconsistent when sync
        updated_cnt = 0
        for row in rows:
            car_id = row['car_id']
            final_score = row['final_score'] + 1000
            updated_cnt += self.dbw.update('car_rank',
                                          {'car_id': car_id},
                                          {'final_score': final_score})
        self.dbw.commit()
        logger.info('[workaround] update {} sanya full-hosted cars'.format(updated_cnt))

def main():
    global logger

    parser = argparse.ArgumentParser(description='cron task')
    parser.add_argument('action', type=str, choices=('holiday_price',
                                                     'sync_hosted',
                                                     'update_rank',
                                                     'fix_price',
                                                     'test'), help='actions')
    parser.add_argument('--weight', type=int, help='weight for holiday price')
    parser.add_argument('--dbhost', type=str, default='master',
                        help='action on which db')
    parser.add_argument('--exp', action='store_true', help='whether active experiment')
    parser.add_argument('--holiday', action='store_true', help='holiday patch policy')
    parser.add_argument('--logfile', type=str, help='log file path')
    parser.add_argument('--cars', type=str, help='test cars (id)')
    parser.add_argument('--dry', action='store_true', help='whether dry run')
    parser.add_argument('--verbose', action='store_true', help='print verbose log')
    args = parser.parse_args()

    log_level = logging.INFO
    if args.verbose:
        log_level = logging.DEBUG

    if args.logfile:
        logger = init_log(logtofile=args.logfile, level = log_level)
    else:
        logger = init_log(logtofile="car_rank.log", level = log_level)

    update_cars = []
    if args.cars:
        for carid in args.cars.split(','):
            update_cars.append(int(carid))
    if select.select([sys.stdin,],[],[],0.0)[0]:
        for line in sys.stdin:
            update_cars.append(int(line.strip()))

    db = RankTable(args.dbhost, exp=args.exp, dry=args.dry, cars=update_cars)
    if args.action == 'holiday_price':
        db.update_holiday_price(int(args.weight))
    elif args.action == 'sync_hosted':
        db.sync_hosted()
    elif args.action == 'fix_price':
        db.fix_suggest_price()
    elif args.action == 'update_rank':
        db.sync_cars()
        db.update_car_info()
        db.update_car_hosted_info()
        db.update_car_order_info()
        db.update_car_score()
        if args.holiday:
            # db.holiday_workaround_price()
            # db.holiday_workaround_hosted()
            db.holiday_workaround_sanya()
            # db.holiday_workaround_unavailable()
    elif args.action == 'test':
        db.holiday_workaround_unavailable()

if __name__ == "__main__":
    main()
