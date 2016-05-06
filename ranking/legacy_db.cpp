// -*- mode: c++ -*-
//
// Copyright (C) 2016 Julian Qian
//
// @file      legacy_db.cpp
// @author    Julian Qian <junist@gmail.com>
// @created   2016-04-24 20:20:52
//

#include <algorithm>
#include <exception>
#include <memory>
#include <set>
#include <unordered_map>

#include <boost/algorithm/string.hpp>

#include <mysql_public_iface.h>

#include <gflags/gflags.h>
#include <glog/logging.h>

#include "legacy_db.hpp"

DEFINE_string(my_host, "tcp://127.0.0.1:3306", "mysql host");
DEFINE_string(my_user, "root", "mysql user");
DEFINE_string(my_passwd, "root", "mysql password");
DEFINE_string(my_dbname, "test", "mysql database");

namespace ranking
{

const LegacyAlgo::Weights&
LegacyAlgo::get_weights(const std::string& algo)
{
  const auto& itr = algos_.find(algo);
  if (itr == algos_.end()) {
    LOG(ERROR) << "no algo found: " << algo;
    throw std::invalid_argument("invalid algo");
  }
  return itr->second;
}

float
LegacyAlgo::get_weight(const std::string& algo, const std::string& feat)
{
  // FIXME shared lock
  const auto& itr = algos_.find(algo);
  if (itr != algos_.end()) {
    return itr->second.get_weight(feat);
  }
  LOG(WARNING) << "missing feature weight: algo " << algo << ", feat " << feat;
  return 0;
}

LegacyDb::LegacyDb()
    : driver_(nullptr), mutex_()
{
  std::lock_guard<std::mutex> lock(mutex_);
  // not thread-safe
  driver_ = sql::mysql::get_driver_instance();
}

LegacyDb::~LegacyDb()
{
  // delete driver_;
}

void
LegacyDb::fetch_scores(JsonRequest& req)
{
  driver_->threadInit();
  try {
    std::unique_ptr<sql::Connection> conn(driver_->connect(
        FLAGS_my_host, FLAGS_my_user, FLAGS_my_passwd));

    conn->setSchema(FLAGS_my_dbname);

    std::unique_ptr<sql::Statement> stmt(conn->createStatement());

    // combine car ids
    JsonRequest::CarsType& cars = req.cars;
    std::string cars_sql;
    std::for_each(cars.begin(), cars.end(),
                  [&cars_sql](CarInfo& c)
                  {
                    cars_sql.append(std::to_string(c.car_id));
                    cars_sql.push_back(',');
                  });
    if (!cars_sql.empty()) {
      // remove trailing comma
      cars_sql.erase(cars_sql.end() -1);
    }

    // TODO cache collected_cars for users
    std::unordered_map<int, float> prefs;
    // car_rank_users
    {
      std::string sql{"select car_id, preference from car_rank_users where expired=0 and user_id="};
      sql.append(std::to_string(req.user_id));
      sql.append(" and car_id in (");
      sql.append(cars_sql);
      sql.append(") limit 200");

      VLOG(100) << "sql: " << sql;

      std::unique_ptr<sql::ResultSet> res(stmt->executeQuery(sql));
      while (res->next()) {
        int car_id = res->getInt("car_id");
        float pref = static_cast<float>(res->getDouble("preference"));
        prefs[car_id] = pref;
      }
      VLOG(100) << "loaded " << res->rowsCount() << " user preferences";
    }

    // car_rank_legecy
    {
      std::string sql{"select car_id, quality from car_rank_legacy where car_id in ("};
      std::for_each(cars.begin(), cars.end(),
              [&sql](CarInfo& c)
              {
                sql.append(std::to_string(c.car_id));
                sql.push_back(',');
              });
      sql.back() = ')';

      VLOG(100) << "sql: " << sql;

      std::unique_ptr<sql::ResultSet> res(stmt->executeQuery(sql));
      std::unordered_map<int, float> qualities;
      while (res->next()) {
        int car_id = res->getInt("car_id");
        float score = static_cast<float>(res->getDouble("quality"));
        qualities[car_id] = score;
      }

      VLOG(100) << "loaded " << res->rowsCount() << " car quality scores";

      for (auto& car: cars) {
        car.quality = qualities[car.car_id];
        auto itr = prefs.find(car.car_id);
        if (itr != prefs.end()) {
          car.preference = itr->second;
        }
      }
    }

  } catch (sql::SQLException &e) {
    LOG(ERROR) << "Mysql error " << e.what()
               << ", SQLState: " << e.getSQLState() ;
  }

  driver_->threadEnd();
}

void
LegacyDb::fetch_algos(LegacyAlgo& algo)
{
  driver_->threadInit();
  try {
    std::unique_ptr<sql::Connection> conn(driver_->connect(
        FLAGS_my_host, FLAGS_my_user, FLAGS_my_passwd));

    conn->setSchema(FLAGS_my_dbname);

    std::unique_ptr<sql::Statement> stmt(conn->createStatement());

    {

      std::string sql{"select algo, name, weight from car_rank_weights where enabled=1"};

      VLOG(100) << "sql: " << sql;

      std::unique_ptr<sql::ResultSet> res(stmt->executeQuery(sql));
      algo.clear();
      while (res->next()) {
        std::string algo_name{res->getString("algo")};
        std::string feat_name{res->getString("name")};
        float weight = static_cast<float>(res->getDouble("weight"));
        algo.add_weight(algo_name, feat_name, weight);

        VLOG(100) << "algo " << algo_name << ", feat " << feat_name
                  << ", weight " << weight;
      }
      LOG(INFO) << "loaded " << algo.size() << " algos, and "
                << res->rowsCount() << " weights";
    }

  } catch (sql::SQLException &e) {
    LOG(ERROR) << "Mysql error " << e.what()
               << ", SQLState: " << e.getSQLState() ;
  }
  driver_->threadEnd();
}

}
