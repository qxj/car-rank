-- -*- mode: sql -*-

CREATE TABLE rank.legacy (
        qid STRING,
        dcg1 FLOAT,
        dcg2 FLOAT,
        better INT
        )
    PARTITIONED BY (ds STRING)
    ROW FORMAT DELIMITED
    FIELDS TERMINATED BY '\t'
    LINES TERMINATED BY '\n'
    STORED AS TEXTFILE;
