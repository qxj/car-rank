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

#include <vector>
#include <string>

namespace ranking {

struct CarInfo
{
  int car_id;
  float distance;
  float price;

  CarInfo(int car_id, float distance=0, float price=0)
      : car_id(car_id) , distance(distance), price(price) {}
};

struct JsonRequest
{
  std::string algo;
  int user_id;
  std::vector<CarInfo> car_list;

  JsonRequest() : algo("default") {}
};

struct JsonReply
{
  int ret;
  std::string err_msg;
  std::vector<int> car_id_list;

  JsonReply() : ret(0) {}
};

}

#endif // JSON_REQUEST_HPP_
