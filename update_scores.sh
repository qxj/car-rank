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

update() {
    # update run every 5 mins
    log "calculate car scores ..."
    (
        flock -xn 200 || die "Another instance is running.."
        ./car_score.py prepare --checkpoint checkpoint.prepare
        ./car_score.py run --checkpoint checkpoint.run
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
        ./car_score.py prepare --throttling 500 --before $before  --checkpoint checkpoint.prepare
        ./car_score.py run --throttling 500 --before $before  --checkpoint checkpoint.run
    ) 200>/tmp/update_scores.lck
}

calc_scores() {
    before=$(echo 60*24*30*12 | bc -l) # before one year
    (
        flock -xn 200 || die "Another instance is running.."
        ./car_score.py run --before $before --checkpoint checkpoint.run
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
