// -*- mode: c++ -*-
//
// Copyright (C) 2016 Julian Qian
//
// @file      example_dummy_server.cpp
// @author    Julian Qian <junist@gmail.com>
// @created   2016-04-24 12:21:12
//

#include <string>
#include <iostream>
#include <functional>

#include "server.hpp"

using namespace http::server;

class dummy_server : public server
{
 public:
  dummy_server(const std::string& host, short port)
      : server(host, port)
  {}
  void dummy_handler(const request& req, reply& rep)
  {
    rep.add_content("hi, " + dummy);
  }
 private:
  std::string dummy = "dummy server";
};

int main(int argc, char *argv[])
{
  using namespace std::placeholders;

  short port = 8888;
  if (argc > 1) {
    port = static_cast<short>(std::stoi(argv[1]));
  }
  std::cout << "listen at port " << port << std::endl;
  try
  {
    dummy_server s("0.0.0.0", port);

    // s.add_handler("/",
    //               [&](const request& req, reply& rep)
    //               {
    //                 rep.add_content("hello, dummy server");
    //               });

    s.add_handler("/",
                  std::bind(&dummy_server::dummy_handler, &s,
                          _1, _2));
    // Run the server until stopped.
    s.run();
  }
  catch (std::exception& e)
  {
    std::cerr << "exception: " << e.what() << "\n";
  }

  return 0;
}
