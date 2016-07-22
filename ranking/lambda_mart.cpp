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
DEFINE_int32(lambda_mart_ahead, 45,
             "Only rank ahead cars by lambda mart");

namespace ranking
{

LambdaMart::LambdaMart() :
    Ranker(), ensemble_(FLAGS_lambda_mart_model)
{}

void
LambdaMart::ranking(RankList& cars)
{
  namespace fi = ::feat_idx;

  if (FLAGS_lambda_mart_ahead > 0) {

    std::sort(cars.begin(), cars.end(),
              [](const DataPoint& a, const DataPoint& b) {
                return a.get(fi::DISTANCE) < b.get(fi::DISTANCE);
              });

    size_t ahead_num = FLAGS_lambda_mart_ahead;
    if (ahead_num > cars.size()) {
      ahead_num = cars.size();
    }
    float minScore = std::numeric_limits<float>::max();
    for (size_t i=0; i<ahead_num; i++) {
      auto& car = cars[i];
      car.score = ensemble_.eval(car);
      VLOG(100) << car.to_string();
      if (car.score < minScore) {
        minScore = car.score;
      }
    }
    for (size_t i=ahead_num; i<cars.size(); i++) {
      auto& car = cars[i];
      car.score = --minScore;
    }
  } else {
    for (auto& car: cars) {
      car.score = ensemble_.eval(car);
    }
  }
}

}
