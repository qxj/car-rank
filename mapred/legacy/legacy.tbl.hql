-- -*- mode: sql -*-

CREATE TABLE rank.legacy (
        qid STRING,
        ndcg1 FLOAT,
        ndcg2 FLOAT,
        better INT,
        city_code STRING,
        has_date INT,
        algo STRING
        )
    PARTITIONED BY (ds STRING)
    ROW FORMAT DELIMITED
    FIELDS TERMINATED BY '\t'
    LINES TERMINATED BY '\n'
    STORED AS TEXTFILE;
