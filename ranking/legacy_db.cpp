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
#include <utility>

#include <boost/algorithm/string.hpp>

#include <mysql_public_iface.h>

#include <gflags/gflags.h>
#include <glog/logging.h>

#include "data_point.hpp"
#include "legacy.hpp"

#include "legacy_db.hpp"

DECLARE_string(my_host);
DECLARE_string(my_user);
DECLARE_string(my_passwd);
DECLARE_string(my_dbname);

namespace fi = ::feat_idx;

namespace ranking
{

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
LegacyDb::fetch_legacy(std::vector<DataPoint>& dps, int user_id)
{
  driver_->threadInit();
  try {
    std::unique_ptr<sql::Connection> conn(driver_->connect(
        FLAGS_my_host, FLAGS_my_user, FLAGS_my_passwd));

    conn->setSchema(FLAGS_my_dbname);

    std::unique_ptr<sql::Statement> stmt(conn->createStatement());

    // car_rank_legecy
    {
      std::string sql{"select car_id, quality, price, model from "
            "car_rank_legacy where car_id in ("};
      // combine car ids
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

      size_t i = 0;
      while (res->next()) {
        int car_id = res->getInt("car_id");

        while (i < dps.size() && dps[i].id != car_id) {
          LOG(ERROR) << "rotten request? car " << dps[i].id
                     << " is missing";
          i ++;
        }

        if (! (i < dps.size() && dps[i].id == car_id) ) {
          // throw std::invalid_argument("broken requests, no data");
          break;
        }

        auto& dp = dps[i++];

        float quality = static_cast<float>(res->getDouble("quality"));
        dp.set(fi::QUALITY, quality);
        // float price = static_cast<float>(res->getInt("price"));
        // dp.set(fi::PRICE, price);
        float model = static_cast<float>(res->getInt("model"));
        dp.set(fi::MODEL, model);
      }

      VLOG(100) << "loaded " << res->rowsCount() << " car quality scores";
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

      std::string sql{"select algo, name, weight from car_rank_weights "
            "where enabled=1"};

      VLOG(100) << "sql: " << sql;

      std::unique_ptr<sql::ResultSet> res(stmt->executeQuery(sql));
      algo.clear();
      while (res->next()) {
        std::string algo_name{res->getString("algo")};
        std::string feat_name{res->getString("name")};
        float weight = static_cast<float>(res->getDouble("weight"));
        algo.add_weight(algo_name, feat_name, weight);

        LOG(INFO) << "algo " << algo_name << ", feat " << feat_name
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
