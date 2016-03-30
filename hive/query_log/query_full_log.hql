-- -*- mode: sql -*-

-- CTR base features
-- 1. scene
-- 2. car
-- 3. user
-- 4. distance

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

FROM_UNIXTIME(UNIX_TIMESTAMP(lt.ds,'yyyyMMdd'), 'u') AS day_of_week,

p.price,
p.suggest_price,
p.owner_proportion,

ROUND((UNIX_TIMESTAMP(lt.ds,'yyyyMMdd') - c.appointed_time/1000)/86400, 1) AS appointed_days,
ROUND((UNIX_TIMESTAMP(lt.ds,'yyyyMMdd') - c.icarbox_time/1000)/86400, 1) AS icarbox_days,
ROUND((UNIX_TIMESTAMP(lt.ds,'yyyyMMdd') - c.verified_time/1000)/86400, 1) AS verified_days,
ROUND((UNIX_TIMESTAMP(lt.ds,'yyyyMMdd') - c.listed_on/1000)/86400, 1) AS listed_days,
c.avg_reply_time,
c.checked,
CASE c.city_code
    WHEN '110100' THEN 1
    WHEN '310100' THEN 1
    WHEN '440100' THEN 1
    WHEN '440300' THEN 1
    WHEN '210200' THEN 2
    WHEN '320100' THEN 2
    WHEN '320500' THEN 2
    WHEN '330100' THEN 2
    WHEN '340100' THEN 2
    WHEN '420100' THEN 2
    WHEN '430100' THEN 2
    WHEN '440600' THEN 2
    WHEN '441900' THEN 2
    WHEN '450100' THEN 2
    WHEN '460100' THEN 2
    WHEN '460200' THEN 2
    WHEN '510100' THEN 2
    WHEN '610100' THEN 2
    ELSE 0 END car_city,
IF(c.confirmed_rate='-',0,confirmed_rate) confirmed_rate,
IF(c.confirmed_rate_app IS NULL OR c.confirmed_rate_app<0,
    0,c.confirmed_rate_app) confirmed_rate_app,
CASE c.engine_cap
    WHEN 'Below 1,600cc' THEN 1
    WHEN '1,600cc to 2,000cc' THEN 2
    WHEN '2,001cc to 2,400cc' THEN 3
    WHEN 'Above 2,400cc' THEN 4
    ELSE 0 END engine_cap,
LENGTH(REGEXP_REPLACE(c.freetime,'0','')) freetime_days,
IF(c.keyless=1,1,0) keyless,
c.make,
c.model,
c.name,
IF(c.manual_transmission='Yes',1,0) manual_transmission,
SUBSTR(lt.ds, 0, 4) - c.year AS car_age,
c.miles,
c.recover_rate,
c.review_cnt,
CASE c.seat
    WHEN '2' THEN 1
    WHEN '3' THEN 1
    WHEN '4' THEN 1
    WHEN '5' THEN 1
    WHEN '6' THEN 2
    WHEN '7' THEN 2
    WHEN '>7' THEN 2
    WHEN '8' THEN 2
    WHEN '9' THEN 2
    ELSE 0 END seat,
ROUND((UNIX_TIMESTAMP(lt.ds,'yyyyMMdd') - u.birthday/1000)/86400/365, 1) AS user_age,
ROUND((UNIX_TIMESTAMP(lt.ds,'yyyyMMdd') - u.license_pass_date/1000)/86400/365, 1) AS license_age,
ROUND((UNIX_TIMESTAMP(lt.ds,'yyyyMMdd') - COALESCE(u.device_android, u.device_ios) / 1000)/86400, 1) AS device_days,
CASE u.device_kind WHEN 'APP' THEN 1
    WHEN 'H5' THEN 2
    WHEN 'PC' THEN 3
    ELSE 0 END device_kind,
IF(u.gender='F',0,1) gender,
CASE u.hp_city_code
    WHEN '110100' THEN 1
    WHEN '310100' THEN 1
    WHEN '440100' THEN 1
    WHEN '440300' THEN 1
    WHEN '210200' THEN 2
    WHEN '320100' THEN 2
    WHEN '320500' THEN 2
    WHEN '330100' THEN 2
    WHEN '340100' THEN 2
    WHEN '420100' THEN 2
    WHEN '430100' THEN 2
    WHEN '440600' THEN 2
    WHEN '441900' THEN 2
    WHEN '450100' THEN 2
    WHEN '460100' THEN 2
    WHEN '460200' THEN 2
    WHEN '510100' THEN 2
    WHEN '610100' THEN 2
    ELSE 0 END user_city,
CASE u.channel_kind
    WHEN '自然增长' THEN 1
    WHEN 'APP组' THEN 2
    WHEN 'BD组' THEN 3
    WHEN '展示组' THEN 4
    WHEN '精准组' THEN 5
    ELSE 0 END channel_kind

FROM
query_log lt
JOIN daily_price p ON p.ds=${hiveconf:datestr} AND p.car_id=lt.car_id
JOIN dm_car c ON c.ds=${hiveconf:datestr} AND c.car_id=lt.car_id
JOIN dm_user u ON u.ds=${hiveconf:datestr} AND u.user_id=lt.user_id
WHERE lt.ds=${hiveconf:datestr} AND lt.page<10;
