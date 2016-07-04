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

namespace
{
class LegacyScore
{
 public:
  explicit LegacyScore(const LegacyAlgo::Weights& ws)
  {
    w_quality    = ws.get_weight("quality");
    w_distance1  = ws.get_weight("distance1");
    w_distance2  = ws.get_weight("distance2");
    w_distance3  = ws.get_weight("distance3");
    w_distance4  = ws.get_weight("distance4");

    w_preference = ws.get_weight("preference");
    w_collected  = ws.get_weight("collected");
    w_ordered    = ws.get_weight("ordered");
    w_model      = ws.get_weight("prefer_model");
    w_price      = ws.get_weight("prefer_price");
  }

  float score(const CarInfo& ci)
  {
    float d1, d2, d3, d4;
    std::tie(d1, d2, d3, d4) = ci.trans_distance();

    float s;

    s = w_quality * ci.quality + w_distance1 * d1 + w_distance2 * d2 + w_distance3 * d3 + \
        w_distance4 * d4 + \
        w_preference * (w_collected * ci.is_collected + w_ordered * ci.is_ordered + \
                w_model * ci.is_model + w_price * ci.is_price);
    return s;
  }
 private:
  float w_quality   ;
  float w_distance1 ;
  float w_distance2 ;
  float w_distance3 ;
  float w_distance4 ;
  float w_preference;
  float w_collected ;
  float w_ordered   ;
  float w_model     ;
  float w_price     ;
};
}

Legacy::Legacy()
    : algo_(), db_()
{
  // TODO fetch algos from db every some interval minutes
  db_.fetch_algos(algo_);
}

void
Legacy::ranking(ranking::JsonRequest & req, ranking::JsonReply & rep)
{
  db_.fetch_scores(req);
  JsonRequest::CarsType& cars = req.cars;

  const auto& weights = algo_.get_weights(req.algo);

  LegacyScore ls(weights);

  std::for_each(cars.begin(), cars.end(),
                [this, &ls](CarInfo& ci) {
                  ci.score = ls.score(ci);
                });

  std::sort(cars.begin(), cars.end(),
            [this, &ls](const CarInfo& a, const CarInfo& b) {
              return a.score > b.score;
            });
  rep.from_request(req);

  if (req.debug) {
    std::for_each(cars.begin(), cars.end(),
                  [this, &rep](const CarInfo& ci) {
                    rep.scores.push_back(ci.score);
                  });
  }
}
