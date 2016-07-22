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

#include <map>

#include "ranker.hpp"

#include "legacy_db.hpp"

namespace ranking
{

class LegacyAlgo
{
  // friend class LegacyDb;
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

  void clear() {
    algos_.clear();
  }

  void add_weight(const std::string& algo, const std::string& feat,
                  float weight) {
    algos_[algo].set_weight(feat, weight);
  }

 private:
  typedef std::map<std::string, Weights> Algos;

  Algos algos_;
};

class Legacy : public Ranker
{
 public:
  Legacy();
  virtual ~Legacy() {}
  void update(RankItr beg, RankItr end, int user_id)
  {
    db_.fetch_legacy(beg, end, user_id);
  }

  void ranking(RankItr, RankItr) override;

 private:
  LegacyAlgo algo_;
  LegacyDb db_;
};
}

#endif // LEGACY_HPP_
