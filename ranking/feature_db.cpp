// -*- mode: c++ -*-
//
// Copyright (C) 2016 Julian Qian
//
// @file      feature_db.cpp
// @author    Julian Qian <junist@gmail.com>
// @created   2016-07-15 23:44:44
//

#include <iostream>
#include <stdexcept>

#include <boost/algorithm/string.hpp>

#include <mysql_public_iface.h>

#include <gflags/gflags.h>
#include <glog/logging.h>

#include "feature_db.hpp"

DECLARE_string(my_host);
DECLARE_string(my_user);
DECLARE_string(my_passwd);
DECLARE_string(my_dbname);

namespace ranking
{

FeatureDb::FeatureDb(std::string feat_file)
    : driver_(nullptr), mutex_()
{
  std::lock_guard<std::mutex> lock(mutex_);
  // not thread-safe
  driver_ = sql::mysql::get_driver_instance();
}

FeatureDb::~FeatureDb()
{

}

void
FeatureDb::fetch_feats(std::vector<DataPoint>& dps)
{
  driver_->threadInit();
  try {
    std::unique_ptr<sql::Connection> conn(driver_->connect(
        FLAGS_my_host, FLAGS_my_user, FLAGS_my_passwd));
    conn->setSchema(FLAGS_my_dbname);

    std::unique_ptr<sql::Statement> stmt(conn->createStatement());

    // car_rank_feats
    {
      std::string sql{"select city_code, price_daily, proportion, review,"
            "review_cnt,auto_accept,quick_accept,station,confirm_rate,"
            "collect_count from car_rank_feats where car_id in ("};
      std::for_each(dps.begin(), dps.end(),
              [&sql](DataPoint& dp)
              {
                sql.append(std::to_string(dp.id));
                sql.push_back(',');
              });
      sql.back() = ')';
      std::unique_ptr<sql::ResultSet> res(stmt->executeQuery(sql));
      while (res->next()) {
      }
    }

  } catch (sql::SQLException &e) {
    LOG(ERROR) << "Mysql error " << e.what()
               << ", SQLState: " << e.getSQLState() ;
  }

  driver_->threadEnd();

}

int
FeatureDb::feat_index(const std::string& feat_name)
{
  auto itr = featMap_.find(feat_name);
  if (itr != featMap_.end()) {
    return itr->second;
  }
  LOG(WARN) << "feature " << feat_name << " is missing.";
  return 0;
}

void
FeatureDb::load_feat_map(const std::string& feat_file)
{
  std::ifstream fin(feat_file, std::ios_base::in);
  if (fin.fail()) {
    LOG(ERROR) << "Failed to open feature file " << feat_file;
    throw std::invalid_argument("failed to open feature file");
  }
  std::string line
  for (int lineno = 1; std::getline(fin, line); lineno ++) {
    boost::trim(line);
    if (line.empty() || line[0] == '#') continue;
    featMap_[line] = lineno;
    LOG(INFO) << "feature " << line << " -> " << lineno;
  }
  fin.close();
}

}
