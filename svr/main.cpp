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
#include <boost/asio.hpp>
#include <gflags/gflags.h>
#include <glog/logging.h>

#include "server.hpp"

DEFINE_string(host, "0.0.0.0", "rank server host");
DEFINE_string(port, "20164", "rank server port");

int main(int argc, char* argv[])
{
  google::ParseCommandLineFlags(&argc, &argv, true);
  // google::ReadFromFlagsFile("ranksvr.gflags", program_invocation_name, true);

  google::InitGoogleLogging(argv[0]);
  LOG(INFO) << "GFLAGS:\n" << google::CommandlineFlagsIntoString() << std::endl;

  try
  {
    // Initialise the server.
    http::server::server s(FLAGS_host, FLAGS_port);

    // Run the server until stopped.
    s.run();
  }
  catch (std::exception& e)
  {
    std::cerr << "exception: " << e.what() << "\n";
  }

  return 0;
}
