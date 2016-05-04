// -*- mode: c++ -*-
//
// Copyright (C) 2016 Julian Qian
//
// @file      legacy.hpp
// @author    Julian Qian <junist@gmail.com>
// @created   2016-04-24 22:31:14
//

#ifndef LEGACY_HPP_
#define LEGACY_HPP_

#include "ranker.hpp"
#include "legacy_db.hpp"

namespace ranking
{
class Legacy : public Ranker
{
 public:
  void ranking(JsonRequest&, JsonReply&) override;
 private:
  LegacyDb db_;
};
}

#endif // LEGACY_HPP_
