ALTER TABLE rank.legacy ADD IF NOT EXISTS PARTITION(ds=${hiveconf:ds})
LOCATION '/user/work/rank/legacy/ds=${hiveconf:ds}';
