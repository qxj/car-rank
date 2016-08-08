-- -*- sql -*-

CREATE EXTERNAL TABLE `rank.metrics`(
  `qid` string,
  `label` string,
  `ap` float,
  `ndcg` float,
  `city_code` string,
  `algo` string,
  `visit_time` string,
  `n_impress` int,
  `n_click` int,
  `n_precheck` int,
  `n_order` int,
  `ctr` float,
  `cvr` float,
  `cvr1` float,
  `cvr2` float
  )
PARTITIONED BY (`ds` string)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY '\t'
STORED AS TEXTFILE
LOCATION 'hdfs://Tyrael/user/work/rank/metrics';
