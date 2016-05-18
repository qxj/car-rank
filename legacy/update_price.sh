#!/bin/bash

TEST_CMD=''
if [[ -n $IS_TEST_ENV ]]; then
    TEST_CMD=' --test '
    echo "[1;31m====NOTE: WE ARE IN A TEST ENVIRONMENT====[0m"
fi

flock -xn /tmp/update_price.lck -c ./rank_price.py $TEST_CMD
