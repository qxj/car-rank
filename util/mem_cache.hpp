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

#include <string>

#include <boost/noncopyable.hpp>

#include <libmemcached/memcached.h>

class MemCache : private boost::noncopyable
{
 public:
  explicit MemCache(const std::string&);
  ~MemCache();

  std::string get(const std::string&);
  void set(const std::string&, const std::string&);
 private:
  memcached_pool_st* pool_;
};

#endif // MEM_CACHE_HPP_
