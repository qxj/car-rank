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
JsonParser::parse_query(const std::string& query_string,
                        Query& query)
{

}

void
JsonParser::parse_request(const std::string& json_string,
        JsonRequest& json_request)
{
  doc_.Parse(json_string);

  if (!doc_.IsObject()) {
    throw std::invalid_argument("post data is invalid, expected json string");
  }

  // algo
  {
    Value::ConstMemberIterator itr = doc_.FindMember("algo");
    if (itr != doc_.MemberEnd()) {
      if (!itr->value.IsString()) {
        throw std::invalid_argument("algo is not a string");
      }
      json_request.algo = itr->value.GetString();
    }
  }
  // query string
  {
    Value::ConstMemberIterator itr = doc_.FindMember("query");
    if (itr != doc_.MemberEnd()) {
      if (!itr->value.IsString()) {
        throw std::invalid_argument("query string is not a string");
      }
      parse_query(itr->value.GetString(), json_request.query);
    }
  }
  // user_id
  {
    Value::ConstMemberIterator itr = doc_.FindMember("user_id");
    if (itr != doc_.MemberEnd()) {
      if (!itr->value.IsInt()) {
        throw std::invalid_argument("user_id is not a integer");
      }
      json_request.user_id = itr->value.GetInt();
    }
  }
  // debug
  {
    Value::ConstMemberIterator itr = doc_.FindMember("debug");
    if (itr != doc_.MemberEnd()) {
      if (!itr->value.IsBool()) {
        throw std::invalid_argument("debug is not a bool");
      }
      json_request.debug = itr->value.GetBool();
    }
  }
  // car_list is required
  if (!doc_.HasMember("car_list")) {
    throw std::invalid_argument("car_list is required");
  }
  const Value& car_ids = doc_["car_list"];
  if (!car_ids.IsArray()) {
    throw std::invalid_argument("car_list is wrong, expect array type");
  }
  size_t car_ids_len = car_ids.Size();
  if (car_ids_len == 0) {
    throw std::invalid_argument("car_list is empty");
  }
  Value::ConstMemberIterator disItr = doc_.FindMember("distance");
  if (disItr != doc_.MemberEnd()) {
    if (!disItr->value.IsArray()) {
      throw std::invalid_argument("distance should be array ");
    } else if (disItr->value.Size() != car_ids_len) {
      throw std::invalid_argument("car_list and distance length are unmatch ");
    }
  }
  Value::ConstMemberIterator priceItr = doc_.FindMember("price");
  if (priceItr != doc_.MemberEnd()) {
    if (!priceItr->value.IsArray()) {
      throw std::invalid_argument("price should be array ");
    } else if (priceItr->value.Size() != car_ids_len) {
      throw std::invalid_argument("car_list and price length are unmatch ");
    }
  }
  auto& cars = json_request.cars;
  // TODO limit cars capacity
  constexpr size_t limit = 500;
  for (SizeType i=0; i < car_ids_len; i++) {
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
      // TODO for debug output
      if (!reply.scores.empty()) {
        Value score_list(kArrayType);
        auto& scores = reply.scores;
        for (auto& s: scores) {
          Value score(s);
          score_list.PushBack(score, allocator);
        }
        o.AddMember("score_list", score_list, allocator);
      }
    }
  }
  StringBuffer buffer;
  Writer<StringBuffer> writer(buffer);
  o.Accept(writer);
  json_string.assign(buffer.GetString());
  return 0;
}
