-- -*- mode: sql -*-

DROP TABLE IF EXISTS temp.corpus_ranklib;

CREATE TABLE temp.corpus_rl
ROW FORMAT DELIMITED
FIELDS TERMINATED BY '\t'
LINES TERMINATED BY '\n'
STORED AS TEXTFILE
AS
SELECT
c.label,
c.qid,
c.car_id,
c.idx,
d.city_code,
IF(d.date_begin IS NOT NULL,1,0) has_date,
IF(d.reserve_price IS NOT NULL,SPLIT(d.reserve_price,',')[1],999) max_price,
c.price,
c.distance,
c.proportion,
c.review,
c.review_cnt,
c.auto_accept,
c.quick_accept,
IF(c.is_recommend IS NULL,0,1) is_recommend,
c.station,
c.confirm_rate,
c.collect_count,
c.is_collect
FROM rank.corpus c
JOIN rank.query_detail d
ON c.qid=d.qid
WHERE c.ds=${hiveconf:datestr} AND d.ds=${hiveconf:datestr}
