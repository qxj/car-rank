// -*- mode: c++ -*-
//
// Copyright (C) 2016 Julian Qian
//
// @file      rank_svr.cpp
// @author    Julian Qian <junist@gmail.com>
// @created   2016-04-24 23:02:37
//

#include <iterator>
#include <functional>

#include <gflags/gflags.h>
#include <glog/logging.h>

#include "feat_idx.hpp"

#include "rank_svr.hpp"

DEFINE_int32(thread_pool_size, 4, "rank server thread pool size");
DEFINE_string(memcached_server, "", "memcached server address list");
DEFINE_int32(memcached_expired_secs, 600, "memcached expired seconds");
DEFINE_int32(rank_num, 0, "only rank first few cars (distance)");
DECLARE_bool(dry);

using namespace ranking;

RankSvr::RankSvr(const std::string& address, short port)
    : http::server::server(address, port, FLAGS_thread_pool_size),
      cache_(FLAGS_memcached_server, FLAGS_memcached_expired_secs)
{}

void
RankSvr::rank_handler(const http::server::request& req,
        http::server::reply& rep)
{

  std::string cached_content;
  std::hash<std::string> hash_func;
  uint32_t reqid = hash_func(req.content);
  try {
    cached_content = cache_.get(std::to_string(reqid));
  } catch(const std::runtime_error& e) {
    LOG(WARNING) << "runtime error: " << e.what();
  } catch(const std::invalid_argument& e) {
    VLOG(100) << "memcached: " << e.what();
  }

  VLOG(100) << "request content " << req.content;

  if (cached_content.empty()) {

    JsonRequest jreq;
    JsonReply jrep;
    try {
      jreq << req.content;
      VLOG(10) << jreq;
      if (FLAGS_dry) {
        jrep.from_request(jreq);
      } else {
        auto& cars = jreq.cars;
        int user_id = jreq.user_id;
        RankItr begItr = cars.begin();
        RankItr endItr = cars.end();
        RankItr headItr = cars.begin();
        if (FLAGS_rank_num > 0 && FLAGS_rank_num < cars.size()) {
          std::advance(headItr, FLAGS_rank_num);
        } else {
          headItr = cars.end();
        }
        if (headItr < endItr) {
          namespace fi = ::feat_idx;

          std::sort(headItr, endItr,
                  [](const DataPoint& a, const DataPoint& b) {
                    return a.get(fi::DISTANCE) < b.get(fi::DISTANCE);
                  });
        }
        // fetch features of cars
        featDb_.fetch_feats(begItr, headItr, user_id);
        if (jreq.algo == "lambdamart") {
          lmart_.ranking(begItr, headItr);
        } else {
          legacy_.update(begItr, headItr, user_id);
          legacy_.ranking(begItr, headItr);
        }

        std::sort(begItr, headItr,
                  [](const DataPoint& a, const DataPoint& b) {
                    return a.score > b.score;
                  });
        jrep.from_request(jreq);

        if (jreq.debug) {
          std::for_each(begItr, headItr,
                  [this, &jrep](const DataPoint& dp) {
                    jrep.scores.push_back(dp.score);
                  });
        }

      }
    } catch (const std::invalid_argument& e) {
      jrep.ret = -1;
      jrep.err_msg = e.what();
    }

    // TODO error handling
    jrep.to_buffer(rep.content);
    VLOG(10) << jrep;

    try {
      cache_.set(std::to_string(reqid), rep.content);
    } catch(const std::runtime_error& e) {
      LOG(WARNING) << e.what();
    } catch(const std::invalid_argument& e) {
      VLOG(100) << e.what();
    }
  } else {
    rep.content.assign(cached_content);
    VLOG(10) << "hit cache, key: " << reqid;
  }

  VLOG(100) << "reply content: " << rep.content;
  rep.add_content_type("plain/json");
}
