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

#include <boost/lexical_cast.hpp>
#include <glog/logging.h>

#include <string>
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
  std::string body;

  size_t content_length() {
    if (!content_length_) {
      for (auto h: headers) {
        if (h.name == "content-length") {
          VLOG(100) << "content length: " << h.value ;
          try {
            content_length_ = boost::lexical_cast<int>(h.value);
          } catch (const boost::bad_lexical_cast& ) {
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
