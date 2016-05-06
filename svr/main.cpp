// -*- mode: c++ -*-
//
// Copyright (C) 2016 Julian Qian
//
// @file      main.cpp
// @author    Julian Qian <junist@gmail.com>
// @created   2016-05-04 16:37:58
//

#include <iostream>
#include <string>
#include <functional>

#include <boost/asio.hpp>
#include <gflags/gflags.h>
#include <glog/logging.h>

#include "rank_svr.hpp"
#include "util.hpp"

DEFINE_string(host, "0.0.0.0", "rank server host");
DEFINE_int32(port, 20164, "rank server port");
DEFINE_bool(daemon, true, "run as a daemonized service");
DEFINE_bool(dry, false, "whether only dry-run for testing");
DEFINE_string(lock_file, "/tmp/rank_svr.pid", "rank svr pid file");

int main(int argc, char* argv[])
{
  using namespace std::placeholders;

  google::ParseCommandLineFlags(&argc, &argv, true);

  google::InitGoogleLogging(argv[0]);

  if (already_running(FLAGS_lock_file.c_str())) {
    LOG(ERROR) << "another instance is already running, check " << FLAGS_lock_file;
    return -1;
  }

  if (FLAGS_daemon) {
    daemonize();
  }

  LOG(INFO) << "GFLAGS:\n" << google::CommandlineFlagsIntoString() << std::endl;

  try
  {
    // Initialise the server.
    RankSvr s(FLAGS_host, static_cast<short>(FLAGS_port));

    s.add_handler("/legacy", std::bind(
        &RankSvr::legacy_handler, &s, _1, _2));

    // Run the server until stopped.
    s.run();
  }
  catch (std::exception& e)
  {
    LOG(ERROR) << "exception: " << e.what() ;
  }

  LOG(INFO) << "QUIT rank server.";

  return 0;
}
