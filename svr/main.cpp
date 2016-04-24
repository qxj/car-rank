//
// main.cpp
// ~~~~~~~~
//
// Copyright (c) 2003-2013, 2016 Christopher M. Kohlhoff (chris at kohlhoff dot com)
//
// Distributed under the Boost Software License, Version 1.0. (See accompanying
// file LICENSE_1_0.txt or copy at http://www.boost.org/LICENSE_1_0.txt)
//

#include <iostream>
#include <string>
#include <functional>

#include <boost/asio.hpp>
#include <gflags/gflags.h>
#include <glog/logging.h>

#include "rank_svr.hpp"

DEFINE_string(host, "0.0.0.0", "rank server host");
DEFINE_int32(port, 20164, "rank server port");

int main(int argc, char* argv[])
{
  using namespace std::placeholders;

  google::ParseCommandLineFlags(&argc, &argv, true);
  // google::ReadFromFlagsFile("ranksvr.gflags", program_invocation_name, true);

  google::InitGoogleLogging(argv[0]);
  LOG(INFO) << "GFLAGS:\n" << google::CommandlineFlagsIntoString() << std::endl;

  try
  {
    // Initialise the server.
    RankSvr s(FLAGS_host, static_cast<short>(FLAGS_port));

    s.add_handler("/legecy", std::bind(
        &RankSvr::legecy_handler, &s, _1, _2));

    // Run the server until stopped.
    s.run();
  }
  catch (std::exception& e)
  {
    LOG(ERROR) << "exception: " << e.what() ;
  }

  return 0;
}
