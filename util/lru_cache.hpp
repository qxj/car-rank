// -*- mode: c++ -*-
//
// Copyright (C) 2016 Julian Qian
//
// @file      lru_cache.hpp
// @author    Julian Qian <junist@gmail.com>
// @created   2016-05-06 12:14:47
//

#ifndef LRU_CACHE_HPP_
#define LRU_CACHE_HPP_

#if __cplusplus <= 199711L
  #error This library needs at least a C++11 compliant compiler
#endif

#include <cassert>
#include <unordered_map>
#include <list>
#include <stdexcept>

#include <boost/thread/locks.hpp>  // for thread-safe
#include <boost/thread/shared_mutex.hpp>

// load & dump
// #include <fstream>
// #include <string>
// #include <vector>
// #include <boost/algorithm/string.hpp>

// Class providing fixed-size (by number of records) LRU-replacement cache
//
template <typename K, typename V>
class LruCache
{
 public:
  typedef K key_type;
  typedef V value_type;

  typedef std::list<key_type> key_tracker_type;

  typedef std::unordered_map<
    key_type,
    std::pair<value_type, typename key_tracker_type::iterator>
    > key_to_value_type;

  explicit LruCache(size_t c) : capacity_(c)
  {
    assert(capacity_!=0);
  }

  void set(const key_type& k, const value_type& v)
  {
    const typename key_to_value_type::iterator it = key_to_value_.find(k);

    if (it == key_to_value_.end()) {
      insert(k, v);
    } else {
      key_tracker_.splice(key_tracker_.end(),
              key_tracker_,
              (*it).second.second);
      (*it).second.first = v;
    }
  }

  value_type get(const key_type& k)
  {
    boost::upgrade_lock< boost::shared_mutex > lock(mutex_);

    const typename key_to_value_type::iterator it = key_to_value_.find(k);

    if (it == key_to_value_.end()) {
      throw std::invalid_argument("get key miss");
    } else {
      boost::upgrade_to_unique_lock< boost::shared_mutex > uniqueLock(mutex_);

      key_tracker_.splice(key_tracker_.end(),
              key_tracker_,
              (*it).second.second);
      return (*it).second.first;
    }
  }

#if 0
  void load(const char* filename)
  {
    std::ifstream ifs(filename);
    std::string line;
    std::vector<std::string> cols;
    while(getline(ifs, line)){
      boost::split(cols, line, boost::is_any_of("\t "),
                   boost::token_compress_on);
      key_type k = load_key(cols[0]);
      value_type v = load_value(cols[1]);
      set(k, v);

    }

  }
  void dump(const char* filename)
  {
    std::ofstream ofs(filename, std::ofstream::out);
    for (container_type::const_iterator itr = container_.begin();
         itr != container_.end(); ++itr) {
      ofs << dump_key(itr->left) << "\t" << dump_value(get(itr->left)) << "\n";

    }

  }
#endif

 private:
  void insert(const key_type& k, const value_type& v)
  {
    assert(key_to_value_.find(k)==key_to_value_.end());

    if (key_to_value_.size() == capacity_) evict();

    typename key_tracker_type::iterator it
        = key_tracker_.insert(key_tracker_.end(), k);
    key_to_value_.insert(std::make_pair(k,
            std::make_pair(v,it)));
  }

  void evict()
  {
    assert(!key_tracker_.empty());

    const typename key_to_value_type::iterator it
        = key_to_value_.find(key_tracker_.front());

    assert(it!=key_to_value_.end());

    key_to_value_.erase(it);
    key_tracker_.pop_front();
  }

  size_t capacity_;

  key_tracker_type key_tracker_;
  key_to_value_type key_to_value_;

  boost::shared_mutex mutex_;
};

#endif // LRU_CACHE_HPP_
