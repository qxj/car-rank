// -*- mode: c++ -*-
//
// Copyright (C) 2016 Julian Qian
//
// @file      legacy_db.hpp
// @author    Julian Qian <junist@gmail.com>
// @created   2016-04-24 19:34:55
//

#ifndef LEGACY_DB_HPP_
#define LEGACY_DB_HPP_

#include <map>
#include <mutex>

#include <boost/noncopyable.hpp>

#include "json_request.hpp"

namespace sql
{
class Connection;
class Driver;
}

namespace ranking
{

class LegacyDb;

class LegacyAlgo
{
  friend class LegacyDb;
 public:

  typedef std::map<std::string, float> FeatWeightMap;
  typedef std::map<std::string, FeatWeightMap> AlgoMap;

  const FeatWeightMap& get_weights(const std::string& algo) noexcept(false);

  float get_weight(const std::string& algo, const std::string& feat);

 private:
  void add_weight(const std::string& algo, const std::string& feat,
                  float weight) {
    algos_[algo][feat] = weight;
  }

  void clear() {
    algos_.clear();
  }

 private:
  AlgoMap algos_;
};

class LegacyDb : private boost::noncopyable
{
 public:
  LegacyDb();
  ~LegacyDb();

  void query_scores(JsonRequest&);
  void fetch_algos(LegacyAlgo&);
 private:
  sql::Driver* driver_;
  std::mutex mutex_;
};

}

#endif // LEGACY_DB_HPP_
