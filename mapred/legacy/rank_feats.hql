-- -*- mode: sql -*-

DROP TABLE IF EXISTS temp.rank_feats;
CREATE TABLE temp.rank_feats
ROW FORMAT DELIMITED
FIELDS TERMINATED BY '\t'
LINES TERMINATED BY '\n'
STORED AS TEXTFILE
AS
SELECT * FROM default.car_rank_feats
WHERE ds=${hiveconf:datestr}
