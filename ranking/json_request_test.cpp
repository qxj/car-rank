// -*- mode: c++ -*-
//
// Copyright (C) 2016 Julian Qian
//
// @file      json_request_test.cpp
// @author    Julian Qian <junist@gmail.com>
// @created   2016-07-05 20:26:58
//

#include <iostream>
#include <gtest/gtest.h>
#include <glog/logging.h>

#include "data_point.hpp"
#include "json_request.hpp"

namespace
{

class JsonRequestTest: public ::testing::Test
{
 protected:
  JsonRequestTest() {}
  virtual ~JsonRequestTest() {}
  virtual void SetUp()
  {
    // google::InitGoogleLogging("json_parser_test");
  }
};

TEST_F(JsonRequestTest, json_to_request)
{
  std::string json = "{"
      "\"algo\": \"legacy\","
      "\"car_list\": [1, 2, 3, 4],"
      "\"distance\": [0.1,0.2,0.3,0.4],"
      "\"user_id\": 1234}";
  ranking::JsonRequest request;

  request << json;

  // TODO catch exception
  EXPECT_TRUE(request.algo == "legacy");
  // std::cerr << "Request algo " << request.algo << "\n";
  EXPECT_EQ(1234, request.user_id);
  EXPECT_EQ(4, request.cars.size());
}

TEST_F(JsonRequestTest, reply_to_json)
{
  ranking::JsonReply reply;
  reply.ret = -1;
  reply.err_msg = "Unknown Error";
}

}
