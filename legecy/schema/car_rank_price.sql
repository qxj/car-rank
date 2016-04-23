DROP TABLE IF EXISTS `car_rank_price`;
CREATE TABLE `car_rank_price` (
  `car_id` int(11) NOT NULL,
  `price` float DEFAULT 0 COMMENT '当日出租价',
  `suggest_price` float DEFAULT 0 COMMENT '当日基准价',
  `base_price` float DEFAULT 0 COMMENT '基础指导价',
  `proportion` float DEFAULT 0 COMMENT '车主浮动系数',
  `update_time` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`car_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
