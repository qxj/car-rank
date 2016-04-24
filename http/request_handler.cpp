//
// request_handler.cpp
// ~~~~~~~~~~~~~~~~~~~
//
// Copyright (c) 2003-2013, 2016 Christopher M. Kohlhoff (chris at kohlhoff dot com)
//
// Distributed under the Boost Software License, Version 1.0. (See accompanying
// file LICENSE_1_0.txt or copy at http://www.boost.org/LICENSE_1_0.txt)
//

#include <fstream>
#include <sstream>

#include <glog/logging.h>

// #include "reply.hpp"
// #include "request.hpp"

#include "request_handler.hpp"

namespace http {
namespace server {


void request_handler::handle_request(const request& req, reply& rep)
{
  // Decode url to path.
  std::string request_path;
  if (!url_decode(req.uri, request_path))
  {
    LOG(ERROR) << "Failed to decode url " << req.uri;
    rep = reply::stock_reply(reply::bad_request);
    return;
  }

  // Request path must be absolute and not contain "..".
  if (request_path.empty() || request_path[0] != '/'
      || request_path.find("..") != std::string::npos)
  {
    LOG(ERROR) << "Request path must be absolute and not contain .." << req.uri;
    rep = reply::stock_reply(reply::bad_request);
    return;
  }

  // VLOG(100) << "request content " << req.content;

  RouteType::const_iterator itr = route_.find(request_path);
  if (itr != route_.end()) {
    (itr->second)(req, rep);
    rep.add_content_length();
  } else {
    VLOG(100) << "unknown route path " << request_path;
    rep = reply::stock_reply(reply::not_found);
  }
}

bool request_handler::url_decode(const std::string& in, std::string& out)
{
  out.clear();
  out.reserve(in.size());
  for (std::size_t i = 0; i < in.size(); ++i)
  {
    if (in[i] == '%')
    {
      if (i + 3 <= in.size())
      {
        int value = 0;
        std::istringstream is(in.substr(i + 1, 2));
        if (is >> std::hex >> value)
        {
          out += static_cast<char>(value);
          i += 2;
        }
        else
        {
          return false;
        }
      }
      else
      {
        return false;
      }
    }
    else if (in[i] == '+')
    {
      out += ' ';
    }
    else
    {
      out += in[i];
    }
  }
  return true;
}

} // namespace server
} // namespace http
