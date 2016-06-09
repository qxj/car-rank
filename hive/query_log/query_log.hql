-- -*- mode: sql -*-

ADD JAR /home/work/udf.jar;
-- CREATE FUNCTION ppzc_decode AS 'udf.PpzcDecode';


-- NOTE: this hql will fail when process php_svr_log before 20151225, because
-- distance is missing

INSERT OVERWRITE TABLE query_log
PARTITION (ds=${hiveconf:datestr})
SELECT
DISTINCT
t_exp.query_id,
CASE WHEN t_order.qcid IS NOT NULL THEN 'order'
    WHEN t_precheck.qcid IS NOT NULL THEN 'precheck'
    WHEN t_click.qcid IS NOT NULL THEN 'click'
    ELSE 'impress' END AS label,
t_exp.city_code,
t_exp.user_id,
t_exp.car_id,
t_order.order_id,
t_dis.distance,
t_exp.pos,
t_exp.page,
t_exp.visit_time
FROM
(
SELECT
expo_car_id car_id,
user_id,
city_code,
params['page'] page,
pos,
visit_time,
CONCAT(user_id, '_', params['query_id']) query_id,
CONCAT(user_id, '_', params['query_id'], '_', params['page'], '_', pos) pos_id,
CONCAT(user_id, '_', params['query_id'], '_', expo_car_id) qcid,
ds
FROM
php_svr_log LATERAL VIEW POSEXPLODE(search.result) t AS pos, expo_car_id
WHERE ds=${hiveconf:datestr}
AND uri RLIKE '/vehicle\\.search'
AND search IS NOT NULL
AND user_id IS NOT NULL
AND params['query_id'] IS NOT NULL
) t_exp

JOIN
(
SELECT
distance,
CONCAT(user_id, '_', params['query_id'], '_', params['page'], '_', pos) pos_id
FROM
php_svr_log LATERAL VIEW POSEXPLODE(search.distance) t AS pos, distance
WHERE ds=${hiveconf:datestr}
AND uri RLIKE '/vehicle\\.search'
AND search IS NOT NULL
AND user_id IS NOT NULL
AND params['query_id'] IS NOT NULL
) t_dis ON t_exp.pos_id=t_dis.pos_id

LEFT JOIN
(
SELECT
CONCAT(user_id, '_', params['query_id'], '_', car_id) qcid
FROM
php_svr_log
WHERE ds=${hiveconf:datestr}
AND uri RLIKE '/vehicle\\.info'
AND params['query_id'] IS NOT NULL
AND car_id IS NOT NULL
) t_click ON t_click.qcid=t_exp.qcid

LEFT JOIN
(
SELECT
CONCAT(user_id, '_', params['query_id'], '_', ppzc_decode(params['car_id'])) qcid
FROM php_svr_log
WHERE ds=${hiveconf:datestr}
AND (uri RLIKE '/order\\.precheck' OR uri RLIKE '/order\\.submit_precheck')
AND params['query_id'] IS NOT NULL
AND params['car_id'] IS NOT NULL
) t_precheck ON t_precheck.qcid=t_exp.qcid

LEFT JOIN
(
SELECT
CONCAT(user_id, '_', params['query_id'], '_', car_id) qcid,
order_id
FROM php_svr_log
WHERE ds=${hiveconf:datestr}
AND (uri RLIKE '/order\\.new' OR uri RLIKE '/order\\.create')
AND params['query_id'] IS NOT NULL
AND car_id IS NOT NULL
) t_order ON t_order.qcid=t_exp.qcid;


ALTER TABLE query_log ADD IF NOT EXISTS PARTITION(ds=${hiveconf:datestr})
LOCATION '/user/work/query_log/ds=${hiveconf:datestr}';
