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
  int parse_request(const std::string&, json_request&);
  int reply_string(const json_reply&, std::string&);
 private:
  rapidjson::Document doc_;
};

}

#endif // JSON_PARSER_HPP_
