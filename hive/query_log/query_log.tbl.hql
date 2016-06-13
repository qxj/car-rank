-- -*- mode: sql -*-

CREATE EXTERNAL TABLE query_log (
        query_id STRING,
        label STRING,
        city_code STRING,
        user_id INT,
        car_id INT,
        `order_id` INT,
        distance FLOAT,
        pos INT,
        page INT,
        algo STRING,
        visit_time STRING,
        price INT,
        has_date TINYINT,
        review FLOAT,
        review_cnt INT,
        auto_accept TINYINT,
        quick_accept TINYINT,
        is_recommend TINYINT,
        station STRING,
        confirm_rate INT
        )
    PARTITIONED BY (ds STRING)
    ROW FORMAT DELIMITED
    FIELDS TERMINATED BY '\t'
    LINES TERMINATED BY '\n'
    STORED AS TEXTFILE;
