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
#include "legecy.hpp"

class RankSvr : public http::server::server
{
 public:
  void legecy_handler(const http::server::request& req, http::server::reply& rep);
 private:
  Legecy legecy_;
}

#endif // RANK_SVR_HPP_
