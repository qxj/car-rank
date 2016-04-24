// -*- mode: c++ -*-
//
// Copyright (C) 2016 Julian Qian
//
// @file      rank_svr.cpp
// @author    Julian Qian <junist@gmail.com>
// @created   2016-04-24 23:02:37
//

#include "rank_svr.hpp"

void
RankSvr::legecy_handler(const http::server::request& req, http::server::reply& rep)
{
  ranking::JsonRequest jreq;
  ranking::JsonReply jrep;
  parser_.parse_request(req.content, jreq);
  legecy_.ranking(jreq, jrep);
  parser_.reply_string(jrep, rep.content);
  rep.add_content_type("plain/json");
}
