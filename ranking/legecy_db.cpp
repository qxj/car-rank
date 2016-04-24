// -*- mode: c++ -*-
//
// Copyright (C) 2016 Julian Qian
//
// @file      legecy_db.cpp
// @author    Julian Qian <junist@gmail.com>
// @created   2016-04-24 20:20:52
//

#include <algorithm>
#include <memory>

#include <mysql_connection.h>
#include <cppconn/driver.h>
#include <cppconn/exception.h>
#include <cppconn/resultset.h>
#include <cppconn/statement.h>

#include <gflags/gflags.h>

#include "legecy_db.hpp"

DEFINE_string(my_host, "tcp://127.0.0.1:3306", "mysql host");
DEFINE_string(my_user, "root", "mysql user");
DEFINE_string(my_passwd, "root", "mysql password");
DEFINE_string(my_dbname, "test", "mysql database");

namespace ranking
{
LegecyDb::LegecyDb()
{
  // not thread-safe
  driver_ = sql::mysql::get_driver_instance();
}

LegecyDb::~LegecyDb()
{
  delete driver_;
}

void
LegecyDb::query_scores(JsonRequest::CarsType& cars)
{
  try {
    std::scoped_ptr<sql::Connection> conn(driver_->connect(
        FLAGS_my_host, FLAGS_my_user, FLAGS_my_passwd));

    conn->setSchema(FLAGS_my_dbname);

    std::scoped_ptr<sql::Statement> stmt(conn->createStatement());

    std::string sql{"select car_id, score from car_rank_legecy where car_id in ("};

    std::for_each(cars.begin(), cars.end(),
                  [&sql](auto& c)
                  {
                    sql.append(std::to_string(c.car_id));
                    sql.push_back(',');
                  });
    sql.back() = ')';

    VLOG(100) << "query sql: " << sql;

    {
      std::scoped_ptr<sql::ResultSet> res(stmt->executeQuery(sql));
      std::unordered_map<int, float> car_scores;
      while (res->next()) {
        int car_id = res->getInt("car_id");
        float score = static_cast<float>(res->getDouble("score"));
        car_scores[car_id] = score;
        VLOG(100) << "car_id " << car_id << ", score " << score;
      }

      for (auto& car: cars) {
        car.score = car_scores[car.car_id];
      }
    }

  } catch (sql::SQLException &e) {
    LOG(ERROR) << "Mysql error " << e.what()
               << ", SQLState: " << e.getSQLState() ;
  }
}
}
