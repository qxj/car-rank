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
FeatureDb::fetch_feats(std::vector<DataPoint>& dps, int user_id)
{
  driver_->threadInit();
  try {
    std::unique_ptr<sql::Connection> conn(driver_->connect(
        FLAGS_my_host, FLAGS_my_user, FLAGS_my_passwd));
    conn->setSchema(FLAGS_my_dbname);

    std::unique_ptr<sql::Statement> stmt(conn->createStatement());

    std::unordered_set<int> collected_cars;

    // car_rank_users
    if (user_id > 0) {
      std::string sql{"select collected_cars from car_rank_users where user_id="};
      sql.append(std::to_string(user_id));

      VLOG(100) << "sql: " << sql;

      std::unique_ptr<sql::ResultSet> res(stmt->executeQuery(sql));
      if (res->next()) {
        using namespace boost::algorithm;
        {
          std::string str{std::move(res->getString("collected_cars"))};
          std::string word;

          for (auto it = make_split_iterator(str, token_finder(is_from_range(',', ',')));
               it != decltype(it)(); ++it) {
            word = std::move(boost::copy_range<std::string>(*it));
            try {
              collected_cars.insert(std::stoi(word));
            } catch (const std::invalid_argument& e) {
              VLOG(100) << "Invalid collected car_id: " << word;
            }
          }
        }
      }
    }

    // car_rank_feats
    {
      std::string sql{"select car_id,city_code,price_daily,proportion,"
            "review,review_cnt,auto_accept,quick_accept,station,confirm_rate,"
            "collect_cnt from car_rank_feats where car_id in ("};
      std::for_each(dps.begin(), dps.end(),
              [&sql](DataPoint& dp)
              {
                sql.append(std::to_string(dp.id));
                sql.push_back(',');
              });
      sql.back() = ')';
      sql.append(" order by car_id");

      VLOG(100) << "sql: " << sql;

      std::unique_ptr<sql::ResultSet> res(stmt->executeQuery(sql));
      while (res->next()) {
        int car_id = res->getInt("car_id");
        auto itr = collected_cars.find(car_id);
        if (itr != collected_cars.end()) {
          set_feat(dp, "is_collect", 1);
        }

        float price = static_cast<float>(res->getInt("price_daily"));
        set_feat(dp, "price", price);
        float proportion = static_cast<float>(res->getDouble("proportion"));
        set_feat(dp, "proportion", proportion);
        float review = static_cast<float>(res->getDouble("review"));
        set_feat(dp, "review", review);
        float review_cnt = static_cast<float>(res->getInt("review_cnt"));
        set_feat(dp, "review_cnt", review_cnt);
        float auto_accept = static_cast<float>(res->getInt("auto_accept"));
        set_feat(dp, "auto_accept", auto_accept);
        float quick_accept = static_cast<float>(res->getInt("quick_accept"));
        set_feat(dp, "quick_accept", quick_accept);
        float station = static_cast<float>(res->getInt("station"));
        set_feat(dp, "station", station);
        float confirm_rate = static_cast<float>(res->getDouble("confirm_rate"));
        set_feat(dp, "confirm_rate", confirm_rate);
        float collect_cnt = static_cast<float>(res->getInt("collect_cnt"));
        set_feat(dp, "collect_cnt", collect_cnt);
      }
    }


  } catch (sql::SQLException &e) {
    LOG(ERROR) << "Mysql error " << e.what()
               << ", SQLState: " << e.getSQLState() ;
  }

  driver_->threadEnd();

}

void
FeatureDb::set_feat(DataPoint& dp, const std::string& name, float value)
{
  int idx = feat_index(name);
  dp.feats[idx] = value;
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
