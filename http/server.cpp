//
// server.cpp
// ~~~~~~~~~~
//
// Copyright (c) 2003-2013, 2016 Christopher M. Kohlhoff (chris at kohlhoff dot com)
//
// Distributed under the Boost Software License, Version 1.0. (See accompanying
// file LICENSE_1_0.txt or copy at http://www.boost.org/LICENSE_1_0.txt)
//

#include <signal.h>
#include <utility>
#include <glog/logging.h>

#include "server.hpp"

namespace http {
namespace server {

server::server(const std::string& address, short port, std::size_t io_service_pool_size)
  : io_service_pool_(io_service_pool_size),
    signals_(io_service_pool_.get_io_service()),
    acceptor_(io_service_pool_.get_io_service()),
    request_handler_()
{
  // Register to handle the signals that indicate when the server should exit.
  // It is safe to register for the same signal multiple times in a program,
  // provided all registration for the specified signal is made through Asio.
  signals_.add(SIGINT);
  signals_.add(SIGTERM);
#if defined(SIGQUIT)
  signals_.add(SIGQUIT);
#endif // defined(SIGQUIT)

  do_await_stop();

  // Open the acceptor with the option to reuse the address (i.e. SO_REUSEADDR).
  boost::asio::ip::tcp::endpoint endpoint(
      boost::asio::ip::address::from_string(address), port);
  acceptor_.open(endpoint.protocol());
  acceptor_.set_option(boost::asio::ip::tcp::acceptor::reuse_address(true));
  acceptor_.bind(endpoint);
  acceptor_.listen();

  do_accept();
}

void server::run()
{
  // The io_service::run() call will block until all asynchronous operations
  // have finished. While the server is running, there is always at least one
  // asynchronous operation outstanding: the asynchronous accept call waiting
  // for new incoming connections.
  io_service_pool_.run();
}

void server::do_accept()
{
  /// The next connection to be accepted.
  new_connection_.reset(new connection(
      io_service_pool_.get_io_service(), request_handler_));

  acceptor_.async_accept(new_connection_->socket(),
          [this](boost::system::error_code ec)
      {
        // Check whether the server was stopped by a signal before this
        // completion handler had a chance to run.
        if (!acceptor_.is_open())
        {
          return;
        }

        if (!ec)
        {
          VLOG(100) << "new connection " << new_connection_->socket().remote_endpoint();
          // connection_manager_.start(new_connection_);
          new_connection_->start();
        }

        do_accept();
      });
}

void server::do_await_stop()
{
  signals_.async_wait(
      [this](boost::system::error_code /*ec*/, int /*signo*/)
      {
        // acceptor_.close();
        io_service_pool_.stop();
        // The server is stopped by cancelling all outstanding asynchronous
        // operations. Once all operations have finished the io_service::run()
        // call will exit.
        // connection_manager_.stop_all();
      });
}

} // namespace server
} // namespace http
