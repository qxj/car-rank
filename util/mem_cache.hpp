// -*- mode: c++ -*-
//
// Copyright (C) 2016 Julian Qian
//
// @file      mem_cache.hpp
// @author    Julian Qian <junist@gmail.com>
// @created   2016-05-20 16:54:38
//

#ifndef MEM_CACHE_HPP_
#define MEM_CACHE_HPP_

#include <time.h>
#include <string>

#include <boost/noncopyable.hpp>

#include <libmemcached/memcached.h>
#include <libmemcachedutil-1.0/pool.h>

class MemCache : private boost::noncopyable
{
 public:
  explicit MemCache(const std::string&, time_t e = 600);
  ~MemCache();

  std::string get(const std::string&) noexcept(false);
  void set(const std::string&, const std::string&) noexcept(false);
 private:
  memcached_pool_st* pool_;
  time_t expired_secs_;
};

#endif // MEM_CACHE_HPP_
