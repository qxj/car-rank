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
#include <unordered_map>
#include <unordered_set>

#include <boost/algorithm/string.hpp>

#include <mysql_public_iface.h>

#include <gflags/gflags.h>
#include <glog/logging.h>

#include "feature_db.hpp"

DEFINE_string(my_host, "tcp://127.0.0.1:3306", "mysql host");
DEFINE_string(my_user, "root", "mysql user");
DEFINE_string(my_passwd, "root", "mysql password");
DEFINE_string(my_dbname, "test", "mysql database");

namespace fi = ::feat_idx;

namespace ranking
{

FeatureDb::FeatureDb()
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

    // TODO cache collected_cars for users

    std::unordered_set<int> collected_cars;
    std::unordered_set<int> ordered_cars;
    std::unordered_set<int> prefer_models;
    std::pair<int, int> prefer_price{0, 0};

    // car_rank_users
    if (user_id > 0) {
      std::string sql{"select collected_cars,ordered_cars,prefer_models,"
            "prefer_price from car_rank_users where user_id="};
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
        {
          std::string str{res->getString("ordered_cars")};
          std::string word;

          for (auto it = make_split_iterator(str, token_finder(is_from_range(',', ',')));
               it != decltype(it)(); ++it) {
            word = std::move(boost::copy_range<std::string>(*it));
            try {
              ordered_cars.insert(std::stoi(word));
            } catch (const std::invalid_argument& e) {
              VLOG(100) << "Invalid ordered car_id: " << word;
            }
          }
        }
        {
          std::string str{res->getString("prefer_models")};
          std::string word;

          for (auto it = make_split_iterator(str, token_finder(is_from_range(',', ',')));
               it != decltype(it)(); ++it) {
            word = std::move(boost::copy_range<std::string>(*it));
            try {
              prefer_models.insert(std::stoi(word));
            } catch (const std::invalid_argument& e) {
              VLOG(100) << "Invalid prefer model: " << word;
            }
          }
        }
        {
          std::string str{res->getString("prefer_price")};
          size_t pos = str.find(',');
          if (pos != std::string::npos) {
            try {
              prefer_price.first = std::stoi(str.substr(0, pos));
              prefer_price.second = std::stoi(str.substr(pos+1));
            } catch (const std::out_of_range& e) {
              LOG(ERROR) << "failed to parse prefer_price " << str;
            } catch (const std::invalid_argument& e) {
              VLOG(100) << "Invalid price range: " << str;
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
      int i = 0;
      while (res->next() && i < dps.size()) {
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

        {
          auto itr = collected_cars.find(car_id);
          if (itr != collected_cars.end()) {
            dp.set(fi::IS_COLLECT, 1);
          }
        }
        {
          auto itr = ordered_cars.find(car_id);
          if (itr != ordered_cars.end()) {
            dp.set(fi::IS_ORDERED, 1);
          }
        }

        float price = static_cast<float>(res->getInt("price_daily"));
        dp.set(fi::PRICE, price);

        {
          if (dp.get(fi::PRICE) > 0) {  // request will override db
            price = dp.get(fi::PRICE);
          }
          if (price >= prefer_price.first &&
              price <= prefer_price.second) {
            dp.set(fi::IS_PRICE, 1);
          }
        }

        int model = res->getInt("model");
        {
          auto itr = prefer_models.find(model);
          if (itr != prefer_models.end()) {
            dp.set(fi::IS_MODEL, 1);
          }
        }

        float proportion = static_cast<float>(res->getDouble("proportion"));
        dp.set(fi::PROPORTION, proportion);
        float review = static_cast<float>(res->getDouble("review"));
        dp.set(fi::REVIEW, review);
        float review_cnt = static_cast<float>(res->getInt("review_cnt"));
        dp.set(fi::REVIEW_CNT, review_cnt);
        float auto_accept = static_cast<float>(res->getInt("auto_accept"));
        dp.set(fi::AUTO_ACCEPT, auto_accept);
        float quick_accept = static_cast<float>(res->getInt("quick_accept"));
        dp.set(fi::QUICK_ACCEPT, quick_accept);
        float station = static_cast<float>(res->getInt("station"));
        dp.set(fi::STATION, station);
        float confirm_rate = static_cast<float>(res->getDouble("confirm_rate"));
        dp.set(fi::CONFIRM_RATE, confirm_rate);
        float collect_cnt = static_cast<float>(res->getInt("collect_cnt"));
        dp.set(fi::COLLECT_COUNT, collect_cnt);
      }

      VLOG(100) << "loaded " << res->rowsCount() << " car feature rows";
    }


  } catch (sql::SQLException &e) {
    LOG(ERROR) << "Mysql error " << e.what()
               << ", SQLState: " << e.getSQLState() ;
  }

  driver_->threadEnd();
}

}
