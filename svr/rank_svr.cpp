// -*- mode: c++ -*-
//
// Copyright (C) 2016 Julian Qian
//
// @file      rank_svr.cpp
// @author    Julian Qian <junist@gmail.com>
// @created   2016-04-24 23:02:37
//

#include <functional>

#include <gflags/gflags.h>
#include <glog/logging.h>

#include "rank_svr.hpp"

DEFINE_int32(thread_pool_size, 4, "rank server thread pool size");
DEFINE_string(memcached_server, "", "memcached server address list");
DEFINE_int32(memcached_expired_secs, 600, "memcached expired seconds");
DECLARE_bool(dry);

RankSvr::RankSvr(const std::string& address, short port)
    : http::server::server(address, port, FLAGS_thread_pool_size),
      cache_(FLAGS_memcached_server, FLAGS_memcached_expired_secs)
{}

void
RankSvr::legacy_handler(const http::server::request& req,
        http::server::reply& rep)
{

  std::string cached_content;
  std::hash<std::string> hash_func;
  uint32_t reqid = hash_func(req.content);
  try {
    cached_content = cache_.get(std::to_string(reqid));
  } catch(const std::runtime_error& e) {
    LOG(WARNING) << "Runtime error: " << e.what();
  } catch(const std::invalid_argument& e) {
    VLOG(100) << "Invalid args: " << e.what();
  }

  VLOG(100) << "request content " << req.content;

  if (cached_content.empty()) {

    ranking::JsonRequest jreq;
    ranking::JsonReply jrep;
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

    try {
      cache_.set(std::to_string(reqid), rep.content);
    } catch(const std::runtime_error& e) {
      LOG(WARNING) << e.what();
    } catch(const std::invalid_argument& e) {
      VLOG(100) << e.what();
    }
  } else {
    rep.content.assign(cached_content);
    VLOG(100) << "hit cache, key: " << reqid;
  }

  VLOG(100) << "reply content " << rep.content;
  rep.add_content_type("plain/json");
}
