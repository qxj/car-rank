-- -*- mode: sql -*-

CREATE EXTERNAL TABLE rank.query_log (
        query_id STRING,
        pos INT,
        page INT,
        label STRING,
        city_code STRING,
        user_id INT,
        car_id INT,
        `order_id` INT,
        distance FLOAT,
        algo STRING,
        visit_time STRING,
        has_date TINYINT,
        price INT,
        review FLOAT,
        review_cnt INT,
        auto_accept TINYINT,
        quick_accept TINYINT,
        is_recommend TINYINT,
        station STRING,
        confirm_rate INT,
        collect_cnt INT,
        sales_label STRING
        )
    PARTITIONED BY (ds STRING)
    ROW FORMAT DELIMITED
    FIELDS TERMINATED BY '\t'
    LINES TERMINATED BY '\n'
    STORED AS TEXTFILE;