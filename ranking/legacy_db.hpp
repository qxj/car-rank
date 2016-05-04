// -*- mode: c++ -*-
//
// Copyright (C) 2016 Julian Qian
//
// @file      legacy_db.hpp
// @author    Julian Qian <junist@gmail.com>
// @created   2016-04-24 19:34:55
//

#ifndef LEGACY_DB_HPP_
#define LEGACY_DB_HPP_

#include <mutex>

#include <boost/noncopyable.hpp>

#include "json_request.hpp"

namespace sql
{
class Connection;
class Driver;
}

namespace ranking
{
class LegacyDb : private boost::noncopyable
{
 public:
  LegacyDb();
  ~LegacyDb();

  void query_scores(JsonRequest::CarsType& cars);
 private:
  sql::Driver* driver_;
  std::mutex mutex_;
};

}

#endif // LEGACY_DB_HPP_
