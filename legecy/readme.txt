-*- markdown -*-

车辆质量分和相关排序因子的离线计算程序

## 部署方法

假设代码clone到 `/home/work/rank`，则在crontab里增加如下内容即可：

    */5 * * * * cd /home/work/rank && ./update_scores.sh update &>> update_scores.log
    4 2 * * * cd /home/work/rank && ./update_scores.sh all &>> update_scores.log
    0 1 * * * cd /home/work/rank && ./update_price.sh &>> update_price.log

参数说明如下：

- `update_scores.sh update` 增量计算
- `update_scores.sh all` 全量计算
- `update_price.sh` 同步车辆价格快照表

### 测试环境

对测试环境，可以定义一个环境变量 `IS_TEST_ENV`，然后类似这样执行脚本：

    IS_TEST_ENV=1 ./update_scores.sh update
