#!/bin/bash

cd $(dirname $0) || exit


log() {
    dt=$(date +%c)
    echo "[$dt] $1"
}

die() {
    log $1
    exit 1
}

TEST_CMD=''
if [[ -n $IS_TEST_ENV ]]; then
    TEST_CMD=' --test '
    echo "[1;31m====NOTE: WE ARE IN A TEST ENVIRONMENT====[0m"
fi

update() {
    # update run every 5 mins
    log "calculate car scores ..."
    (
        flock -xn 200 || die "Another instance is running.."
        ./rank_feats.py --checkpoint checkpoint.prepare $TEST_CMD
        ./rank_users.py --checkpoint checkpoint.users $TEST_CMD
        ./rank_score.py --checkpoint checkpoint.run $TEST_CMD
    ) 200>/tmp/update_scores.lck
}

update_all() {
    days=$1
    if [[ -z $days ]]; then
        days=365
    fi
    before=$(echo 60*24*$days | bc -l) # before one year
    (
        flock -xn 200 || die "Another instance is running.."
        ./rank_feats.py --throttling 500 --before $before  --checkpoint checkpoint.prepare $TEST_CMD
        ./rank_users.py --throttling 500 --before $before  --checkpoint checkpoint.users $TEST_CMD
        ./rank_score.py --throttling 500 --before $before  --checkpoint checkpoint.run $TEST_CMD
    ) 200>/tmp/update_scores.lck
}

calc_scores() {
    before=$(echo 60*24*30*12 | bc -l) # before one year
    (
        flock -xn 200 || die "Another instance is running.."
        ./rank_score.py --before $before --checkpoint checkpoint.run $TEST_CMD
    ) 200>/tmp/update_scores.lck
}

case "$1" in
    "update")
        update
        ;;
    "all")
        update_all $2
        ;;
    "calc")
        calc_scores
        ;;
    *)
        echo "Please specify an argument."
        ;;
esac
