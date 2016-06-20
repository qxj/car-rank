-- -*- mode: sql -*-

ADD JAR /home/work/udf.jar;
-- CREATE FUNCTION ppzc_decode AS 'udf.PpzcDecode';


-- NOTE: this hql will fail when process php_svr_log before 20151225, because
-- distance is missing

INSERT OVERWRITE TABLE rank.query_log
PARTITION (ds=${hiveconf:datestr})
SELECT
DISTINCT
t_exp.qid,
t_exp.idx,
CASE WHEN t_order.qcid IS NOT NULL THEN 'order'
    WHEN t_precheck.qcid IS NOT NULL THEN 'precheck'
    WHEN t_click.qcid IS NOT NULL THEN 'click'
    ELSE 'impress' END AS label,
t_exp.pos,
t_exp.page,
t_exp.city_code,
t_exp.user_id,
t_exp.car_id,
t_order.order_id,
t_exp.distance,
t_exp.algo,
t_exp.visit_time,
t_exp.has_date,
t_exp.price,
t_exp.review,
t_exp.review_cnt,
t_exp.auto_accept,
t_exp.quick_accept,
t_exp.is_recommend,
t_exp.station,
t_exp.confirm_rate,
t_exp.collect_cnt,
t_exp.sales_label
FROM
    (
    SELECT
        city_code,
        user_id,
        car['id'] car_id,
        `order_id`,
        IF(params['date_begin'] IS NOT NULL,1,0) has_date,

        car['distance'] distance,
        car['price_daily'] price,
        car['review'] review,
        car['review_cnt'] review_cnt,
        IF(car['auto_accept']='YES',1,0) auto_accept,
        IF(car['quick_accept']='YES',1,0) quick_accept,
        car['is_recommend'] is_recommend,
        car['station_name'] station,
        car['confirmed_rate_app'] confirm_rate,

        car['collect_cnt'] collect_cnt,
        car['sales_label'] sales_label,

        params['page'] page,
        pos,
        ( (CAST(params['page'] AS INT) -1) * CAST(params['pagesize'] AS INT) + pos) idx,
        IF(experiment IS NOT NULL, experiment['rank_algo'], NULL) algo,
        visit_time,
        CONCAT(user_id, '_', params['query_id']) qid,
        CONCAT(user_id, '_', params['query_id'], '_', car['id']) qcid,
        ds
    FROM
        php_svr_log LATERAL VIEW POSEXPLODE(search1) t AS pos, car
    WHERE ds=${hiveconf:datestr}
        AND uri RLIKE '/vehicle\\.search'
        AND search1 IS NOT NULL
        AND user_id IS NOT NULL
        AND city_code IS NOT NULL
        AND (params['query_id'] IS NOT NULL AND params['query_id'] != "null")
        AND (params['page'] IS NOT NULL AND params['pagesize'] IS NOT NULL)
        AND (car['distance'] IS NOT NULL AND car['distance'] != "null")
        ) t_exp

LEFT JOIN
(
SELECT
CONCAT(user_id, '_', params['query_id'], '_', car_id) qcid
FROM
php_svr_log
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
FROM php_svr_log
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
FROM php_svr_log
WHERE ds=${hiveconf:datestr}
AND (uri RLIKE '/order\\.new' OR uri RLIKE '/order\\.create')
AND (params['query_id'] IS NOT NULL AND params['query_id'] != "null")
AND car_id IS NOT NULL
) t_order ON t_order.qcid=t_exp.qcid;


ALTER TABLE rank.query_log ADD IF NOT EXISTS PARTITION(ds=${hiveconf:datestr})
LOCATION '/user/work/rank/query_log/ds=${hiveconf:datestr}';
