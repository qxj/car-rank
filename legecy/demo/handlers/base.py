#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; -*-
# @(#) base.py  Time-stamp: <Julian Qian 2015-02-05 16:33:28>
# Copyright 2015 Julian Qian
# Author: Julian Qian <junist@gmail.com>
# Version: $Id: base.py,v 0.1 2015-02-05 10:59:09 jqian Exp $
#

import functools
import json

import tornado.web
from tornado.log import app_log

try:
    import urlparse
except ImportError:
    import urllib.parse as urlparse

try:
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode

from utils.mydb import get_db

class BaseHandler(tornado.web.RequestHandler):
    def initialize(self):
        self.db = get_db('slave')

    def on_finish(self):
        self.db.close()

    def get(self):
        self.redirect("/metrics")

    def prepare(self):
        pass

    def bad_request(self, ret=-1, data='bad request'):
        return self.write(
            {
                'ret': ret,
                'data': data
            }
        )

    def success(self, data='success'):
        return self.write(
            {
                'ret': 0,
                'data': data
            }
        )

    def on_result(self, response):
        self.write(response)
        self.finish()

    def get_current_user(self):
        return None
