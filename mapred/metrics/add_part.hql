ALTER TABLE rank.metrics ADD IF NOT EXISTS PARTITION(ds=${hiveconf:ds})
LOCATION '/user/work/rank/metrics/ds=${hiveconf:ds}';
