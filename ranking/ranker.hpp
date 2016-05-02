// -*- mode: c++ -*-
//
// Copyright (C) 2016 Julian Qian
//
// @file      ranker.hpp
// @author    Julian Qian <junist@gmail.com>
// @created   2016-04-24 22:34:29
//

#ifndef RANKER_HPP_
#define RANKER_HPP_

#include "json_request.hpp"

namespace ranking
{
class Ranker
{
 public:
  virtual void ranking(JsonRequest&, JsonReply&) = 0;
};
}

#endif // RANKER_HPP_
