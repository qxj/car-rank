// -*- mode: c++ -*-
//
// Copyright (C) 2016 Julian Qian
//
// @file      legacy.cpp
// @author    Julian Qian <junist@gmail.com>
// @created   2016-04-25 07:33:39
//

#include <algorithm>

#include "legacy.hpp"

using namespace ranking;

Legacy::Legacy()
    : algo_(), db_()
{
  db_.fetch_algos(algo_);
}

void
Legacy::ranking(ranking::JsonRequest & req, ranking::JsonReply & rep)
{
  db_.query_scores(req);
  JsonRequest::CarsType& cars = req.cars;
  // const auto& weights = algo_.get_weights(req.algo);
  float w_quality    = algo_.get_weight(req.algo, "quality");
  float w_preference = algo_.get_weight(req.algo, "preference");
  float w_distance1  = algo_.get_weight(req.algo, "distance1");
  float w_distance2  = algo_.get_weight(req.algo, "distance2");
  float w_distance3  = algo_.get_weight(req.algo, "distance3");

  std::sort(cars.begin(), cars.end(),
            [](const CarInfo& a, const CarInfo& b) {
              // linear function
              float sa, sb;
              float d1, d2, d3;
              std::tie(d1, d2, d3) = a.trans_distance();

              return ;
            });
  rep.from_request(req);
}
