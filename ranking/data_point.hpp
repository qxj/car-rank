// -*- mode: c++ -*-
//
// Copyright (C) 2016 Julian Qian
//
// @file      data_point.hpp
// @author    Julian Qian <junist@gmail.com>
// @created   2016-07-15 23:31:53
//

#ifndef DATA_POINT_HPP_
#define DATA_POINT_HPP_

#include <array>
#include <string>
#include <vector>

#include "feat_idx.hpp"

namespace ranking
{
struct DataPoint
{
  DataPoint() = default;
  explicit DataPoint(int id) :
      id(id), score(0) {}

  int id;
  float score;

  // dense features
  std::array<float, feat_idx::MAX_NUM> feats{};

  void set(int feat, float val)
  {
    feats[feat] = val;
  }

  float get(int feat) const
  {
    return feats[feat];
  }

  bool operator<(const DataPoint& o) const
  {
    return this->id < o.id;
  }

  std::string to_string() const
  {
    std::string out{"dp id:"};
    out.append(std::to_string(id));
    out.append(",score:");
    out.append(std::to_string(score));
    out.append(",feats:");
    for (auto& f: feats) {
      out.append(std::to_string(f));
      out.append(",");
    }
    out.back() = '.';
    return out;
  }
};

typedef std::vector<DataPoint> RankList;
typedef RankList::iterator RankItr;
typedef RankList::const_iterator RankConstItr;

}

#endif // DATA_POINT_HPP_
