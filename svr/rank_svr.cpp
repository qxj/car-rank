// -*- mode: c++ -*-
//
// Copyright (C) 2016 Julian Qian
//
// @file      rank_svr.cpp
// @author    Julian Qian <junist@gmail.com>
// @created   2016-04-24 23:02:37
//

#include <glog/logging.h>

#include "rank_svr.hpp"

void
RankSvr::legacy_handler(const http::server::request& req, http::server::reply& rep)
{
  ranking::JsonRequest jreq;
  ranking::JsonReply jrep;
  VLOG(100) << "request content " << req.content;
  parser_.parse_request(req.content, jreq);
  legacy_.ranking(jreq, jrep);
  parser_.reply_string(jrep, rep.content);
  VLOG(100) << "reply content " << rep.content;
  rep.add_content_type("plain/json");
}
