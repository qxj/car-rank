-- -*- mode: sql -*-

ADD JAR /home/work/udf.jar;
-- CREATE FUNCTION ppzc_decode AS 'udf.PpzcDecode';


-- NOTE: this hql will fail when process db.php_svr_log before 20151225, because
-- distance is missing.

-- NOTE: this hql is expired after 20160616, because add the search1 field to instead of
-- the original search.

SET partpath="/user/work/rank/query_log/ds=${hiveconf:datestr}";

-- INSERT OVERWRITE TABLE rank.query_log
INSERT OVERWRITE DIRECTORY ${hiveconf:partpath}
    ROW FORMAT DELIMITED
    FIELDS TERMINATED BY '\t'
    LINES TERMINATED BY '\n'
    STORED AS TEXTFILE
SELECT
DISTINCT
t_exp.query_id,
t_exp.pos,
t_exp.page,
CASE WHEN t_order.qcid IS NOT NULL THEN 'order'
    WHEN t_precheck.qcid IS NOT NULL THEN 'precheck'
    WHEN t_click.qcid IS NOT NULL THEN 'click'
    ELSE 'impress' END AS label,
t_exp.city_code,
t_exp.user_id,
t_exp.car_id,
t_order.order_id,
t_dis.distance,
t_exp.algo,
t_exp.visit_time,
t_exp.has_date
FROM
(
SELECT
expo_car_id car_id,
user_id,
city_code,
params['page'] page,
IF(params['date_begin'] IS NULL,0,1) has_date,
pos,
IF(experiment IS NOT NULL, experiment['rank_algo'], NULL) algo,
visit_time,
CONCAT(user_id, '_', params['query_id']) query_id,
CONCAT(user_id, '_', params['query_id'], '_', params['page'], '_', pos) pos_id,
CONCAT(user_id, '_', params['query_id'], '_', expo_car_id) qcid,
ds
FROM
db.php_svr_log LATERAL VIEW POSEXPLODE(search.result) t AS pos, expo_car_id
WHERE ds=${hiveconf:datestr}
AND uri RLIKE '/vehicle\\.search'
AND search IS NOT NULL
AND user_id IS NOT NULL
AND (params['query_id'] IS NOT NULL AND params['query_id'] != "null")
) t_exp

JOIN
(
SELECT
distance,
CONCAT(user_id, '_', params['query_id'], '_', params['page'], '_', pos) pos_id
FROM
db.php_svr_log LATERAL VIEW POSEXPLODE(search.distance) t AS pos, distance
WHERE ds=${hiveconf:datestr}
AND uri RLIKE '/vehicle\\.search'
AND search IS NOT NULL
AND user_id IS NOT NULL
AND (params['query_id'] IS NOT NULL AND params['query_id'] != "null")
) t_dis ON t_exp.pos_id=t_dis.pos_id

LEFT JOIN
(
SELECT
CONCAT(user_id, '_', params['query_id'], '_', car_id) qcid
FROM
db.php_svr_log
WHERE ds=${hiveconf:datestr}
AND uri RLIKE '/vehicle\\.info'
AND (params['query_id'] IS NOT NULL AND params['query_id'] != "null")
AND car_id IS NOT NULL
) t_click ON t_click.qcid=t_exp.qcid

LEFT JOIN
(
SELECT
    CONCAT(user_id, '_', params['query_id'], '_',
        IF(car_id IS NOT NULL, car_id, ppzc_decode(params['car_id']))) qcid
FROM db.php_svr_log
WHERE ds=${hiveconf:datestr}
AND (uri RLIKE '/order\\.precheck' OR uri RLIKE '/order\\.submit_precheck')
AND (params['query_id'] IS NOT NULL AND params['query_id'] != "null")
AND (params['car_id'] IS NOT NULL OR car_id IS NOT NULL)
) t_precheck ON t_precheck.qcid=t_exp.qcid

LEFT JOIN
(
SELECT
CONCAT(user_id, '_', params['query_id'], '_', car_id) qcid,
order_id
FROM db.php_svr_log
WHERE ds=${hiveconf:datestr}
AND (uri RLIKE '/order\\.new' OR uri RLIKE '/order\\.create')
AND (params['query_id'] IS NOT NULL AND params['query_id'] != "null")
AND car_id IS NOT NULL
) t_order ON t_order.qcid=t_exp.qcid;


ALTER TABLE rank.query_log ADD IF NOT EXISTS PARTITION(ds=${hiveconf:datestr})
LOCATION ${hiveconf:partpath};
