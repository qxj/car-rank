-- -*- mode: sql -*-

DROP TABLE IF EXISTS temp.legacy;

CREATE TABLE temp.legacy
ROW FORMAT DELIMITED
FIELDS TERMINATED BY '\t'
LINES TERMINATED BY '\n'
STORED AS TEXTFILE
AS
SELECT
c.qid,
c.idx,
c.label,
c.city_code,
c.user_id,
c.car_id,
c.`order_id`,
c.distance,
c.algo,
c.visit_time,
c.has_date,
c.price,
c.review,
c.review_cnt review_cnt1,
c.auto_accept auto_accept1,
c.quick_accept quick_accept1,
c.is_recommend,
c.station station1,
c.confirm_rate,
c.sales_label,
c.is_collect,
c.lat,
c.lng,
c.proportion proportion1,
c.car_score,
d.date_begin qs_date_begin,
d.date_end qs_date_end,
d.reserve_price qs_reserve_price,
d.make qs_make,
d.module qs_module,
d.transmission qs_transmission,
f.suggest_price,
f.proportion,
f.owner_send,
f.owner_send_desc_len,
f.owner_send_distance,
f.owner_send_has_tags,
f.price_tuning,
f.auto_accept,
f.quick_accept,
f.recent_rejected,
f.recent_accepted,
f.recent_paid,
f.recent_paid1,
f.recent_paid2,
f.recent_completed,
f.recent_completed1,
f.recent_completed2,
f.review_owner,
f.review_car,
f.review_cnt,
f.collect_cnt,
f.recommend_level,
f.pic_num,
f.desc_len,
f.station,
f.recent_cancelled_owner,
f.recent_paid_cancelled_owner,
f.recent_cancelled_renter,
f.verified_time,
f.available_days,
f.rented_days,
f.manual_weight

FROM rank.corpus c
    JOIN rank.query_detail d
    ON c.qid=d.qid AND d.ds=${hiveconf:datestr} AND c.ds=${hiveconf:datestr}
    LEFT JOIN default.car_rank_feats f
    ON c.car_id=f.car_id AND f.ds=${hiveconf:datestr} AND c.ds=${hiveconf:datestr}
WHERE c.ds=${hiveconf:datestr} ;
