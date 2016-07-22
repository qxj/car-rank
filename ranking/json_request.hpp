// -*- mode: c++ -*-
//
// Copyright (C) 2016 Julian Qian
//
// @file      json_request.hpp
// @author    Julian Qian <junist@gmail.com>
// @created   2016-04-28 04:19:26
//

#ifndef JSON_REQUEST_HPP_
#define JSON_REQUEST_HPP_

#include <iostream>
#include <string>
#include <tuple>
#include <vector>

namespace ranking
{

struct Query
{
  int price0;
  int price1;
  double lng;
  double lat;

  friend std::ostream& operator<<(std::ostream&, const Query&) ;
  Query& operator<<(const std::string&);
};

struct JsonRequest
{
  std::string algo;
  int user_id;
  bool debug{false};

  Query query;

  RankList cars;

  JsonRequest() : algo("default") {}

  JsonRequest& operator<<(const std::string&) noexcept(false);

};

struct JsonReply
{
  int ret;
  std::string err_msg;

  typedef std::vector<int> CarIds;
  CarIds car_ids;

  typedef std::vector<float> Scores;
  Scores scores;

  JsonReply() : ret(0) {}

  void to_buffer(std::string&);

  void from_request(const JsonRequest& req);
};

}

std::ostream& operator<<(std::ostream&, const ranking::JsonRequest&) ;

#endif // JSON_REQUEST_HPP_
