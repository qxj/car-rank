#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; -*-
#
# Copyright (C) 2016 Julian Qian
#
# @file      rank_client.py
# @author    Julian Qian <junist@gmail.com>
# @created   2016-05-03 02:49:24
#

import argparse
import httplib
import urlparse
import json
from timeit import default_timer as timer


def main():
    parser = argparse.ArgumentParser(description='rank client')
    parser.add_argument('--url', type=str, help='rank svr url')
    parser.add_argument('--algo', type=str, default='legacy',
                        help='rank algo')
    parser.add_argument('--num', type=int, default=100,
                        help='car num in one request')
    parser.add_argument('--user', type=int, default=0,
                        help='user id in request')
    parser.add_argument('--verbose', action='store_true',
                        help='print verbose log')
    args = parser.parse_args()

    url = "http://127.0.0.1:20164/rank"
    if args.url:
        url = args.url

    uri = urlparse.urlparse(url)

    data = {
        "algo": args.algo,
        "car_list": range(args.num),
        "distance": [i / 500.0 for i in range(args.num)],
        "price": [i / 50.0 for i in range(args.num)],
        "user_id": args.user
    }

    request = json.dumps(data)

    print uri.netloc, uri.path
    print request

    start = timer()
    conn = httplib.HTTPConnection(uri.netloc)
    conn.request("POST", uri.path, request)
    response = conn.getresponse()

    print response.status, response.reason
    print response.read()
    print timer() - start

    conn.close()

if __name__ == "__main__":
    main()
