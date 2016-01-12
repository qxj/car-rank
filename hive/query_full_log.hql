-- -*- mode: sql -*-

INSERT OVERWRITE DIRECTORY "query_full_log/ds=${hiveconf:datestr}"

SELECT
lt.label,
lt.car_id,
lt.user_id,
lt.order_id,
lt.distance,
lt.page,
lt.pos,
lt.id,

p.price,
p.suggest_price,
p.owner_proportion,

(UNIX_TIMESTAMP(lt.ds,'yyyyMMdd') - c.appointed_time/1000)/86400 AS appointed_days,
(UNIX_TIMESTAMP(lt.ds,'yyyyMMdd') - c.icarbox_time/1000)/86400 AS icarbox_days,
(UNIX_TIMESTAMP(lt.ds,'yyyyMMdd') - c.verified_time/1000)/86400 AS verified_days,
(UNIX_TIMESTAMP(lt.ds,'yyyyMMdd') - c.listed_on/1000)/86400 AS listed_days,
c.avg_reply_time,
c.checked,
c.city_code,
c.confirmed_rate,
c.confirmed_rate_app,
c.engine_cap,
LENGTH(REGEXP_REPLACE(c.freetime,'0','')) freetime_days,
c.keyless,
c.make,
c.model,
c.name,
c.manual_transmission,
SUBSTR(lt.ds, 0, 4) - c.year AS car_age,
c.miles,
c.recover_rate,
c.review_cnt,
c.seat,
c.state,
c.region,

(UNIX_TIMESTAMP(lt.ds,'yyyyMMdd') - u.birthday/1000)/86400/365 AS user_age,
(UNIX_TIMESTAMP(lt.ds,'yyyyMMdd') - u.license_pass_date/1000)/86400/365 AS license_age,
(UNIX_TIMESTAMP(lt.ds,'yyyyMMdd') - COALESCE(u.device_android, u.device_ios) / 1000)/86400 AS device_days,
u.device_kind,
u.gender,
u.hp_city_code,
u.demerit_points,
u.channel_kind

FROM
query_log lt
JOIN daily_price p ON p.ds=${hiveconf:datestr} AND p.car_id=lt.car_id
JOIN dm_car c ON c.ds=${hiveconf:datestr} AND c.car_id=lt.car_id
JOIN dm_user u ON u.ds=${hiveconf:datestr} AND u.user_id=lt.user_id
WHERE lt.ds=${hiveconf:datestr};