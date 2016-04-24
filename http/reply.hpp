//
// reply.hpp
// ~~~~~~~~~
//
// Copyright (c) 2003-2013, 2016 Christopher M. Kohlhoff (chris at kohlhoff dot com)
//
// Distributed under the Boost Software License, Version 1.0. (See accompanying
// file LICENSE_1_0.txt or copy at http://www.boost.org/LICENSE_1_0.txt)
//

#ifndef HTTP_REPLY_HPP
#define HTTP_REPLY_HPP

#include <string>
#include <vector>
#include <boost/asio.hpp>

#include "header.hpp"

namespace http {
namespace server {

/// A reply to be sent to a client.
struct reply
{

  /// The status of the reply.
  enum status_type
  {
    ok = 200,
    created = 201,
    accepted = 202,
    no_content = 204,
    multiple_choices = 300,
    moved_permanently = 301,
    moved_temporarily = 302,
    not_modified = 304,
    bad_request = 400,
    unauthorized = 401,
    forbidden = 403,
    not_found = 404,
    internal_server_error = 500,
    not_implemented = 501,
    bad_gateway = 502,
    service_unavailable = 503
  } status;

  /// The headers to be included in the reply.
  std::vector<header> headers;

  /// The content to be sent in the reply.
  std::string content;

  reply() : status(reply::ok) {}

  // helper functions
  void add_content(const std::string& cont)
  {
    content = cont;
  }

  void add_header(const std::string& name, const std::string& value)
  {
    headers.emplace_back(name, value);
  }

  void add_content_length()
  {
    add_header("Content-Length", std::to_string(content.size()));
  }

  void add_content_type(const std::string& type)
  {
    add_header("Content-Type", type);
  }

  /// Convert the reply into a vector of buffers. The buffers do not own the
  /// underlying memory blocks, therefore the reply object must remain valid and
  /// not be changed until the write operation has completed.
  std::vector<boost::asio::const_buffer> to_buffers();

  /// Get a stock reply.
  static reply stock_reply(status_type status);
};

} // namespace server
} // namespace http

#endif // HTTP_REPLY_HPP
