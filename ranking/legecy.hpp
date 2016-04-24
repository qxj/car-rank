// -*- mode: c++ -*-
//
// Copyright (C) 2016 Julian Qian
//
// @file      legecy.hpp
// @author    Julian Qian <junist@gmail.com>
// @created   2016-04-24 22:31:14
//

#ifndef LEGECY_HPP_
#define LEGECY_HPP_

#include "ranker.hpp"
#include "legecy_db.hpp"

namespace ranking
{
class Legecy : public Ranker
{
 public:
  void ranking(const JsonRequest&, JsonReply&) override;
 private:
  LegecyDb db_;
};
}

#endif // LEGECY_HPP_
