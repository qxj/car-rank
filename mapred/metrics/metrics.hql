CREATE EXTERNAL TABLE `metrics`(
  `qid` string,
  `label` string,
  `ap` float,
  `ndcg` float,
  `city_code` string,
  `algo` string,
  `visit_time` string
  )
PARTITIONED BY (`ds` string)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY '\t'
STORED AS TEXTFILE
LOCATION 'hdfs://Tyrael/user/work/rank/metrics';
