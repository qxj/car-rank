-- -*- mode: sql -*-

DROP TABLE IF EXISTS temp.legacy;

CREATE TABLE temp.legacy
ROW FORMAT DELIMITED
FIELDS TERMINATED BY '\t'
LINES TERMINATED BY '\n'
STORED AS TEXTFILE
AS
SELECT
    c.*, f.*
FROM rank.corpus c LEFT JOIN default.car_rank_feats f
    ON c.car_id=f.car_id AND f.ds=${hiveconf:datestr} AND c.ds=${hiveconf:datestr}
WHERE c.ds=${hiveconf:datestr} ;
