// -*- mode: c++ -*-
//
// Copyright (C) 2016 Julian Qian
//
// @file      json_parser.hpp
// @author    Julian Qian <junist@gmail.com>
// @created   2016-04-28 04:18:10
//

#ifndef JSON_PARSER_HPP_
#define JSON_PARSER_HPP_

#include <string>

#include "rapidjson/document.h"

#include "json_request.hpp"

namespace ranking
{

class JsonParser
{
 public:
  void parse_request(const std::string&, JsonRequest&) noexcept(false);
  int reply_string(const JsonReply&, std::string&);
 private:
  void parse_query(const std::string&, Query&) noexcept(false);
 private:
  rapidjson::Document doc_;
};

}

#endif // JSON_PARSER_HPP_
