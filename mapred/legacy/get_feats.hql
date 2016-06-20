-- -*- mode: sql -*-

set hive.cli.print.header=true;

SELECT
    *
FROM default.car_rank_feats
WHERE ds=${hiveconf:ds} AND car_id=${hiveconf:car_id};
