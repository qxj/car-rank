// -*- mode: c++ -*-
//
// Copyright (C) 2016 Julian Qian
//
// @file      legecy_db.hpp
// @author    Julian Qian <junist@gmail.com>
// @created   2016-04-24 19:34:55
//

#ifndef LEGECY_DB_HPP_
#define LEGECY_DB_HPP_

#include <boost/noncopyable.hpp>

#include "json_request.hpp"

namespace sql
{
class Connection;
class Driver;
}

namespace ranking
{
class LegecyDb : private boost::noncopyable
{
 public:
  LegecyDb();
  ~LegecyDb();

  void query_scores(JsonRequest::CarsType& cars);
 private:
  sql::Driver* driver_;
};

}

#endif // LEGECY_DB_HPP_
