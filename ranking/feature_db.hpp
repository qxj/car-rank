// -*- mode: c++ -*-
//
// Copyright (C) 2016 Julian Qian
//
// @file      feature_db.hpp
// @author    Julian Qian <junist@gmail.com>
// @created   2016-07-15 23:38:26
//

#ifndef FEATURE_DB_HPP_
#define FEATURE_DB_HPP_

#include <map>
#include <mutex>
#include <string>
#include <vector>

#include "data_point.hpp"

namespace sql
{
class Connection;
class Driver;
}

namespace ranking
{

class FeatureDb
{
 public:
  FeatureDb();
  ~FeatureDb();

  void fetch_feats(RankItr, RankItr, int);

 private:
  sql::Driver* driver_;
  std::mutex mutex_;
};
}

#endif // FEATURE_DB_HPP_
