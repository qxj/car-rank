-- -*- mode: sql -*-

CREATE EXTERNAL TABLE rank.corpus (
        qid STRING,
        idx INT,
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
        station INT,
        confirm_rate INT,
        collect_count INT,
        sales_label INT,
        is_collect TINYINT,
        lat DOUBLE,
        lng DOUBLE,
        proportion FLOAT,
        car_score FLOAT
        )
    PARTITIONED BY (ds STRING)
    ROW FORMAT DELIMITED
    FIELDS TERMINATED BY '\t'
    LINES TERMINATED BY '\n'
    STORED AS TEXTFILE;
