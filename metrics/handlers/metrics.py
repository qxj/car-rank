#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; -*-
# @(#) metrics.py  Time-stamp: <Julian Qian 2015-04-22 16:55:04>
# Copyright 2015 Julian Qian
# Author: Julian Qian <junist@gmail.com>
# Version: $Id: metrics.py,v 0.1 2015-02-05 10:33:06 jqian Exp $
#

from collections import defaultdict
import json
import time
import urllib

from tornado.log import app_log

import base
from utils.xcrypt import Xcrypt

class MetricsHandler(base.BaseHandler):
    def get(self):
        lat = self.get_argument('lat', 0)
        lng = self.get_argument('lng', 0)
        isExp = 1 if int(self.get_argument('exp', 0)) > 0 else 0
        car_list = []
        time_delta = 0
        city_code = '110100'
        if lat>0 and lng>0:
            city_code = self.get_argument('city_code', '110100')
            limit = int(self.get_argument('limit', 100))
            sql = '''select
            rule
            from car_rank_rule
            where enable=1
            '''
            rows = self.db.exec_sql(sql)
            rank_rule = rows[0]['rule']
            sql = '''SELECT SQL_NO_CACHE *,
            {rank_rule} rank_score
            FROM
            (
                SELECT
                id,userID,latitude,longitude,manual_transmission,min_duration,
                max_duration,review,agent_min_duration,review_cnt,verified_time,
                confirmed_rate_app,rank_score1,rank_score2,has_box,recommend_level,
                can_send,signed_level,final_score,name,station_name,station_line,
                out_of_city,renter_age,car_time_start,car_time_end,make,module,
                keyless,year,engine_cap,city_code,cover_photo,street,price_daily,
                price_hourly,price_weekly,region,licence_plate_no,can_pay_before_start,
                can_send_distance,
                (
                    6378.138*2*asin(sqrt(pow(sin( ({latitude}*pi()/180-latitude*pi()/180)/2),2)+
                    cos({latitude}*pi()/180)*cos(latitude*pi()/180)*
                    pow(sin( ({longitude}*pi()/180-longitude*pi()/180)/2),2)))
                ) as distance
                FROM `sphinxse`
                WHERE `query`="filter=city_code,{city_code};limit=10000;maxmatches=10000;"
            ) se
            ORDER BY rank_score
            '''.format(city_code=city_code, latitude=lat,
                       longitude=lng, rank_rule=rank_rule)
            time_begin = time.time()
            rows = self.db.exec_sql(sql)
            if isExp:
                sql = '''select
                car_id
                from cr_exp_cars c
                where c.city_code='{}'
                '''.format(city_code)
                expCarids = set()
                for row in self.db.exec_sql(sql, resultFormat='tuple'):
                    expCarids.add(row[0])
                expRows = []
                for row in rows:
                    if row['id'] in expCarids:
                        expRows.append(row)
                rows = expRows
            time_delta = round((time.time() - time_begin)*1000,2)
            xc = Xcrypt()
            idx = 0
            for row in rows:
                idx += 1
                if idx > limit: break
                car = {}
                car['rank'] = idx
                car['id'] = row['id']
                car['xid'] = xc.encode(row['id'])
                car['licence_plate_no'] = row['licence_plate_no']
                car['name'] = row['name']
                car['distance'] = '%.3f' % row['distance']
                car['final_score'] = '%.2f' % row['final_score']
                car['rank_score'] = '%.2f' % (- row['rank_score'])
                car['recommend_level'] = row['recommend_level']
                car['can_send'] = row['can_send']
                car['price_daily'] = row['price_daily']
                car['longitude'] = row['longitude']
                car['latitude'] = row['latitude']
                car_list.append(car)
        self.render("metrics.html", latitude=lat, longitude=lng,
                    city_code=city_code, car_list=car_list,
                    remote_ip=self.request.remote_ip,
                    query_time=time_delta)
