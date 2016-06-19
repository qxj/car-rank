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
c.user_id,
c.car_id,
c.`order_id`,
c.distance,
c.algo,
c.visit_time,
c.has_date,
c.price,
c.review,
c.review_cnt,
c.auto_accept,
c.quick_accept,
c.is_recommend,
c.station,
c.confirm_rate,
c.sales_label,
f.suggest_price,
f.proportion,
f.owner_send,
f.owner_send_desc_len,
f.owner_send_distance,
f.owner_send_has_tags,
f.price_tuning,
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
f.collect_cnt,
f.recommend_level,
f.pic_num,
f.desc_len,
f.recent_cancelled_owner,
f.recent_paid_cancelled_owner,
f.recent_cancelled_renter,
f.verified_time,
f.available_days,
f.rented_days,
f.manual_weight

FROM rank.corpus c LEFT JOIN default.car_rank_feats f
    ON c.car_id=f.car_id AND f.ds=${hiveconf:datestr} AND c.ds=${hiveconf:datestr}
WHERE c.ds=${hiveconf:datestr} ;
