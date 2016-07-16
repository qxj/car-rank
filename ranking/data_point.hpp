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
#include <string>

namespace ranking
{
struct DataPoint
{
  enum {MAX_FEAT_NUM = 20};
  // feature index starts from 1
  int id;
  float feats[MAX_FEAT_NUM];

  void set(const std::string& feat, float val)
  {

  }

  float getValue(int feat_id) {
    return feats[feat_id];
  }
};
}

#endif // DATA_POINT_HPP_
