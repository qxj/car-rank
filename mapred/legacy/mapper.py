#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; -*-
#
# Copyright (C) 2016 Julian Qian
#
# @file      mapper.py
# @author    Julian Qian <junist@gmail.com>
# @created   2016-06-13 16:18:23
#

from __future__ import division
import datetime
import sys

import zipimport
imp = zipimport.zipimporter('utils.mod')
utils = imp.load_module('utils')
from utils import table


def calc_score(row):
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
    # send car
    scores['w_send'] = 0
    if row['owner_send'] and row['owner_send_desc_len'] > 15:
        scores['w_send'] = 5
    if row['owner_send_has_tags']:
        scores['w_send'] += 10
    if row['owner_send_distance'] >= 5:
        scores['w_send'] += 5
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
    # for k, v in scores.items():
    #     rows[k] = round(v, 2)
    rows['quality'] = round(car_score, 2)
    rows['car_id'] = row['car_id']
    return rows


def discrete_distance(distance):
    d1, d2, d3 = 0, 0, 0
    if distance < 2:
        d1 = 1
    elif distance < 5:
        d2 = 1
    elif distance < 20:
        d3 = 1 - distance / 20
    return d1, d2, d3


def main():
    td = table.TableMeta('legacy.desc')
    for line in sys.stdin:
        cols = line.strip().split('\t')
        data = td.fields(cols)

        qid = data['qid']
        idx = data['idx']
        label = data['label']

        rets = calc_score(data)
        quality = rets['quality']
        distance = data['distance']
        d1, d2, d3 = discrete_distance(distance)
        score = quality * 1 + d1 * 60 + d2 * 30 + d3 * 10
        print '%s:%.10d\t%s\t%f' % (qid, idx, label, score)

if __name__ == "__main__":
    main()
