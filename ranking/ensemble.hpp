// -*- mode: c++ -*-
//
// Copyright (C) 2016 Julian Qian
//
// @file      ensemble.hpp
// @author    Julian Qian <junist@gmail.com>
// @created   2016-07-22 16:27:28
//

#ifndef SPLIT_HPP_
#define SPLIT_HPP_

#include <memory>
#include <string>
#include <vector>

#include <gtest/gtest_prod.h>

#include "data_point.hpp"

namespace ranking
{
class Split
{
 public:
  Split() : feat_(-1) {}
  Split(int f, float th) : feat_(f), threshold_(th) {}
  explicit Split(double o) : feat_(-1), output_(o) {}

  double eval(const DataPoint& dp);

  void setLeft(std::shared_ptr<Split> sp)
  {
    left_.swap(sp);
  }
  void setRight(std::shared_ptr<Split> sp)
  {
    right_.swap(sp);
  }

  std::string to_string() const;
 public:
  bool is_leaf() const { return feat_ == -1; }
  std::shared_ptr<Split> left() const { return left_; }
  std::shared_ptr<Split> right() const { return right_; }
  int feat() const { return feat_; }
  float threshold() const { return threshold_; }
  double output() const { return output_; }
 private:
  std::string get_string(std::string indent) const;
 private:
  std::shared_ptr<Split> left_;
  std::shared_ptr<Split> right_;
 private:
  int feat_;
  float threshold_;
  double output_;
};

typedef std::shared_ptr<Split> SplitPtr;

class RegressionTree
{
 public:
  explicit RegressionTree(SplitPtr root) :
      root_(root) {}

  double eval(const DataPoint& dp)
  {
    return root_->eval(dp);
  }

  std::string to_string() const;

 public:
  SplitPtr root() const { return root_; }
 private:
  SplitPtr root_;
};

typedef std::shared_ptr<RegressionTree> TreePtr;

class Ensemble
{
  friend class EnsembleTest;
  FRIEND_TEST(EnsembleTest, build_trees);
 public:
  explicit Ensemble(std::string xmlFile);
  explicit Ensemble(const char* xmlContent);

  float eval(const DataPoint& dp);
 private:
  void build_trees(const char*);

 private:
  std::vector<TreePtr> trees_;
  std::vector<float> weights_;
};
}

#endif // SPLIT_HPP_
