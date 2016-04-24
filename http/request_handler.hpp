//
// request_handler.hpp
// ~~~~~~~~~~~~~~~~~~~
//
// Copyright (c) 2003-2013, 2016 Christopher M. Kohlhoff (chris at kohlhoff dot com)
//
// Distributed under the Boost Software License, Version 1.0. (See accompanying
// file LICENSE_1_0.txt or copy at http://www.boost.org/LICENSE_1_0.txt)
//

#ifndef HTTP_REQUEST_HANDLER_HPP
#define HTTP_REQUEST_HANDLER_HPP

#include <functional>
#include <map>
#include <string>

#include "reply.hpp"
#include "request.hpp"

namespace http {
namespace server {

// struct reply;
// struct request;

typedef std::function<void(const request&, reply&)> HandlerFunc;

/// The common handler for all incoming requests.
class request_handler
{
public:
  request_handler() = default;
  // request_handler(const request_handler&) = delete;
  // request_handler& operator=(const request_handler&) = delete;

  /// Handle a request and produce a reply.
  void handle_request(const request& req, reply& rep);

  /// process request and output reply
  // TODO support regexp handler
  void add_handler(const std::string& path, HandlerFunc handler)
  {
    route_[path] = handler;
  }

private:

  /// Perform URL-decoding on a string. Returns false if the encoding was
  /// invalid.
  static bool url_decode(const std::string& in, std::string& out);

  typedef std::map<std::string, HandlerFunc> RouteType;

  /// route map
  RouteType route_;
};


} // namespace server
} // namespace http

#endif // HTTP_REQUEST_HANDLER_HPP
