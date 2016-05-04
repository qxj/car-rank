// -*- mode: c++ -*-
//
// Copyright (C) 2016 Julian Qian
//
// @file      util.hpp
// @author    Julian Qian <junist@gmail.com>
// @created   2016-05-03 07:14:23
//

#ifndef UTIL_HPP_
#define UTIL_HPP_

int already_running(const char* lck_file);
void daemonize(const char* chdir = nullptr);

#endif // UTIL_HPP_
