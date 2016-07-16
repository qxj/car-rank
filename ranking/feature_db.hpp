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
#include "json_request.hpp"

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
  explicit FeatureDb(std::string feat_file);
  ~FeatureDb();

  void fetch_feats(std::vector<DataPoint>&, int);

  void set_feat(DataPoint&, const std::string&, float);
  int feat_index(const std::string& feat_name);

 private:
  void load_feat_map(const std::string&);


 private:
  std::map<std::string, int> featMap_;

  sql::Driver* driver_;
  std::mutex mutex_;
};
}

#endif // FEATURE_DB_HPP_
