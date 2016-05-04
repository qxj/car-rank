// -*- mode: c++ -*-
//
// Copyright (C) 2016 Julian Qian
//
// @file      util.cpp
// @author    Julian Qian <junist@gmail.com>
// @created   2016-05-03 07:15:01
//

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sched.h>              // sched_yield
#include <netdb.h>
#include <ifaddrs.h>            // getifaddrs
#include <arpa/inet.h>
#include <sys/socket.h>
#include <sys/stat.h>
#include <sys/file.h>
#include <syslog.h>             // syslog
#include <signal.h>             // signal
#include <sys/ioctl.h>          // ioctl
#include <fcntl.h>
#include <errno.h>              // errno
#include <string.h>             // strerror
#include <time.h>

#include "util.hpp"


int already_running(const char* lck_file)
{
  int fd;
  char buf[16];

  fd = open(lck_file, O_RDWR|O_CREAT, S_IRUSR|S_IWUSR|S_IRGRP|S_IROTH);

  if (fd < 0) {
    syslog(LOG_ERR,"can't open %s: %s", lck_file, strerror(errno));
    return 1;
  }

  struct flock flck;
  flck.l_type = F_WRLCK;
  flck.l_start = 0;
  flck.l_whence = SEEK_SET;
  flck.l_len = 0;

  if (fcntl(fd, F_SETLK, &flck) < 0) {
    if (errno == EACCES || errno == EAGAIN) {
      close(fd);
      return 1;
    }
    syslog(LOG_ERR, "can't lock %s: %s", lck_file, strerror(errno));
    return 1;
  }

  ftruncate(fd, 0);
  sprintf(buf, "%d", getpid());
  write(fd, buf, strlen(buf));
  return 0;
}

void daemonize(const char* dir)
{
  int fd;
  signal(SIGTTOU,SIG_IGN);
  signal(SIGTTIN,SIG_IGN);
  signal(SIGTSTP,SIG_IGN);
  signal(SIGHUP,SIG_IGN);

  if (fork() != 0) { exit(1); }
  if (setsid() < 0) { exit(1); }
  // if ((fd = open("/dev/tty",O_RDWR)) >= 0) {
  //     ioctl(fd, TIOCNOTTY ,NULL);
  //     close(fd);
  // }
  if (fork() != 0) { exit(1); }
  if (dir != nullptr && ::chdir(dir) == -1) { exit(1); }
  for (fd = 0 ; fd < getdtablesize(); ++fd) { close(fd); }
  umask(0);
  signal(SIGCHLD,SIG_IGN);
}
