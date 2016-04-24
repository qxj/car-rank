// -*- mode: c++ -*-
//
// Copyright (C) 2016 Julian Qian
//
// @file      legecy.cpp
// @author    Julian Qian <junist@gmail.com>
// @created   2016-04-25 07:33:39
//

#include <algorithm>

#include "legecy.hpp"

using namespace ranking;

void
Legecy::ranking(const ranking::JsonRequest & req, ranking::JsonReply & rep)
{
  const JsonRequest::CarsType& cars = req.cars;
  std::sort(cars.begin(), cars.end(),
            [](const CarInfo& a, const CarInfo& b) {
              return a.score > b.score;
            });
  rep.from_request(req);
}
