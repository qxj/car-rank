#!/usr/bin/env bash
#
# Copyright (C) 2016 Julian Qian
#
# @file      ranksvr.sh
# @author    Julian Qian <junist@gmail.com>
# @created   2016-06-03 11:15:37
#

cd $(dirname $0)

ACTION=$1

start()
{
    ./ranksvr -flagfile ranksvr.conf
}

stop()
{
    pkill ranksvr
}

supervisor()
{
    pgrep ranksvr &> /dev/null
    if [[ $? -ne 0 ]]; then
        ds=$(date)
        echo "[$ds] ranksvr is down"
        start
    fi
}

deploy()
{
    latest=(ls -rt ranksvr.20* | tail -1)
    ln -sf $latest ranksvr
}

case "$ACTION" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        stop && start
        ;;
    supervisor)
        supervisor
        ;;
    deploy)
        deploy
        ;;
esac
