-- -*- mode: sql -*-

ADD JAR /home/work/udf.jar;
-- CREATE FUNCTION ppzc_decode AS 'udf.PpzcDecode';


-- NOTE: this hql will fail when process php_svr_log before 20151225, because
-- distance is missing

INSERT OVERWRITE TABLE query_log
PARTITION (ds=${hiveconf:datestr})
SELECT
DISTINCT
t_exp.id,
CASE WHEN t_order.car_id IS NOT NULL THEN 9
    WHEN t_precheck.car_id IS NOT NULL THEN 2
    WHEN t_click.car_id IS NOT NULL THEN 1
    ELSE 0 END AS label,
t_exp.user_id,
t_exp.car_id,
t_order.order_id,
t_dis.distance,
t_exp.pos,
t_exp.page
FROM
(
SELECT
expo_car_id car_id,
user_id,
params['page'] page,
params['query_id'] quer_id,
ds,
pos,
CONCAT(log_id, '_', pos) id
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
CONCAT(log_id, '_', pos) id
FROM
php_svr_log LATERAL VIEW POSEXPLODE(search.distance) t AS pos, distance
WHERE ds=${hiveconf:datestr}
AND uri RLIKE '/vehicle\\.search'
AND search IS NOT NULL
AND user_id IS NOT NULL
) t_dis ON t_exp.id=t_dis.id
LEFT JOIN
(
SELECT
params['query_id'] query_id,
car_id
FROM
php_svr_log
WHERE ds=${hiveconf:datestr}
AND uri RLIKE '/vehicle\\.info'
AND params['query_id'] IS NOT NULL
AND car_id IS NOT NULL
) t_click ON t_click.query_id=t_exp.query_id
LEFT JOIN
(
SELECT
params['query_id'] query_id,
ppzc_decode(params['car_id']) car_id,
user_id
FROM php_svr_log
WHERE ds=${hiveconf:datestr}
AND uri RLIKE '/order\\.precheck'
AND params['car_id'] IS NOT NULL
) t_precheck ON t_precheck.query_id=t_exp.query_id
AND t_precheck.car_id=t_exp.car_id
AND t_precheck.user_id=t_exp.user_id
LEFT JOIN
(
SELECT
params['query_id'] query_id,
order_id,
user_id,
car_id
FROM php_svr_log
WHERE ds=${hiveconf:datestr}
AND uri RLIKE '/order\\.new'
) t_order ON t_order.query_id=t_click.query_id
AND t_order.car_id=t_exp.car_id
AND t_order.user_id=t_exp.user_id;


ALTER TABLE query_log ADD IF NOT EXISTS PARTITION(ds=${hiveconf:datestr})
LOCATION '/user/work/query_log/ds=${hiveconf:datestr}';
