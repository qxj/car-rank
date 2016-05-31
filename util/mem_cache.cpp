// -*- mode: c++ -*-
//
// Copyright (C) 2016 Julian Qian
//
// @file      mem_cache.cpp
// @author    Julian Qian <junist@gmail.com>
// @created   2016-05-20 18:13:01
//

#include <stdexcept>
#include <string>

#include <glog/logging.h>

#include "mem_cache.hpp"

MemCache::MemCache(const std::string& conf, time_t secs)
    : pool_(nullptr), expired_secs_(secs)
{
  pool_ = memcached_pool(conf.c_str(), conf.size());
  if (!pool_) {
    LOG(WARNING) << "Failed to create memcached pool, conf: " << conf;
  }
}

MemCache::~MemCache()
{
  memcached_pool_destroy(pool_);
}

std::string
MemCache::get(const std::string& key)
{
  memcached_return_t rc;
  memcached_st *mst= memcached_pool_fetch(pool_, NULL, &rc);
  if (!mst) {
    throw std::invalid_argument("memcached pool is null");
  }
  if (!memcached_success(rc)) {
    throw std::runtime_error("failed to fetch from memcached pool when get");
  }

  char* value;
  size_t valen;
  uint32_t flags;
  value = memcached_get(mst, key.data(), key.size(), &valen, &flags, &rc);
  memcached_pool_release(pool_, mst);

  if (memcached_success(rc)) {
    std::string retval{value, valen};
    free(value);
    return retval;
  } else if (rc == MEMCACHED_NOTFOUND) {
    std::string msg{"Not found in memcached, key: "};
    msg.append(key);
    throw std::invalid_argument(msg);
  } else {
    std::string msg{"Failed to get memcached, key: "};
    msg.append(key);
    msg.append(", rc: ");
    msg.append(std::to_string(static_cast<int>(rc)));
    throw std::runtime_error(msg);
  }
}

void
MemCache::set(const std::string& key, const std::string& value)
{
  memcached_return_t rc;
  memcached_st *mst= memcached_pool_fetch(pool_, NULL, &rc);
  if (!mst) {
    throw std::invalid_argument("memcached pool is null");
  }
  if (!memcached_success(rc)) {
    throw std::runtime_error("failed to fetch from memcached pool when set");
  }

  uint32_t flags{0};
  time_t now = time(NULL);
  rc = memcached_set(mst, key.data(), key.size(), value.data(),
          value.size(), now + expired_secs_, flags);
  memcached_pool_release(pool_, mst);

  if (!memcached_success(rc)) {
    std::string msg{"Failed to set memcached, key: "};
    msg.append(key);
    msg.append(", rc: ");
    msg.append(std::to_string(static_cast<int>(rc)));
    throw std::runtime_error(msg);
  }
}
