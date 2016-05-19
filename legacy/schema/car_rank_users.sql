CREATE TABLE `car_rank_users` (
`user_id` int(11) NOT NULL,
`update_time` timestamp NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
`collected_cars` text COMMENT '收藏过的车辆id，逗号分隔',
`ordered_cars` text COMMENT '下单过的车辆id，逗号分隔',
`prefer_price` text COMMENT '偏好价格区间，逗号分隔',
`prefer_models` text COMMENT '偏好车型id，逗号分隔',
PRIMARY KEY (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
