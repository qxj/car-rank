#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; -*-
#
# Copyright (C) 2016 Julian Qian
#
# @file      press_test.py
# @author    Julian Qian <junist@gmail.com>
# @created   2016-05-23 11:20:55
#

import argparse
import httplib
import urlparse
import json
import random
import threading
from timeit import default_timer as timer


class PressTest(threading.Thread):

    def __init__(self, url, cnt=1000):
        super(PressTest, self).__init__()
        self.url = url
        self.data = self.get_data(random.randint(100, 500))
        self.cnt = cnt

    def get_data(self, n):
        car_list = range(n)
        random.shuffle(car_list)
        pre_dis = range(n)
        random.shuffle(pre_dis)
        self.data = {
            "algo": "legacy",
            "car_list": car_list,
            "distance": [float(i) / n for i in pre_dis],
            "price": [i / 100.0 for i in range(1000)],
            "user_id": random.randint(10000, 100000)
        }

    def log(self, msg):
        print "[%s] %s" % (self.getName(), msg)

    def run(self):
        self.log("thread is starting")

        total_timeout = 0

        for i in range(self.cnt):
            uri = urlparse.urlparse(self.url)

            request = json.dumps(self.data)

            # print uri.netloc, uri.path
            # print request

            start = timer()
            conn = httplib.HTTPConnection(uri.netloc)
            conn.request("POST", uri.path, request)
            response = conn.getresponse()

            # print response.status, response.reason
            # print response.read()
            conn.close()

            timeout = timer() - start
            total_timeout += timeout

        self.log("total %d requests, time cost %f, avg %f secs" % (
            self.cnt, total_timeout, total_timeout / self.cnt))


def main():
    parser = argparse.ArgumentParser(description='press test tool')
    parser.add_argument('--url', type=str, help='rank svr url',
                        default="http://127.0.0.1:20164/legacy")
    parser.add_argument('--thr-num', type=int, default=20,
                        help='concurrent threads num')
    parser.add_argument('--req-num', type=int, default=100,
                        help='request num per thread')
    parser.add_argument('--verbose', action='store_true',
                        help='print verbose log')
    args = parser.parse_args()

    threads = []
    for i in range(args.thr_num):
        threads.append(PressTest(args.url, args.req_num))
    start = timer()
    for thr in threads:
        thr.start()
    for thr in threads:
        thr.join()
    print timer() - start

if __name__ == "__main__":
    main()
