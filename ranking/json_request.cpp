// -*- mode: c++ -*-
//
// Copyright (C) 2016 Julian Qian
//
// @file      json_request.cpp
// @author    Julian Qian <junist@gmail.com>
// @created   2016-07-05 19:42:24
//

#include <algorithm>
#include <stdexcept>

#include <glog/logging.h>

#include "rapidjson/document.h"
#include "rapidjson/ostreamwrapper.h"
#include "rapidjson/stringbuffer.h"
#include "rapidjson/writer.h"

#include "data_point.hpp"
#include "feat_idx.hpp"

#include "json_request.hpp"

using namespace rapidjson;
namespace ranking
{

Query&
Query::operator<<(const std::string& s)
{
  return *this;
}

JsonRequest&
JsonRequest::operator<<(const std::string& json_string)
{
  Document doc;
  doc.Parse(json_string);

  if (!doc.IsObject()) {
    throw std::invalid_argument("post data is invalid, expected json string");
  }

  // algo
  {
    Value::ConstMemberIterator itr = doc.FindMember("algo");
    if (itr != doc.MemberEnd()) {
      if (!itr->value.IsString()) {
        throw std::invalid_argument("algo is not a string");
      }
      this->algo = itr->value.GetString();
    }
  }
  // query string
  {
    Value::ConstMemberIterator itr = doc.FindMember("query");
    if (itr != doc.MemberEnd()) {
      if (!itr->value.IsString()) {
        throw std::invalid_argument("query string is not a string");
      }
      this->query << itr->value.GetString();
    }
  }
  // user_id
  {
    Value::ConstMemberIterator itr = doc.FindMember("user_id");
    if (itr != doc.MemberEnd()) {
      if (!itr->value.IsInt()) {
        throw std::invalid_argument("user_id is not a integer");
      }
      this->user_id = itr->value.GetInt();
    }
  }
  // debug
  {
    Value::ConstMemberIterator itr = doc.FindMember("debug");
    if (itr != doc.MemberEnd()) {
      if (!itr->value.IsBool()) {
        throw std::invalid_argument("debug is not a bool");
      }
      this->debug = itr->value.GetBool();
    }
  }
  // car_list is required
  if (!doc.HasMember("car_list")) {
    throw std::invalid_argument("car_list is required");
  }
  const Value& car_ids = doc["car_list"];
  if (!car_ids.IsArray()) {
    throw std::invalid_argument("car_list is wrong, expect array type");
  }
  size_t car_ids_len = car_ids.Size();
  if (car_ids_len == 0) {
    throw std::invalid_argument("car_list is empty");
  }
  Value::ConstMemberIterator disItr = doc.FindMember("distance");
  if (disItr != doc.MemberEnd()) {
    if (!disItr->value.IsArray()) {
      throw std::invalid_argument("distance should be array ");
    } else if (disItr->value.Size() != car_ids_len) {
      throw std::invalid_argument("car_list and distance length are unmatch ");
    }
  }
  Value::ConstMemberIterator priceItr = doc.FindMember("price");
  if (priceItr != doc.MemberEnd()) {
    if (!priceItr->value.IsArray()) {
      throw std::invalid_argument("price should be array ");
    } else if (priceItr->value.Size() != car_ids_len) {
      throw std::invalid_argument("car_list and price length are unmatch ");
    }
  }
  auto& cars = this->cars;
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
    if (disItr != doc.MemberEnd()) {
      if (disItr->value[i].IsNumber()) {
        distance = static_cast<float>(disItr->value[i].GetDouble());
      } else {
        throw std::invalid_argument("distance is invalid, expect float type");
      }
    }
    float price = 0;
    if (priceItr != doc.MemberEnd()) {
      if (priceItr->value[i].IsNumber()) {
        distance = static_cast<float>(priceItr->value[i].GetDouble());
      } else {
        throw std::invalid_argument("price is invalid, expect float type");
      }
    }
    cars.emplace_back(car_id);
    auto& car = cars.back();
    car.set(feat_idx::DISTANCE, distance);
    car.set(feat_idx::PRICE, price);
  }

  // NOTE convenient to fetch data from db
  std::sort(cars.begin(), cars.end(),
            [](const DataPoint& a, const DataPoint& b) {
              return a.id < b.id;
            });
  return *this;
}

void
JsonReply::to_buffer(std::string& output)
{
  Document doc;
  Document::AllocatorType& alloc = doc.GetAllocator();
  // NOTE if re-use Document(doc) instead of Value(a), core dump when concurrent requests.
  Value o(kObjectType);
  {
    Value ret(this->ret);
    o.AddMember("ret", ret, alloc);
    if (this->ret) {  // error message
      Value err_msg;
      err_msg.SetString(this->err_msg, alloc);
      o.AddMember("err_msg", err_msg, alloc);
    } else {
      Value car_list(kArrayType);
      auto& car_ids = this->car_ids;
      for (auto itr=car_ids.cbegin(); itr!=car_ids.cend(); itr++) {
        Value car_id(*itr);
        car_list.PushBack(car_id, alloc);
      }
      o.AddMember("car_list", car_list, alloc);
      // TODO for debug output
      if (!this->scores.empty()) {
        Value score_list(kArrayType);
        auto& scores = this->scores;
        for (auto& s: scores) {
          Value score(s);
          score_list.PushBack(score, alloc);
        }
        o.AddMember("score_list", score_list, alloc);
      }
    }
  }
  StringBuffer buffer;
  Writer<StringBuffer> writer(buffer);
  o.Accept(writer);
  output.assign(buffer.GetString());
}

void
JsonReply::from_request(const JsonRequest& req)
{
  for (const auto& car: req.cars) {
    car_ids.push_back(car.id);
  }
}

}

std::ostream& operator<<(std::ostream& os, const ranking::JsonRequest& jr)
{
  os << "[JsonRequest] algo " << jr.algo
     << ", user_id " << jr.user_id
     << ", cars num " << jr.cars.size();
  return os;
}

std::ostream& operator<<(std::ostream& os, const ranking::JsonReply& jr)
{
  os << "[JsonReply] ";
  if (jr.ret) {  // error
    os << "return error " << jr.ret
       << ",  " << jr.err_msg;
  } else {
    os << "reply sorted " << jr.car_ids.size() << " cars";
  }
  return os;
}
