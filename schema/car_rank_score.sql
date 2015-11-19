DROP TABLE IF EXISTS `car_rank_score`;
CREATE TABLE `car_rank_score` (
  `car_id` int(11) unsigned NOT NULL,
  `score` float DEFAULT 0 COMMENT '车辆质量分',
  `w_price` float DEFAULT 0,
  `w_send` float DEFAULT 0,
  `w_confirm` float DEFAULT 0,
  `w_review_owner` float DEFAULT 0,
  `w_review_car` float DEFAULT 0,
  `w_recommend` int(11) DEFAULT 0,
  `w_manual` int(11) DEFAULT 0,
  `update_time` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`car_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
