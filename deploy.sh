#!/usr/bin/env bash
#
# Copyright (C) 2016 Julian Qian
#
# @file      deploy.sh
# @author    Julian Qian <junist@gmail.com>
# @created   2016-06-17 11:00:42
#

cd $(dirname $0)

sync_relay()
{
    from=$1
    to=$2
    rsync -avz -e "ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null" --progress $from qianxiaojun@121.42.29.135:rank/$to
}

sync_log01()
{
    from=$1
    to=$2
    rsync -avz -e "ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null" --progress $from work@10.161.59.223:rank/$to
}

sync_op()
{
    from=$1
    to=$2
    rsync -avz -e "ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null" --progress $from work@121.42.56.224:jqian/rank/$to
}

sync_se()
{
    from=$1
    to=$2
    for host in pp-se00 pp-se01 pp-se02; do
        rsync -avz -e "ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null" --progress $from work@${host}:rank/$to
    done
}

ssh_se()
{
    cmd=$1
    for host in pp-se00 pp-se01 pp-se02; do
        ssh $host "$cmd"
    done
}

today=$(date +%F)

case $1 in
    relay)
        ./mapred/mk_mod.sh
        sync_relay deploy.sh ""
        sync_relay mapred/ mapred
        sync_relay hive/ hive
        ;;
    log01)
        sync_log01 "mapred/*" ""
        sync_log01 hive/query_log/ hive
        ;;
    op)
        sync_op build/bin/ranksvr ranksvr.$today
        sync_op contrib/ranksvr.sh ""
        ;;
    se)
        sync_se ranksvr.$today ""
        ssh_se "cd ~/rank && ./ranksvr.sh deploy"
        # ssh_se "cd ~/rank && ./ranksvr.sh restart"
        ;;
    *)
        echo "invalid arguments"
        ;;
esac
