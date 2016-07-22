// -*- mode: c++ -*-
//
// Copyright (C) 2016 Julian Qian
//
// @file      ensemble_test.cpp
// @author    Julian Qian <junist@gmail.com>
// @created   2016-07-22 19:04:36
//

#include <iostream>
#include <gtest/gtest.h>
#include <glog/logging.h>

#include "ensemble.hpp"

namespace ranking
{
class EnsembleTest : public ::testing::Test
{
 protected:
  EnsembleTest() {}
  virtual ~EnsembleTest() {}
  virtual void SetUp()
  {
    // google::InitGoogleLogging("ensemble_test");
  }
};

TEST_F(EnsembleTest, build_trees)
{
  char xml[] = "<ensemble>"
      "<tree id=\"1\" weight=\"0.1\">"
      "  <split>"
      "    <feature> 15 </feature>"
      "    <threshold> 0.3 </threshold>"
      "    <split pos=\"left\">"
      "      <feature> 6 </feature>"
      "      <threshold> 1.074188 </threshold>"
      "      <split pos=\"left\">"
      "        <output> 1.128550 </output>"
      "      </split>"
      "      <split pos=\"right\">"
      "        <output> 0.181089 </output>"
      "      </split>"
      "    </split>"
      "    <split pos=\"right\">"
      "      <output> 1.031120 </output>"
      "    </split>"
      "  </split>"
      "</tree>"
      "<tree id=\"2\" weight=\"0.2\">"
      "  <split>"
      "    <feature> 11 </feature>"
      "    <threshold> 0.1 </threshold>"
      "    <split pos=\"left\">"
      "      <output> 2.3012931 </output>"
      "    </split>"
      "    <split pos=\"right\">"
      "      <output> -3.1029102 </output>"
      "    </split>"
      "  </split>"
      "</tree>"
      "</ensemble>";
  Ensemble ensemble(xml);
  for (auto& tree: ensemble.trees_) {
    std::cout << tree->to_string();
  }
  EXPECT_EQ(2, ensemble.trees_.size());
  SplitPtr sp = ensemble.trees_[0]->root();
  EXPECT_EQ(15, sp->feat());
  EXPECT_EQ(6, sp->left()->feat());
  EXPECT_LT(0.1, sp->left()->right()->output() );
  EXPECT_LT(1, sp->right()->output());
  SplitPtr sp1 = ensemble.trees_[1]->root();
  EXPECT_EQ(11, sp1->feat());
  EXPECT_TRUE(sp1->left()->is_leaf());
  EXPECT_LT(2, sp1->left()->output() );
}
}
