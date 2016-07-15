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

#include <vector>

namespace ranking
{
struct DataPoint
{
  // feature index starts from 1
  int id;
  std::vector<float> feats;

  float getValue(int feat_id) {
    return feats[feat_id];
  }
};
}

#endif // DATA_POINT_HPP_
