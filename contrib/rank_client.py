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
    parser.add_argument('--algo', type='legacy', help='rank algo')
    parser.add_argument('--verbose', action='store_true',
                        help='print verbose log')
    args = parser.parse_args()

    url = "http://127.0.0.1:20164/rank"
    if args.url:
        url = args.url

    uri = urlparse.urlparse(url)

    data = {
        "algo": args.algo,
        "car_list": range(1000),
        "distance": [i / 1000.0 for i in range(1000)],
        "price": [i / 100.0 for i in range(1000)],
        "user_id": 142317
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
