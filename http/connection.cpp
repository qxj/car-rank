//
// connection.cpp
// ~~~~~~~~~~~~~~
//
// Copyright (c) 2003-2013, 2016 Christopher M. Kohlhoff (chris at kohlhoff dot com)
//
// Distributed under the Boost Software License, Version 1.0. (See accompanying
// file LICENSE_1_0.txt or copy at http://www.boost.org/LICENSE_1_0.txt)
//

#include <utility>
#include <vector>
#include <glog/logging.h>

#include "request_handler.hpp"

#include "connection.hpp"

namespace http {
namespace server {

connection::connection(boost::asio::io_service& io_service,
        request_handler& handler)
  : socket_(io_service),
    request_handler_(handler)
{
}

void connection::start()
{
  do_read();
}

void connection::stop()
{
  socket_.close();
}

void connection::do_read()
{
  auto self(shared_from_this());
  socket_.async_read_some(boost::asio::buffer(buffer_),
      [this, self](boost::system::error_code ec, std::size_t bytes_transferred)
      {
        if (!ec)
        {
          request_parser::result_type result;
          std::tie(result, std::ignore) = request_parser_.parse(
              request_, buffer_.data(), buffer_.data() + bytes_transferred);

          VLOG(100) << "async read " << bytes_transferred << " bytes from " << socket_.remote_endpoint();

          if (result == request_parser::good)
          {
            request_handler_.handle_request(request_, reply_);
            do_write();
          }
          else if (result == request_parser::bad)
          {
            LOG(ERROR) << "failed to parse request, from " << socket_.remote_endpoint();
            reply_ = reply::stock_reply(reply::bad_request);
            do_write();
          }
          else
          {
            do_read();
          }
        } else {
          LOG(ERROR) << "failed to get request: " << ec.message();
        }
        // else if (ec != boost::asio::error::operation_aborted)
        // {
        //   connection_manager_.stop(shared_from_this());
        // }
      });
}

void connection::do_write()
{
  auto self(shared_from_this());
  boost::asio::async_write(socket_, reply_.to_buffers(),
      [this, self](boost::system::error_code ec, std::size_t bytes_transferred)
      {
        if (!ec)
        {
          VLOG(100) << "replied " << bytes_transferred << " bytes.";
          // Initiate graceful connection closure.
          boost::system::error_code ignored_ec;
          socket_.shutdown(boost::asio::ip::tcp::socket::shutdown_both,
                  ignored_ec);
        } else {
          LOG(ERROR) << "async_write failed: " << ec.message();
        }

        // if (ec != boost::asio::error::operation_aborted)
        // {
        //   connection_manager_.stop(shared_from_this());
        // }
      });
}

} // namespace server
} // namespace http
