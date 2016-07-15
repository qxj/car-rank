// -*- mode: c++ -*-
//
// Copyright (C) 2016 Julian Qian
//
// @file      lambda_mart.hpp
// @author    Julian Qian <junist@gmail.com>
// @created   2016-07-15 22:51:26
//

#ifndef LAMBDA_MART_HPP_
#define LAMBDA_MART_HPP_

#include "ranker.hpp"
#include "json_request.hpp"

namespace ranking
{

class LambdaMart : public Ranker
{
 public:
  LambdaMart();
  void ranking(JsonRequest&, JsonReply&) override;

};
}

#endif // LAMBDA_MART_HPP_
