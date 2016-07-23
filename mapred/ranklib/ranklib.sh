#!/usr/bin/env bash
#
# Copyright (C) 2016 Julian Qian
#
# @file      ranklib.sh
# @author    Julian Qian <junist@gmail.com>
# @created   2016-07-20 12:47:07
#

ACTION=$1
INPUT=$2

if [[ -z $INPUT ]]; then
    INPUT=corpus_rl.txt
fi

METRIC=NDCG@90
RANKER=6
TREE=500
FEATS=feats.no
MODEL=lm_$(date +%m%d).xml

echo "Action: $ACTION, INPUT: $INPUT"

awk '{if(FILENAME=="feats.txt")a[$1]=NR;else b[$1]=1}END{for(k in b)print a[k]}' feats.txt feats.sel > $FEATS

train()
{
    java -jar RankLib-2.6.jar -ranker $RANKER -tree $TREE -feature $FEATS -metric2t $METRIC -train $INPUT -save $MODEL
}

test()
{
    java -jar RankLib-2.6.jar -load $MODEL -feature $FEATS -metric2T $METRIC -test $INPUT
}

rank()
{
    java -jar RankLib-2.6.jar -load $MODEL -feature $FEATS -metric2T $METRIC -rank $INPUT -score score.txt
}

case $ACTION in
    train)
        train
    ;;
    test)
        test
    ;;
    rank)
        rank
    ;;
esac
