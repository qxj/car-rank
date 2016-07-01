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

#include <sstream>
#include <string>
#include <tuple>
#include <vector>

namespace ranking {

struct CarInfo
{
  int car_id;
  float distance;
  int price;

  // to be fetched from db
  // 1) car quality score
  float quality{0};
  // 2) user preference
  char is_ordered   : 1;
  char is_collected : 1;
  char is_model     : 1;
  char is_price     : 1;

  float score{0};

  CarInfo(int car_id, float distance=0, float price=0)
      : car_id(car_id) , distance(distance), price(price),
        is_ordered(0), is_collected(0), is_model(0), is_price(0)
  {}

  std::tuple<float, float, float> trans_distance() const {
    float d1{0}, d2{0}, d3{0};
    if (distance < 2) {
      d1 = 1;
    } else if (distance < 5) {
      d2 = 1;
    } else if (distance < 20) {
      d3 = 1 - distance / 20;
    }
    return std::make_tuple(d1, d2, d3);
  }
};

struct Query
{
  int price0;
  int price1;
  double lng;
  double lat;
};

struct JsonRequest
{
  std::string algo;
  int user_id;
  bool debug{false};

  Query query;

  typedef std::vector<CarInfo> CarsType;
  CarsType cars;

  JsonRequest() : algo("default") {}

  std::string to_string() const {
    std::ostringstream oss;
    oss << "[JsonRequest] algo " << algo
        << ", user_id " << user_id
        << ", cars num " << cars.size();
    return oss.str();
  }
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

  void from_request(const JsonRequest& req) {
    for (const auto& car: req.cars) {
      car_ids.push_back(car.car_id);
    }
  }
};

}

#endif // JSON_REQUEST_HPP_
