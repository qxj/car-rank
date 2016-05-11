// -*- mode: c++ -*-
//
// Copyright (C) 2016 Julian Qian
//
// @file      json_parser.cpp
// @author    Julian Qian <junist@gmail.com>
// @created   2016-04-28 04:20:38
//

#include <glog/logging.h>

#include "rapidjson/document.h"
#include "rapidjson/stringbuffer.h"
#include "rapidjson/writer.h"

#include "json_parser.hpp"

using namespace rapidjson;
using namespace ranking;

int
JsonParser::parse_request(const std::string& json_string,
        JsonRequest& json_request)
{
  doc_.Parse(json_string);

  if (!doc_.HasMember("car_list")) {
    VLOG(100) << "car_list is required, abort parser";
    return -1;
  }

  // algo
  Value::ConstMemberIterator aitr = doc_.FindMember("algo");
  if (aitr != doc_.MemberEnd()) {
    if (!aitr->value.IsString()) {
      VLOG(ERROR) << "algo is not a string";
      return -1;
    }
    json_request.algo = aitr->value.GetString();
  }
  // user_id
  Value::ConstMemberIterator uitr = doc_.FindMember("user_id");
  if (uitr != doc_.MemberEnd()) {
    if (!uitr->value.IsInt()) {
      VLOG(ERROR) << "user_id is not a integer";
      return -1;
    }
    json_request.user_id = uitr->value.GetInt();
  }
  // car_id list
  const Value& car_ids = doc_["car_list"];
  if (car_ids.Size() == 0) {
    VLOG(100) << "car_list is empty, abort parser";
    return -1;
  }
  Value::ConstMemberIterator itr1 = doc_.FindMember("distance");
  Value::ConstMemberIterator itr2 = doc_.FindMember("price");
  auto& cars = json_request.cars;
  // TODO limit cars capacity
  constexpr size_t limit = 500;
  for (SizeType i=0; i < car_ids.Size(); i++) {
    float distance = (itr1 != doc_.MemberEnd()) ? static_cast<float>(itr1->value[i].GetDouble()) : 0;
    int price = (itr2 != doc_.MemberEnd()) ? itr2->value[i].GetInt() : 0;
    int car_id = car_ids[i].GetInt();
    cars.emplace_back(car_id, distance, price);
  }
  return 0;
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
