DROP TABLE IF EXISTS `car_rank_feats`;
CREATE TABLE `car_rank_feats` (
  `car_id` int(11) unsigned NOT NULL,
  `suggest_price` float DEFAULT 0 COMMENT '基准价',
  `proportion` float DEFAULT 0 COMMENT 'car_owner_price.proportion',
  `owner_send` tinyint(1) DEFAULT 0,
  `owner_send_desc_len` int(11) unsigned DEFAULT 0,
  `owner_send_has_tags` tinyint(1) DEFAULT 0,
  `auto_accept` tinyint(1) DEFAULT 0 COMMENT '是否开启自动接单',
  `recent_rejected` int(11) DEFAULT 0 COMMENT '最近10个单里的拒单数',
  `recent_accepted` int(11) DEFAULT 0 COMMENT '最近10个单里的接单数',
  `review_owner` float DEFAULT 0 COMMENT '3个月内最近10个订单对车主的评价分均分',
  `review_car` float DEFAULT 0 COMMENT '3个月内最近10个订单对车辆的评价分均分',
  `recommend_level` smallint(4) DEFAULT 0,
  `pic_num` int(11) unsigned DEFAULT 0,
  `desc_len` int(11) unsigned DEFAULT 0,
  `recent_cancelled_owner` int(11) DEFAULT 0 COMMENT '最近一个月内车主取消订单数',
  `recent_paid` int(11) DEFAULT 0 COMMENT '最近支付订单数',
  `recent_cancelled_renter` int(11) DEFAULT 0 COMMENT '1个月内最后10个支付后订单(不包含接收后订单)租客取消数',
  `manual_weight` int(11) DEFAULT 0,
  `update_time` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`car_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
