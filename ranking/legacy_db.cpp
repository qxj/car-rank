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
#include <tuple>
#include <unordered_map>
#include <unordered_set>
#include <utility>

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
    std::unordered_set<int> collected_cars;
    std::unordered_set<int> ordered_cars;
    std::unordered_set<int> prefer_models;
    std::pair<int, int> prefer_price{0, 0};
    // car_rank_users
    {
      std::string sql{"select collected_cars, ordered_cars, prefer_models, prefer_price from car_rank_users where user_id="};
      sql.append(std::to_string(req.user_id));

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
              LOG(ERROR) << "Invalid car_id: " << word;
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
              LOG(ERROR) << "Invalid car_id: " << word;
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
              LOG(ERROR) << "Invalid car_id: " << word;
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
              LOG(ERROR) << "Invalid price range: " << str;
            }
          }
        }
      }
    }

    // car_rank_legecy
    {
      std::string sql{"select car_id, quality, price, model from car_rank_legacy where car_id in ("};
      std::for_each(cars.begin(), cars.end(),
              [&sql](CarInfo& c)
              {
                sql.append(std::to_string(c.car_id));
                sql.push_back(',');
              });
      sql.back() = ')';

      VLOG(100) << "sql: " << sql;

      std::unique_ptr<sql::ResultSet> res(stmt->executeQuery(sql));
      std::unordered_map<int, std::tuple<float, int, int>> fetched_cars;
      while (res->next()) {
        int car_id = res->getInt("car_id");
        float quality = static_cast<float>(res->getDouble("quality"));
        int price = res->getInt("price");
        int model = res->getInt("model");
        fetched_cars[car_id] = std::make_tuple(quality, model, price);
      }

      VLOG(100) << "loaded " << res->rowsCount() << " car quality scores";

      for (auto& car: cars) {
        float quality;
        int model, price;
        std::tie(quality, model, price) = fetched_cars[car.car_id];
        car.quality = quality;
        {
          auto itr = collected_cars.find(car.car_id);
          if (itr != collected_cars.end()) {
            car.is_collected = 1;
          }
        }
        {
          auto itr = ordered_cars.find(car.car_id);
          if (itr != ordered_cars.end()) {
            car.is_ordered = 1;
          }
        }
        {
          auto itr = prefer_models.find(model);
          if (itr != prefer_models.end()) {
            car.is_model = 1;
          }
        }
        {
          if (car.price) {  // request will override db
            price = car.price;
          }
          if (price >= prefer_price.first &&
              price <= prefer_price.second) {
            car.is_price = 1;
          }
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
