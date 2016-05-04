//
// server.hpp
// ~~~~~~~~~~
//
// Copyright (c) 2003-2013, 2016 Christopher M. Kohlhoff (chris at kohlhoff dot com)
//
// Distributed under the Boost Software License, Version 1.0. (See accompanying
// file LICENSE_1_0.txt or copy at http://www.boost.org/LICENSE_1_0.txt)
//

#ifndef HTTP_SERVER_HPP
#define HTTP_SERVER_HPP

#include <boost/asio.hpp>
#include <boost/noncopyable.hpp>
#include <string>
#include "connection.hpp"
// #include "connection_manager.hpp"
#include "io_service_pool.hpp"
#include "request_handler.hpp"

namespace http {
namespace server {

/// The top-level class of the HTTP server.
class server : private boost::noncopyable
{
public:
  /// Construct the server to listen on the specified TCP address and port, and
  /// serve up files from the given directory.
  server(const std::string& address, short port, std::size_t io_service_pool_size=2);
  virtual ~server() = default;

  void add_handler(const std::string& path, HandlerFunc handler)
  {
    request_handler_.add_handler(path, handler);
  }

  /// Run the server's io_service loop.
  void run();

private:
  /// Perform an asynchronous accept operation.
  void do_accept();

  /// Wait for a request to stop the server.
  void do_await_stop();

  /// The pool of io_service objects used to perform asynchronous operations.
  io_service_pool io_service_pool_;

  /// The io_service used to perform asynchronous operations.
  // boost::asio::io_service io_service_;

  /// The signal_set is used to register for process termination notifications.
  boost::asio::signal_set signals_;

  /// Acceptor used to listen for incoming connections.
  boost::asio::ip::tcp::acceptor acceptor_;

  /// The next connection to be accepted.
  connection_ptr new_connection_;

  /// The connection manager which owns all live connections.
  // connection_manager connection_manager_;

  /// The handler for all incoming requests.
  request_handler request_handler_;

};

} // namespace server
} // namespace http

#endif // HTTP_SERVER_HPP
