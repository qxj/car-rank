// -*- mode: c++ -*-
//
// Copyright (C) 2016 Julian Qian
//
// @file      rank_svr.cpp
// @author    Julian Qian <junist@gmail.com>
// @created   2016-04-24 23:02:37
//

#include <gflags/gflags.h>
#include <glog/logging.h>

#include "rank_svr.hpp"

DEFINE_int32(thread_pool_size, 4, "rank server thread pool size");
DECLARE_bool(dry);

RankSvr::RankSvr(const std::string& address, short port)
    : http::server::server(address, port, FLAGS_thread_pool_size)
{}

void
RankSvr::legacy_handler(const http::server::request& req, http::server::reply& rep)
{
  ranking::JsonRequest jreq;
  ranking::JsonReply jrep;
  // TODO cache req signature, if the same signature, return cached reply
  VLOG(100) << "request content " << req.content;
  try {
    parser_.parse_request(req.content, jreq);
    if (FLAGS_dry) {
      jrep.from_request(jreq);
    } else {
      legacy_.ranking(jreq, jrep);
    }
  } catch (const std::invalid_argument& e) {
    jrep.ret = -1;
    jrep.err_msg = e.what();
  }

  // TODO error handling
  parser_.reply_string(jrep, rep.content);
  VLOG(100) << "reply content " << rep.content;
  rep.add_content_type("plain/json");
}
