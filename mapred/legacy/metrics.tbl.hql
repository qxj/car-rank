-- -*- mode: sql -*-

CREATE TABLE temp.metrics (
        query_id STRING,
        dcg1 FLOAT,
        dcg2 FLOAT,
        better INT
        )
    ROW FORMAT DELIMITED
    FIELDS TERMINATED BY '\t'
    LINES TERMINATED BY '\n'
    STORED AS TEXTFILE;
