#!/usr/bin/env bash
#
# Copyright (C) 2016 Julian Qian
#
# @file      mk_mod.sh
# @author    Julian Qian <junist@gmail.com>
# @created   2016-06-17 18:33:08
#

cd $(dirname $0)

zip -r utils.zip utils
mv utils.zip utils.mod
