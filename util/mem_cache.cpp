// -*- mode: c++ -*-
//
// Copyright (C) 2016 Julian Qian
//
// @file      mem_cache.cpp
// @author    Julian Qian <junist@gmail.com>
// @created   2016-05-20 18:13:01
//

#include "mem_cache.hpp"

MemCache::MemCache(const std::string& conf)
{
  pool_ = memcached_pool(conf.c_str(), conf.size());
}

~MemCache::MemCache()
{
  memcached_pool_destroy(pool_);
}
