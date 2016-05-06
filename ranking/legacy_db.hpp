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

  class Weights
  {
   public:
    float get_weight(const std::string& feat) const
    {
      const auto& itr = weights_.find(feat);
      if (itr != weights_.end()) {
        return itr->second;
      }
      return 0;
    }
    void set_weight(const std::string& feat, float weight)
    {
      weights_[feat] = weight;
    }
   private:
    typedef std::map<std::string, float> FeatWeightMap;
    FeatWeightMap weights_;
  };

  const Weights& get_weights(const std::string& algo) noexcept(false);

  float get_weight(const std::string& algo, const std::string& feat);

  size_t size() const
  {
    return algos_.size();
  }

 private:
  void add_weight(const std::string& algo, const std::string& feat,
                  float weight) {
    algos_[algo].set_weight(feat, weight);
  }

  void clear() {
    algos_.clear();
  }

 private:
  typedef std::map<std::string, Weights> Algos;

  Algos algos_;
};

class LegacyDb : private boost::noncopyable
{
 public:
  LegacyDb();
  ~LegacyDb();

  void fetch_scores(JsonRequest&);
  void fetch_algos(LegacyAlgo&);
 private:
  sql::Driver* driver_;
  std::mutex mutex_;
};

}

#endif // LEGACY_DB_HPP_
