// -*- mode: c++ -*-
//
// Copyright (C) 2016 Julian Qian
//
// @file      json_parser.cpp
// @author    Julian Qian <junist@gmail.com>
// @created   2016-04-28 04:20:38
//

#include <stdexcept>

#include <glog/logging.h>

#include "rapidjson/document.h"
#include "rapidjson/stringbuffer.h"
#include "rapidjson/writer.h"

#include "json_parser.hpp"

using namespace rapidjson;
using namespace ranking;

void
JsonParser::parse_request(const std::string& json_string,
        JsonRequest& json_request)
{
  doc_.Parse(json_string);

  if (!doc_.IsObject()) {
    throw std::invalid_argument("post data is invalid, expected json string");
  }

  // algo
  Value::ConstMemberIterator aitr = doc_.FindMember("algo");
  if (aitr != doc_.MemberEnd()) {
    if (!aitr->value.IsString()) {
      throw std::invalid_argument("algo is not a string");
    }
    json_request.algo = aitr->value.GetString();
  }
  // user_id
  Value::ConstMemberIterator uitr = doc_.FindMember("user_id");
  if (uitr != doc_.MemberEnd()) {
    if (!uitr->value.IsInt()) {
      throw std::invalid_argument("user_id is not a integer");
    }
    json_request.user_id = uitr->value.GetInt();
  }
  // car_id list
  if (!doc_.HasMember("car_list")) {
    throw std::invalid_argument("car_list is required");
  }
  const Value& car_ids = doc_["car_list"];
  if (!car_ids.IsArray()) {
    throw std::invalid_argument("car_list is wrong, expect array type");
  }
  size_t car_ids_len = car_ids.Size();
  if (car_ids.Size() == 0) {
    throw std::invalid_argument("car_list is empty");
  }
  Value::ConstMemberIterator disItr = doc_.FindMember("distance");
  if (disItr != doc_.MemberEnd() && disItr->value.Size() != car_ids_len) {
    throw std::invalid_argument("car_list and distance length are unmatch ");
  }
  Value::ConstMemberIterator priceItr = doc_.FindMember("price");
  if (priceItr != doc_.MemberEnd() && priceItr->value.Size() != car_ids_len) {
    throw std::invalid_argument("car_list and price length are unmatch ");
  }
  auto& cars = json_request.cars;
  // TODO limit cars capacity
  constexpr size_t limit = 500;
  for (SizeType i=0; i < car_ids.Size(); i++) {
    int car_id = 0;
    if (car_ids[i].IsInt()) {
     car_id = car_ids[i].GetInt();
    } else {
      throw std::invalid_argument("car_id is invalid, expect integer type");
    }

    float distance = 0;
    if (disItr != doc_.MemberEnd()) {
      if (disItr->value[i].IsNumber()) {
        distance = static_cast<float>(disItr->value[i].GetDouble());
      } else {
        throw std::invalid_argument("distance is invalid, expect float type");
      }
    }
    float price = 0;
    if (priceItr != doc_.MemberEnd()) {
      if (priceItr->value[i].IsNumber()) {
        distance = static_cast<float>(priceItr->value[i].GetDouble());
      } else {
        throw std::invalid_argument("price is invalid, expect float type");
      }
    }
    cars.emplace_back(car_id, distance, price);
  }
}

int
JsonParser::reply_string(const JsonReply& reply, std::string& json_string)
{
  Document::AllocatorType& allocator = doc_.GetAllocator();
  Value o(kObjectType);
  {
    Value ret(reply.ret);
    o.AddMember("ret", ret, allocator);
    if (reply.ret) {  // error message
      Value err_msg;
      err_msg.SetString(reply.err_msg, allocator);
      o.AddMember("err_msg", err_msg, allocator);
    } else {
      Value car_list(kArrayType);
      auto& car_ids = reply.car_ids;
      for (auto itr=car_ids.cbegin(); itr!=car_ids.cend(); itr++) {
        Value car_id(*itr);
        car_list.PushBack(car_id, allocator);
      }
      o.AddMember("car_list", car_list, allocator);
    }
  }
  StringBuffer buffer;
  Writer<StringBuffer> writer(buffer);
  o.Accept(writer);
  json_string.assign(buffer.GetString());
  return 0;
}
