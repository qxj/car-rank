//
// request.hpp
// ~~~~~~~~~~~
//
// Copyright (c) 2003-2013, 2016 Christopher M. Kohlhoff (chris at kohlhoff dot com)
//
// Distributed under the Boost Software License, Version 1.0. (See accompanying
// file LICENSE_1_0.txt or copy at http://www.boost.org/LICENSE_1_0.txt)
//

#ifndef HTTP_REQUEST_HPP
#define HTTP_REQUEST_HPP

#include <string>
#include <system_error>
#include <vector>

#include "header.hpp"

namespace http {
namespace server {

/// A request received from a client.
struct request
{
  std::string method;
  std::string uri;
  int http_version_major;
  int http_version_minor;
  std::vector<header> headers;
  std::string content;

  size_t content_length() {
    if (!content_length_) {
      for (auto h: headers) {
        if (h.name == "content-length") {
          try {
            content_length_ = std::stoi(h.value);
          } catch (const std::invalid_argument& ) {
            content_length_ = -1;
          }
          break;
        }
      }
    }
    return content_length_;
  }
 private:
  size_t content_length_ = 0;
};

} // namespace server
} // namespace http

#endif // HTTP_REQUEST_HPP
