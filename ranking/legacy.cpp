// -*- mode: c++ -*-
//
// Copyright (C) 2016 Julian Qian
//
// @file      legacy.cpp
// @author    Julian Qian <junist@gmail.com>
// @created   2016-04-25 07:33:39
//

#include <algorithm>

#include <glog/logging.h>

#include "legacy.hpp"

namespace fi = ::feat_idx;

namespace
{
class LegacyScore
{
 public:
  explicit LegacyScore(const ranking::LegacyAlgo::Weights& ws)
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

  std::tuple<float, float, float, float> trans_distance(float distance)
  {
    float d1{0}, d2{0}, d3{0}, d4{0};
    if (distance < 2) {
      d1 = - distance / 2;
    } else if (distance < 5) {
      d2 = - distance / 2;
    } else if (distance < 12) {
      d3 = - distance;
    } else {
      d4 = - distance * 2;
    }
    return std::make_tuple(d1, d2, d3, d4);
  }

  float score(const ranking::DataPoint& dp)
  {
    float d1, d2, d3, d4;
    std::tie(d1, d2, d3, d4) = trans_distance(dp.get(fi::DISTANCE));

    float quality = dp.get(fi::QUALITY);
    float is_collect = dp.get(fi::IS_COLLECT);
    float is_ordered = dp.get(fi::IS_ORDERED);
    float is_model = dp.get(fi::IS_MODEL);
    float is_price = dp.get(fi::IS_PRICE);

    float s;

    s = w_quality * quality + w_distance1 * d1 + w_distance2 * d2 + \
        w_distance3 * d3 + w_distance4 * d4 + \
        w_preference * (w_collected * is_collect + w_ordered * is_ordered + \
                w_model * is_model + w_price * is_price);
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

namespace ranking
{

const LegacyAlgo::Weights&
LegacyAlgo::get_weights(const std::string& algo)
{
  const auto& itr = algos_.find(algo);
  if (itr == algos_.end()) {
    LOG(ERROR) << "no algo found: " << algo;
    throw std::invalid_argument("invalid algo");
  }
  return itr->second;
}

float
LegacyAlgo::get_weight(const std::string& algo, const std::string& feat)
{
  // FIXME shared lock
  const auto& itr = algos_.find(algo);
  if (itr != algos_.end()) {
    return itr->second.get_weight(feat);
  }
  LOG(WARNING) << "missing feature weight: algo " << algo << ", feat " << feat;
  return 0;
}

Legacy::Legacy()
    : algo_()
{
  // TODO fetch algos from db every some interval minutes
  db_.fetch_algos(algo_);
}

void
Legacy::ranking(RankItr begItr, RankItr endItr)
{
  const auto& weights = algo_.get_weights("legacy");

  LegacyScore ls(weights);

  std::for_each(begItr, endItr,
                [this, &ls](DataPoint& dp) {
                  dp.score = ls.score(dp);
                });
}

}
