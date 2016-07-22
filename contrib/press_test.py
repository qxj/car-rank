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
import collections
import httplib
import urlparse
import json
import random
import threading
import sys
from timeit import default_timer as timer


g_cntr = collections.Counter(timeout=0, requests=0, threads=0)


class PressTest(threading.Thread):

    def __init__(self, url, algo='legacy', cnt=1000, sim_pages=0):
        super(PressTest, self).__init__()
        self.url = url
        self.algo = algo
        self.pages = sim_pages
        self.cnt = cnt

    def get_data(self, n):
        car_list = range(n)
        random.shuffle(car_list)
        pre_dis = range(n)
        random.shuffle(pre_dis)
        price_list = range(n)
        random.shuffle(price_list)
        data = {
            "algo": self.algo,
            "car_list": car_list,
            "distance": [round(float(i) / n * 10, 2) for i in pre_dis],
            "price": price_list,
            "user_id": random.randint(10000, 100000)
        }
        return data

    def log(self, msg):
        print "[%s] %s" % (self.getName(), msg)

    def run(self):
        global g_cntr

        self.log("thread is starting")
        g_cntr['threads'] += 1

        data = self.get_data(random.randint(100, 500))
        pages = 0

        for i in range(self.cnt):
            uri = urlparse.urlparse(self.url)

            pages += 1
            if self.pages > 0 and pages % self.pages == 0:
                data = self.get_data(random.randint(100, 500))

            request = json.dumps(data)

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

            g_cntr['timeout'] += timeout
            g_cntr['requests'] += 1

            if pages % 100 == 0:
                sys.stderr.write('.')


def main():
    parser = argparse.ArgumentParser(description='press test tool')
    parser.add_argument('--url', type=str, help='rank svr url',
                        default="http://127.0.0.1:20164/rank")
    parser.add_argument('--thr-num', type=int, default=20,
                        help='concurrent threads num')
    parser.add_argument('--sim-pages', type=int, default=5,
                        help='generate new data every some pages')
    parser.add_argument('--req-num', type=int, default=1000,
                        help='request num per thread')
    parser.add_argument('--algo', type=str, default='legacy',
                        help='rank algorithm')
    parser.add_argument('--verbose', action='store_true',
                        help='print verbose log')
    args = parser.parse_args()

    threads = []
    for _ in range(args.thr_num):
        threads.append(PressTest(args.url, args.algo,
                                 args.req_num, args.sim_pages))
    start = timer()
    for thr in threads:
        thr.start()
    for thr in threads:
        thr.join()
    g_cntr['actual_timeout'] = timer() - start

    print ""
    print "Total threads %d" % g_cntr['threads']
    print "Total timeout %f " % g_cntr['actual_timeout']
    print "Total requests %d" % g_cntr['requests']
    print "Average request timeout %.2fms" % (g_cntr['timeout'] / g_cntr['requests'] * 1000)
    print "QPS %f" % (g_cntr['requests'] / g_cntr['timeout'])
    print ""

if __name__ == "__main__":
    main()
