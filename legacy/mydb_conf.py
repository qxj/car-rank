#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; -*-
#
# Copyright (C) 2016 Julian Qian
#
# @file      mydb_conf.py
# @author    Julian Qian <junist@gmail.com>
# @created   2016-05-26 11:08:35
#


def db_conf(db_flag, user_flag=None):
    """

    :param db_flag: 数据库标签
    :param user_flag: 用户标签
    :return: {
                'host': host,
                'user': user,
                'password': passwd,
                'db_name': dbname,
                'socket': socket
             }
    """

    conf = {
        'host': 'localhost',
        'port': 3306,
        'dbname': 'icars_zh',
        'user': 'production',
        'password': 'BEEQXXTGICARSCLU',
        'socket': None
    }

    if db_flag == 'testj':
        conf['dbname'] = 'icars_jqian'
        conf['socket'] = '/home/work/log/mysql/mysql.sock'
    elif db_flag == 'test28':
        conf['host'] = '192.168.1.28'
        conf['dbname'] = 'icars_staging'
        conf['socket'] = '/home/work/log/mysql/mysql.sock'
    elif db_flag == 'test28_price':
        conf['host'] = '192.168.1.28'
        conf['dbname'] = 'price'
        conf['socket'] = '/home/work/log/mysql/mysql.sock'
    elif db_flag == 'test28_sphinx':
        conf['host'] = '192.168.1.28'
        conf['dbname'] = 'sphinx'
        conf['socket'] = '/home/work/log/mysql/mysql.sock'
    elif db_flag == 'test38':
        conf['host'] = '192.168.1.38'
        conf['dbname'] = 'icars_sx'
        conf['socket'] = '/home/work/log/mysql/mysql.sock'
    elif db_flag == 'test38_price':
        conf['host'] = '192.168.1.38'
        conf['dbname'] = 'price'
        conf['socket'] = '/home/work/log/mysql/mysql.sock'
    elif db_flag == 'test38_sphinx':
        conf['host'] = '192.168.1.38'
        conf['dbname'] = 'sphinx'
        conf['socket'] = '/home/work/log/mysql/mysql.sock'
    elif db_flag == 'master':
        conf['host'] = '10.45.232.207'
        conf['dbname'] = 'icars_zh'
    elif db_flag == 'slave':
        conf['host'] = '10.45.237.101'
        conf['dbname'] = 'icars_zh'
    elif db_flag == 'score':
        conf['host'] = '10.45.232.207'
    elif db_flag == 'price':
        conf['host'] = '10.45.237.101'
        conf['port'] = 3307
        conf['dbname'] = 'price'
    elif db_flag == 'sphinx':
        conf['host'] = '10.45.238.231'
        conf['dbname'] = 'sphinx'
    else:
        raise Exception('no database flag found: ' + db_flag)

    return conf


def main():
    pass

if __name__ == "__main__":
    main()
