// -*- mode: c++ -*-
//
// Copyright (C) 2016 Julian Qian
//
// @file      ensemble.cpp
// @author    Julian Qian <junist@gmail.com>
// @created   2016-07-22 16:32:19
//

#include <cstring>
#include <fstream>
#include <sstream>
#include <iomanip>

#include <glog/logging.h>
#include <pugixml.hpp>

#include "ensemble.hpp"

namespace ranking
{
double
Split::eval(const DataPoint& dp)
{
  const Split* sp{this};
  while (sp->feat_ != -1) {
    if (dp.get(sp->feat_) <= sp->threshold_) {
      sp = sp->left_.get();
    } else {
      sp = sp->right_.get();
    }
  }
  return sp->output_;
}

std::string
Split::get_string(std::string indent) const
{
  std::ostringstream oss;
  if (is_leaf()) {
    oss << indent << "output: " << output_ << "\n";
  } else {
    oss << indent << "feature: " << feat_ << "\n";
    oss << indent << "threshold: " << threshold_ << "\n";
    oss << left_->get_string(indent + "\t");
    oss << right_->get_string(indent + "\t");
  }
  return oss.str();
}

std::string
Split::to_string() const
{
  return get_string("");
}

std::string
RegressionTree::to_string() const
{
  return root_->to_string();
}

Ensemble::Ensemble(std::string model_file)
{
  std::ifstream fin(model_file, std::ios_base::in);
  if (fin.fail()) {
    LOG(ERROR) << "Failed to open model file " << model_file;
  } else {
    std::string xml;
    for (std::string line; std::getline(fin, line); ) {
      if (line[0] == '#') {
        continue;
      }
      xml.append(line);
    }
    fin.close();
    LOG(INFO) << "Read model " << model_file << ", totally "
              << xml.size() << " bytes.";
    build_trees(xml.c_str());
  }
}

Ensemble::Ensemble(const char* xmlContent)
{
  build_trees(xmlContent);
}

SplitPtr create_tree(const pugi::xml_node& root)
{
  SplitPtr sptr;
  pugi::xml_node node = root.first_child();
  if (std::strncmp(node.name(), "feature", 8) == 0) {  // split
    int feat = node.text().as_int();
    pugi::xml_node threNode = node.next_sibling();  // threshold
    float threshold = threNode.text().as_float();
    sptr.reset(new Split(feat, threshold));

    pugi::xml_node leftNode = threNode.next_sibling();
    sptr->setLeft(create_tree(leftNode));
    pugi::xml_node rightNode = leftNode.next_sibling();
    sptr->setRight(create_tree(rightNode));
  } else {  // stump
    double output = node.text().as_double();
    sptr.reset(new Split(output));
  }
  return sptr;
}

void
Ensemble::build_trees(const char* xmlContent)
{
  pugi::xml_document doc;
  pugi::xml_parse_result result = doc.load_string(xmlContent);
  if (!result) {
    LOG(ERROR) << "Failed to parse model xml content";
    return;
  }

  pugi::xml_node trees = doc.child("ensemble");
  for (pugi::xml_node tree: trees.children("tree")) {
    pugi::xml_attribute attr = tree.attribute("weight");
    float weight = attr.as_float();
    weights_.push_back(weight);
    const char* treeId = tree.attribute("id").value();
    LOG(INFO) << "build tree " << treeId;
    // build regression tree
    pugi::xml_node root = tree.child("split");
    SplitPtr sp = create_tree(root);
    trees_.push_back(std::make_shared<RegressionTree>(sp));
  }
}

float
Ensemble::eval(const DataPoint& dp)
{
  double score;
  for (size_t i=0; i<trees_.size(); i++) {
    auto& tree = trees_[i];
    float weight = weights_[i];
    score += tree->eval(dp) * weight;
  }
  return static_cast<float>(score);
}

}
