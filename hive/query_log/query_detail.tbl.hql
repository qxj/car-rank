
CREATE EXTERNAL TABLE rank.query_detail (
        qid STRING,
        algo STRING,
        user_id INT,
        `order_id` INT,
        car_id INT,
        visit_time STRING,
        city_code STRING,
        city STRING,
        user_lat DOUBLE,
        user_lng DOUBLE,
        date_begin STRING,
        date_end STRING,
        reserve_price STRING,
        distance FLOAT,
        make STRING,
        `module` STRING,
        lat DOUBLE,
        lng DOUBLE,
        transmission STRING,
        engine_cap INT,
        seat INT,
        gps TINYINT,
        audio TINYINT,
        `class` TINYINT,
        `year` INT,
        station TINYINT,
        duration TINYINT,
        beauty TINYINT,
        guy TINYINT,
        sort STRING,
        fuzzy_tm_se TINYINT,
        send_car TINYINT,
        pp_brand_id INT,
        pp_genre_id INT,
        labels STRING,
        sales_labels STRING
        )
    PARTITIONED BY (ds STRING)
    ROW FORMAT DELIMITED
    FIELDS TERMINATED BY '\t'
    LINES TERMINATED BY '\n'
    STORED AS TEXTFILE;
