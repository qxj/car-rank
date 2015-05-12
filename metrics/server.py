#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; -*-
# @(#) server.py  Time-stamp: <Julian Qian 2015-02-05 10:31:17>
# Copyright 2015 Julian Qian
# Author: Julian Qian <junist@gmail.com>
# Version: $Id: server.py,v 0.1 2015-02-05 10:31:09 jqian Exp $
#

import sys
import argparse

import tornado.ioloop
import tornado.web
from tornado.options import parse_config_file

from application import Application

def main():
    parser = argparse.ArgumentParser(description="pdw service")
    parser.add_argument('-p', '--port', type=int, default=8080, help="service port")
    parser.add_argument('-c', '--conf', default='./server.conf',
                        help="service config file")
    args = parser.parse_args()

    parse_config_file(args.conf)
    application = Application()
    application.listen(args.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    reload(sys)
    sys.setdefaultencoding('utf-8')
    main()
