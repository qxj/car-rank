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
  db_.fetch_scores(req);
  JsonRequest::CarsType& cars = req.cars;

  const auto& weights = algo_.get_weights(req.algo);

  std::sort(cars.begin(), cars.end(),
            [this, &weights](const CarInfo& a, const CarInfo& b) {
              return score_func(a, weights) > score_func(b, weights);
            });
  rep.from_request(req);
}

float
Legacy::score_func(const CarInfo& ci, const LegacyAlgo::Weights& ws)
{
  float d1, d2, d3;
  std::tie(d1, d2, d3) = ci.trans_distance();

  float w_quality    = ws.get_weight("quality");
  float w_distance1  = ws.get_weight("distance1");
  float w_distance2  = ws.get_weight("distance2");
  float w_distance3  = ws.get_weight("distance3");

  float w_preference = ws.get_weight("preference");
  float w_collected  = ws.get_weight("collected");
  float w_ordered    = ws.get_weight("ordered");
  float w_model      = ws.get_weight("prefer_model");
  float w_price      = ws.get_weight("prefer_price");

  float s;

  s = w_quality * ci.quality + w_distance1 * d1 + w_distance2 * d2 + w_distance3 * d3 + \
      w_preference * (w_collected * ci.is_collected + w_ordered * ci.is_ordered + \
              w_model * ci.is_model + w_price * ci.is_price);
  return s;
}
