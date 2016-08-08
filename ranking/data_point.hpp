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
    std::string out{"DPid:"};
    out.append(std::to_string(id));
    out.append(",\tscore:");
    out.append(std::to_string(score));
    out.append("\n");
    for (size_t i=0; i<feats.size(); i++) {
      out.append("\t\t");
      out.append(std::to_string(i));
      out.append(":\t");
      out.append(std::to_string(feats[i]));
      out.append("\n");
    }
    return out;
  }
};

typedef std::vector<DataPoint> RankList;
typedef RankList::iterator RankItr;
typedef RankList::const_iterator RankConstItr;

}

#endif // DATA_POINT_HPP_
