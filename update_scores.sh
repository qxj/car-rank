#!/bin/bash

interval=$1
if [[ -z $interval ]]; then
    interval=6
fi

# run every 5 mins, give one minute buffer time
dt=$(date +%c)
echo "[$dt] prepare features ..."
flock -xn /tmp/update_scores.lck -c "./car_score.py prepare --interval $interval"
echo "[$dt] calculate car scores ..."
flock -xn /tmp/update_scores.lck -c "./car_score.py run --interval $interval"
