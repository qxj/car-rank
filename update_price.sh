#!/bin/bash

flock -xn /tmp/update_price.lck -c ./car_price.py
