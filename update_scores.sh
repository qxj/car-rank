#!/bin/bash

cd $(dirname $0) || exit


log() {
    dt=$(date +%c)
    echo "[$dt] $1"
}

update() {
    # update run every 5 mins
    log "calculate car scores ..."
    # (
    #     flock -xn 200
    #     ./car_score.py prepare
    #     ./car_score.py run
    # ) 200>/tmp/update_scores.lck
    flock -xn /tmp/update_scores.lck -c "./car_score.py prepare --checkpoint checkpoint.prepare && ./car_score.py run --checkpoint checkpoint.run"
}

update_all() {
    days=$1
    if [[ -z $days ]]; then
        days=365
    fi
    before=$(echo 60*24*$days | bc -l) # before one year
    flock -xn /tmp/update_scores.lck -c "./car_score.py prepare --throttling 500 --before $before  --checkpoint checkpoint.prepare && ./car_score.py run --throttling 500 --before $before  --checkpoint checkpoint.run"
    if [[ $? -ne 0 ]]; then
        log "Another instance is running.."
    fi
}

calc_scores() {
    before=$(echo 60*24*30*12 | bc -l) # before one year
    flock -xn /tmp/update_scores.lck -c "./car_score.py run --before $before --checkpoint checkpoint.run"
    if [[ $? -ne 0 ]]; then
        log "Another instance is running.."
    fi
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
