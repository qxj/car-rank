CREATE TABLE `car_rank_legacy` (
`car_id` int(11) NOT NULL,
`update_time` timestamp NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
`quality` float DEFAULT '0' COMMENT 'car quality score',
`norm_quality` float DEFAULT '0' COMMENT 'normalized quality score',
`model` int(11) DEFAULT '0' COMMENT '车型id',
`price` float(10,2) DEFAULT '0.00' COMMENT '日租价',
PRIMARY KEY (`car_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
