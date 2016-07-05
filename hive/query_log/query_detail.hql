-- -*- mode: sql -*-


INSERT OVERWRITE TABLE rank.query_detail
    PARTITION (ds=${hiveconf:datestr})
SELECT
    q.qid,
    t.pages,
    q.algo,
    CASE WHEN o.qid IS NOT NULL THEN 'order'
    WHEN p.qid IS NOT NULL THEN 'precheck'
    WHEN i.qid IS NOT NULL THEN 'click'
    ELSE 'impress' END label,
    q.user_id,
    o.`order_id`,
    o.car_id,
    t.visit_time,
    t.city_code,
    t.city,
    t.user_lat,
    t.user_lng,
    t.date_begin,
    t.date_end,
    t.reserve_price,
    t.distance,
    t.make,
    t.`module`,
    t.lat,
    t.lng,
    t.transmission,
    t.engine_cap,
    t.seat,
    t.gps,
    t.audio,
    t.`class`,
    t.`year`,
    t.station,
    t.duration,
    t.beauty,
    t.guy,
    t.sort,
    t.fuzzy_tm_se,
    t.send_car,
    t.pp_brand_id,
    t.pp_genre_id,
    t.labels,
    t.sales_labels
FROM
    (
    SELECT DISTINCT
        CONCAT(user_id, '_', params['query_id']) qid,
        IF(experiment IS NULL, NULL, experiment['rank_algo']) algo,
        user_id
    FROM
        db.php_svr_log
    WHERE ds=${hiveconf:datestr}
        AND uri='/vehicle.search'
        AND params IS NOT NULL
        AND user_id IS NOT NULL
        ) q
    JOIN
    (
    SELECT
        CONCAT(user_id, '_', params['query_id']) qid,
        COUNT(1) pages,
        MAX(city_code) city_code,
        MAX(latitude) user_lat,
        MAX(longitude) user_lng,
        MIN(city) city,
        MAX(params['lat']) lat,
        MAX(params['lng']) lng,
        MAX(params['date_begin']) date_begin,
        MAX(params['date_end']) date_end,
        MAX(params['reserve_price']) reserve_price,
        MAX(params['distance']) distance,
        MAX(params['make']) make,
        MAX(params['module']) `module`,
        MAX(params['transmission']) transmission,
        MAX(params['engine_cap']) engine_cap,
        MAX(params['seat']) seat,
        MAX(params['gps']) gps,
        MAX(params['audio']) audio,
        MAX(params['class']) `class`,
        MAX(params['year']) `year`,
        MAX(params['station']) station,
        MAX(params['duration']) duration,
        MAX(params['beauty']) beauty,
        MAX(params['gay']) guy,
        MAX(params['sort']) sort,
        MAX(params['fuzzy_tm_se']) fuzzy_tm_se,
        MAX(params['send_car']) send_car,
        MAX(params['pp_brand_id']) pp_brand_id,
        MAX(params['pp_genre_id']) pp_genre_id,
        MAX(params['labels']) labels,
        MAX(params['sale_labels']) sales_labels,
        MAX(params['query_id']) query_id,
        MIN(visit_time) visit_time
    FROM
        db.php_svr_log
    WHERE ds=${hiveconf:datestr}
        AND uri='/vehicle.search'
        AND params IS NOT NULL
        AND user_id IS NOT NULL
    GROUP BY CONCAT(user_id, '_', params['query_id'])
    ) t ON t.qid=q.qid
    LEFT JOIN
    (
    SELECT DISTINCT
        CONCAT(user_id, '_', params['query_id']) qid
    FROM
        db.php_svr_log
    WHERE ds=${hiveconf:datestr}
        AND uri='/vehicle.info'
        AND (params IS NOT NULL AND params['query_id'] IS NOT NULL)
        ) i on q.qid=i.qid
    LEFT JOIN
    (
    SELECT DISTINCT
        CONCAT(user_id, '_', params['query_id']) qid
    FROM
        db.php_svr_log
    WHERE ds=${hiveconf:datestr}
        AND (uri='/order.precheck' OR uri='/order.submit_precheck')
        AND (params IS NOT NULL AND params['query_id'] IS NOT NULL)
        ) p on q.qid=p.qid
    LEFT JOIN
    (
    SELECT DISTINCT
        CONCAT(user_id, '_', params['query_id']) qid,
        `order_id`,
        car_id
    FROM
        db.php_svr_log
    WHERE ds=${hiveconf:datestr}
        AND (uri='/order.create' OR uri='/order.new')
        AND (params IS NOT NULL AND params['query_id'] IS NOT NULL)
        ) o ON q.qid=o.qid
