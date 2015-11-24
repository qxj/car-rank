DROP TABLE IF EXISTS `car_rank_score`;
CREATE TABLE `car_rank_score` (
  `car_id` int(11) unsigned NOT NULL,
  `score` float DEFAULT 0 COMMENT '车辆质量分',
  `w_price` float DEFAULT 0 COMMENT '价格分',
  `w_send` float DEFAULT 0 COMMENT '送车上门分',
  `w_accept` float DEFAULT 0 COMMENT '接单率分',
  `w_review_owner` float DEFAULT 0 COMMENT '车主评价分',
  `w_review_car` float DEFAULT 0 COMMENT '车辆评价分',
  `w_recommend` float DEFAULT 0 COMMENT '车辆推荐等级分',
  `w_punish` float DEFAULT 0 COMMENT '惩罚分',
  `w_manual` float DEFAULT 0 COMMENT '人工分',
  `update_time` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`car_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
