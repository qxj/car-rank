// -*- mode: c++ -*-
//
// Copyright (C) 2016 Julian Qian
//
// @file      rank_svr.hpp
// @author    Julian Qian <junist@gmail.com>
// @created   2016-04-24 22:59:02
//

#ifndef RANK_SVR_HPP_
#define RANK_SVR_HPP_

#include "server.hpp"
#include "legacy.hpp"
#include "lambda_mart.hpp"
#include "json_request.hpp"
#include "mem_cache.hpp"

class RankSvr : public http::server::server
{
 public:
  RankSvr(const std::string& address, short port);
  void rank_handler(const http::server::request& req, http::server::reply& rep);
 private:
  ranking::Legacy legacy_;
  ranking::LambdaMart lmart_;
  MemCache cache_;
};

#endif // RANK_SVR_HPP_
