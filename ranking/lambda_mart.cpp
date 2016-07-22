// -*- mode: c++ -*-
//
// Copyright (C) 2016 Julian Qian
//
// @file      lambda_mart.cpp
// @author    Julian Qian <junist@gmail.com>
// @created   2016-04-25 07:35:11
//

// LambdaMART

#include <algorithm>
#include <limits>

#include <gflags/gflags.h>
#include <glog/logging.h>

#include "data_point.hpp"
#include "feat_idx.hpp"

#include "lambda_mart.hpp"


DEFINE_string(lambda_mart_model, "/tmp/lambda_mart.xml",
              "LambdaMART model file");

namespace ranking
{

LambdaMart::LambdaMart() :
    Ranker(), ensemble_(FLAGS_lambda_mart_model)
{}

void
LambdaMart::ranking(RankItr begItr, RankItr endItr)
{
  namespace fi = ::feat_idx;

  for (auto itr=begItr; itr<endItr; itr++) {
    itr->score = ensemble_.eval(*itr);

    VLOG(100) << itr->to_string();
  }
}

}
