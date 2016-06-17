ALTER TABLE rank.corpus ADD IF NOT EXISTS PARTITION(ds=${hiveconf:ds})
LOCATION '/user/work/rank/corpus/ds=${hiveconf:ds}';