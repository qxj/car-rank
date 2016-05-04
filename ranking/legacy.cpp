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

void
Legacy::ranking(ranking::JsonRequest & req, ranking::JsonReply & rep)
{
  JsonRequest::CarsType& cars = req.cars;
  db_.query_scores(cars);
  std::sort(cars.begin(), cars.end(),
            [](const CarInfo& a, const CarInfo& b) {
              return a.score > b.score;
            });
  rep.from_request(req);
}
