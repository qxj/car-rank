CREATE TABLE `car_rank_weights` (
`weight_id` int(11) NOT NULL AUTO_INCREMENT,
`update_time` timestamp NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
`algo` varchar(255) DEFAULT '' COMMENT '算法名',
`name` varchar(255) DEFAULT '' COMMENT '特征名',
`weight` float DEFAULT '1' COMMENT '权重值',
`enabled` tinyint(1) DEFAULT '1' COMMENT '1: enabled',
PRIMARY KEY (`weight_id`),
KEY `algo` (`algo`),
KEY `enabled` (`enabled`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
