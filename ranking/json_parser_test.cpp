// -*- mode: c++ -*-
//
// Copyright (C) 2016 Julian Qian
//
// @file      json_parser_test.cpp
// @author    Julian Qian <junist@gmail.com>
// @created   2016-04-23 09:55:03
//

#include <iostream>
#include <gtest/gtest.h>
#include <glog/logging.h>

#include "json_parser.hpp"

namespace
{

class JsonParserTest: public ::testing::Test
{
 protected:
  JsonParserTest() {}
  virtual ~JsonParserTest() {}
  virtual void SetUp()
  {
    // google::InitGoogleLogging("json_parser_test");
  }
 protected:
  ranking::JsonParser parser;
};

TEST_F(JsonParserTest, json_to_request)
{
  std::string json = "{"
      "\"algo\": \"legecy\","
      "\"car_list\": [1, 2, 3, 4],"
      "\"distance\": [0.1,0.2,0.3,0.4],"
      "\"user_id\": 1234}";
  ranking::JsonRequest request;
  int ret = parser.parse_request(json, request);
  EXPECT_EQ(0, ret);
  EXPECT_TRUE(request.algo == "legecy");
  // std::cerr << "Request algo " << request.algo << "\n";
  EXPECT_EQ(1234, request.user_id);
  EXPECT_EQ(4, request.cars.size());
}

TEST_F(JsonParserTest, reply_to_json)
{
  ranking::JsonReply reply;
  reply.ret = -1;
  reply.err_msg = "Unknown Error";
}

}
