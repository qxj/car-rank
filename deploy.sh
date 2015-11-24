#!/bin/bash
# @(#) deploy.sh  Time-stamp: <Julian Qian 2015-11-25 11:16:55>
# Copyright 2015 Julian Qian
# Author: Julian Qian <junist@gmail.com>
# Version: $Id: deploy.sh,v 0.1 2015-05-22 11:32:06 jqian Exp $
#

curl -u pptester:pptester http://jenkins.dzuche.com/view/PHP/job/data-rank/process/buildWithOpsParameters
if [[ $? -eq 0 ]]; then
    echo "Deployed OK."
else
    echo "Failed to deploy!"
fi
