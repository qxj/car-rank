-- -*- mode: sql -*-


INSERT OVERWRITE TABLE rank.query_detail
PARTITION (ds=${hiveconf:datestr})
SELECT DISTINCT
    CONCAT(user_id, '_', params['query_id']) query_id,
    IF(experiment IS NULL, NULL, experiment['rank_algo']) algo,
    user_id,
    city_code,
    city,
    latitude user_lat,
    longitude user_lng,
    params['date_begin'] date_begin,
    params['date_end'] date_end,
    params['reserve_price'] reserve_price,
    params['distance'] distance,
    params['make'] make,
    params['module'] `module`,
    params['lat'] lat,
    params['lng'] lng,
    params['transmission'] transmission,
    params['engine_cap'] engine_cap,
    params['seat'] seat,
    params['gps'] gps,
    params['audio'] audio,
    params['class'] `class`,
    params['year'] `year`,
    params['station'] station,
    params['duration'] duration,
    params['beauty'] beauty,
    params['gay'] guy,
    params['sort'] sort,
    params['fuzzy_tm_se'] fuzzy_tm_se,
    params['send_car'] send_car,
    params['pp_brand_id'] pp_brand_id,
    params['pp_genre_id'] pp_genre_id,
    params['labels'] labels,
    params['sale_labels'] sales_labels
FROM
    php_svr_log
WHERE ds=${hiveconf:datestr}
    AND uri RLIKE '/vehicle\\.search'
    AND params IS NOT NULL
    AND user_id IS NOT NULL;
