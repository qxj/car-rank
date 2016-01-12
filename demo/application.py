#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; -*-
# @(#) application.py  Time-stamp: <Julian Qian 2015-02-07 11:29:19>
# Copyright 2015 Julian Qian
# Author: Julian Qian <junist@gmail.com>
# Version: $Id: application.py,v 0.1 2015-02-05 10:31:25 jqian Exp $
#

import os

import tornado.web
from tornado.options import define, options

from handlers import *

define('debug', default=True, type=bool)


class Application(tornado.web.Application):
    def __init__(self):
        settings = {
            #"static_path": os.path.join(os.path.dirname(__file__), "static"),
            "wiki_path": os.path.join(os.path.dirname(__file__), "wiki"),
            "template_path": os.path.join(os.path.dirname(__file__), "templates"),
            "cookie_secret": "zTXKAQaGYkd5LgmEGJeJYFu7hEnQpX2dPTo1oVE/16o=",
            "login_url": "/login",
            "xsrf_cookies": True,
        }
        static_path= os.path.join(os.path.dirname(__file__), "static")
        if options.debug:
            settings.update({
                "debug": True,
                "autoreload": True,
                "compiled_template_cache": False,
                "static_hash_cache": False,
                "serve_traceback": True,
            })
            options.logging = 'debug'  # tornado   logger

        handlers = [
            # (r"/?", base.BaseHandler),
            (r"/metrics", metrics.MetricsHandler),
            (r"/(favicon\.ico)", tornado.web.StaticFileHandler, {'path': static_path}),
            (r"/static/(.*)", tornado.web.StaticFileHandler, {'path': static_path}),
        ]
        tornado.web.Application.__init__(self, handlers, **settings)
