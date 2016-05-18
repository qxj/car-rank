#!/usr/bin/python
# coding=utf8
"""
mysql python simple interface
usage:
--------
pydb = get_db('slave')
results = pydb.exec_sql('select count(*) from orders;');
pydb.close()
"""

import os
import sys
from datetime import datetime
import logging

import MySQLdb as mdb
from MySQLdb import converters

from log import init_log, error_info


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
    elif db_flag == 'test38':
        conf['host'] = '192.168.1.38'
        conf['dbname'] = 'icars_sx'
        conf['socket'] = '/home/work/log/mysql/mysql.sock'
    elif db_flag == 'test28_price':
        conf['host'] = '192.168.1.28'
        conf['dbname'] = 'price'
        conf['socket'] = '/home/work/log/mysql/mysql.sock'
    elif db_flag == 'test38_price':
        conf['host'] = '192.168.1.38'
        conf['dbname'] = 'price'
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

    return conf


def get_log_file(ds=None):
    if ds:
        return os.getenv("MYDB_LOG") if os.getenv("MYDB_LOG") else \
            "/tmp/pydb_%s_%s_%s.log" % (
                os.getlogin(), ds,
                os.path.splitext(os.path.basename(sys.argv[0]))[0])
    else:
        return os.getenv("MYDB_LOG") if os.getenv("MYDB_LOG") else \
            "/tmp/pydb_%s_%s.log" % (
                os.getlogin(),
                os.path.splitext(os.path.basename(sys.argv[0]))[0])


log = init_log(get_log_file(),
               logtostderr=True if os.getenv("MYDB_LOGTOSTDERR") else False)
error_log = init_log(get_log_file(datetime.now().strftime('%Y-%m-%d')),
                     level=logging.WARN, logname='pydb_error_log',
                     logtostderr=True if os.getenv("MYDB_LOGTOSTDERR") else False)


def dict_value_pad(key):
    return "%(" + str(key) + ")s"


def db_error_log(sql, param=None, debug=False):
    msg = error_info()
    if param is None:
        error_msg = '%s\nsql: %s\n%s\n' % (msg, sql, 30 * '~')
    else:
        dt = param
        if len(param) > 1 and not isinstance(param, dict) and (
                isinstance(param[0], list) or isinstance(param[0], tuple)):
            dt = param[0]
        error_msg = '%s\nsql: %s\nparam:%s\n%s\n' % (msg, sql, dt, 30 * '~')
    error_log.error(error_msg)
    if debug:
        raise Exception(error_msg)
    return error_msg


class mydb(object):
    """ simple db class """

    def __init__(self, host, user, passwd, dbname, port=3306,
                 coding='utf8', db_flag='slave', conv=False,
                 unix_socket=None, debug=False, use_unicode=False):
        self.db_flag = db_flag
        self.debug = debug
        convs = converters.conversions.copy()
        if conv:
            convs[246] = float  # decimal
            convs[10] = str  # date
            convs[8] = int  # long long
        if unix_socket:
            self.conn = mdb.Connection(
                host='localhost', user=user, passwd=passwd, db=dbname, port=port,
                conv=convs, unix_socket=unix_socket, use_unicode=use_unicode)
        else:
            self.conn = mdb.Connection(
                host=host, user=user, passwd=passwd, db=dbname, port=port, conv=convs,
                use_unicode=use_unicode)
        self.conn.set_character_set(coding)

    def set_debug_mode(self, debug=True):
        self.debug = debug

    def exec_sql(self, sqlstr, params=None, resultFormat='dict',
                 needCommit=False, returnAffectedRows=False, withColumns=False):
        """
        执行sql,执行方式有如下几种：

        >>>pydb=get_db()
        >>>sql='delete from user_tel_sale'
        >>>pydb.exec_sql(sql)

        >>>sql2="insert into user_tel_sale (userhp,userType) values (%s,%s)"

        >>>param=(1,1)
        >>>sql3=sql2 % param
        >>>pydb.exec_sql(sql3)

        >>>param=(2,2)
        >>>pydb.exec_sql(sql2,param)

        >>>param=[(3,3),(4,4)]
        >>>pydb.exec_sql(sql2,param)

        :param sqlstr: sql string
        :type slqstr: str
        :param params:
        :type params: tuple or list
        :return:
        """
        cursorType = mdb.cursors.Cursor
        if resultFormat == 'dict':
            cursorType = mdb.cursors.DictCursor
        curor = self.conn.cursor(cursorType)
        flag = True
        affected_rows = 0
        columns = []
        try:
            if params:
                if isinstance(params, tuple):
                    affected_rows = curor.execute(sqlstr, params)
                elif isinstance(params, list) and isinstance(params[0], tuple):
                    flag = False
                    affected_rows = curor.executemany(sqlstr, params)
                    # print params
            else:
                # print sqlstr
                affected_rows = curor.execute(sqlstr)
            if self.db_flag == 'master' or needCommit:
                self.conn.commit()
            result = []
            if flag:
                # if resultFormat != 'dict':
                if curor.description:
                    columns = [d[0] for d in curor.description]
                result = curor.fetchall()[:]
        except mdb.Error as e:
            result = []
            log.error('%s\nsql: %s' % (e, sqlstr))
            db_error_log(sqlstr, params, self.debug)
        except:
            result = []
            log.error('unknown failure: %s,\nsql: %s' %
                      (sys.exc_info()[0], sqlstr))
            db_error_log(sqlstr, params, self.debug)
        curor.close()

        if returnAffectedRows:
            if not withColumns:
                return affected_rows
            else:
                return affected_rows, columns
        else:
            if not withColumns:
                return result
            else:
                return result, columns

    def get_query_cursor(self, sqlStr, params=None, resultFormat='dict'):
        """
        get the query cursor
        :param sqlStr:
        :param params:
        :param resultFormat:
        :return:
        """
        sqlStriped = sqlStr.strip().split()
        if sqlStriped and sqlStriped[0].upper() not in ('UPDATE', 'DELETE'):
            cursorType = mdb.cursors.Cursor
            if resultFormat == 'dict':
                cursorType = mdb.cursors.DictCursor
            curor = self.conn.cursor(cursorType)
            curor.execute(sqlStr, params)
            return curor
        else:
            db_error_log(
                sqlStr, 'this function is only for select operation', self.debug)
            return None

    def insert(self, table_name, param_dict, on_duplicate_ignore=True,
               restrict=False):
        """
        利用字典方式传参，完成数据插入,使用方式如下：
        >>>pydb=get_db()
        >>>paramDict={'userhp':5,'userType':5}
        >>>pydb.insert('user_tel_sale',paramDict)

        >>>paramDict={'userhp':5,'userType':555}
        >>>pydb.insert('user_tel_sale',paramDict,False)

        :param table_name: 表名称
        :type table_name: str
        :param param_dict: 参数列表
        :type param_dict: dict
        :param on_duplicate_ignore: 遇到重复键是否ignore
        :type on_duplicate_ignore: bool
        :return: affected_rows
        """
        if not param_dict:
            return
        cursor = self.conn.cursor(mdb.cursors.DictCursor)
        ignore = ''
        if on_duplicate_ignore:
            ignore = ' ignore '
        parts = ['insert', ignore, 'into', table_name]
        keys = param_dict.keys()
        fields = '(' + ','.join('`' + str(key) +
                                '`' for key in keys) + ') values'
        symbols = '(' + ','.join(dict_value_pad(key) for key in keys) + ')'
        parts.append(fields)
        parts.append(symbols)
        affected_rows = 0
        if not on_duplicate_ignore:
            update_part = "on duplicate key update "
            update_part += ','.join('`' + str(key) + '`' +
                                    "=" + dict_value_pad(key) for key in keys)
            parts.append(update_part)
        sql = ' '.join(parts)
        try:
            affected_rows = cursor.execute(sql, param_dict)
            if self.db_flag == 'master':
                self.conn.commit()
        except:
            log.info('failed sql: %s' % sql)
            db_error_log(sql, param_dict, self.debug)
        cursor.close()
        return affected_rows

    def get_last_insert_id(self):
        """
        get last inserted id
        :return:
        """
        return self.conn.insert_id()

    def update(self, table_name, condition, value_dict):
        """
        update function
        :param table_name:
        :param condition:
        :param value_dict:
        :return:
        """
        affected_rows = 0
        if value_dict:
            cursor = self.conn.cursor(mdb.cursors.DictCursor)
            parts = ['update', table_name, 'set']
            postfix, paramDict = genUpdateSql(
                condition, value_dict, paramStyle='pyformat')
            parts.append(postfix)
            sql = ' '.join(parts)
            try:
                affected_rows = cursor.execute(sql, paramDict)
            except:
                log.error('failed sql: %s' % sql)
                db_error_log(sql, [condition, value_dict], self.debug)
            cursor.close()
        return affected_rows

    def insert_many(self, table_name, param_list, on_duplicate_ignore=True):
        """
        批量插入，利用字典方式传参，完成数据插入,使用方式如下：
        >>>pydb=get_db()
        >>>paramDict=[{'userhp':6,'userType':6},{'userhp':7,'userType':7},{'userhp':8,'userType':8}]
        >>>pydb.insert_many('user_tel_sale',paramDict)

        >>>paramDict=[{'userhp':6,'userType':66},{'userhp':7,'userType':777},{'userhp':8,'userType':8}]
        >>>pydb.insert_many('user_tel_sale',paramDict,False)


        :param table_name: 表名称
        :type table_name: str
        :param param_list: 参数列表
        :type param_list: list of dict
        :param on_duplicate_ignore: 遇到重复键是否ignore
        :type on_duplicate_ignore: bool
        :return:
        """
        if not param_list:
            return

        cursor = self.conn.cursor(mdb.cursors.DictCursor)
        ignore = ''
        if on_duplicate_ignore:
            ignore = ' ignore '
        parts = ['insert', ignore, 'into', table_name]
        affected_rows = 0
        if on_duplicate_ignore:
            newParamList = self.formatData(param_list, True)
            keys = newParamList[0][0].keys()
            fields = '(' + ','.join('`' + key +
                                    '`' for key in keys) + ') values'
            symbols = '(' + ','.join(dict_value_pad(key) for key in keys) + ')'
            parts.append(fields)
            parts.append(symbols)
            sql = ' '.join(parts)
            for pList in newParamList:
                try:
                    affected_rows += cursor.executemany(sql, pList)
                    # affected_rows = self.conn.affected_rows()
                    # if self.db_flag == 'master':
                    self.conn.commit()
                except:
                    log.info('failed sql: %s' % sql)
                    db_error_log(sql, newParamList, self.debug)
            cursor.close()
        else:
            for param_dict in param_list:
                affected_rows += self.insert(table_name, param_dict, False)
        return affected_rows

    def select(self, table, fields, resultFormat='dict'):
        f = ['`' + item + '`' for item in fields]
        sql_parts = ['select', ','.join(f), 'from', table]
        sql = ' '.join(sql_parts)
        return self.exec_sql(sql, resultFormat=resultFormat)

    def formatData(self, param_list, segment=False, segment_size=20000):
        """
        数据词典对齐

        :param param_list:
        :return:
        """
        allKeys = set()
        for valueDict in param_list:
            for key in valueDict:
                allKeys.add(key)
        result = []
        for valueDict in param_list:
            tmp = {}
            for key in allKeys:
                tmp[key] = valueDict.get(key, None)
            result.append(tmp)

        if not segment:
            return result
        else:
            r = []
            total = len(result)
            segment_num = len(result) / segment_size + 1
            for i in range(segment_num):
                start_index = i * segment_size
                end_index = min(i * segment_size + segment_size, total)
                tmp = result[start_index:end_index]
                r.append(tmp)
            return r

    def commit(self):
        self.conn.commit()

    def escape(self, str_cont):
        """ escape  """
        return self.conn.escape_string(str_cont)

    def close(self):
        """ close the db """
        self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()

    def get_connection(self):
        return self.conn


def genUpdateSql(whereDict, valueDict, paramStyle='pyformat'):
    """
    根据条件词典和之词典生成update语句，条件词典只支持简单and
    usage examples:
    >>>whereDict={'a':1,'b':1,'c':1}
    >>>valueDict={'a':2,'b':2,'d':4}
    >>>sql,paramDict= genUpdateSql(whereDict,valueDict)
    >>>sql,paramDict

    >>>'`a`= $a,`b`= $b,`d`= $d where `a`= $a_w_h_e_r_e and `c`= $c_w_h_e_r_e and `b`= $b_w_h_e_r_e'
    >>>{'a': 2, 'b_w_h_e_r_e': 1, 'b': 2, 'd': 4, 'c_w_h_e_r_e': 1, 'a_w_h_e_r_e': 1}

    :param whereDict:
    :param valueDict:
    :param paramStyle:
    :return:
    """
    if paramStyle not in ('pyformat', 'named', 'phpformat'):
        return None, None
    if not valueDict:
        return None, None
    else:
        paramDict = valueDict
        tmpWhereDict = {}
        for key in whereDict:
            tmpWhereDict[str(key) + '_w_h_e_r_e'] = whereDict[key]
        whereParts = dict2whereSql(whereDict, paramStyle)
        if paramStyle == 'phpformat':
            valueParts = ','.join('`' + str(key) + '`= $' + str(key)
                                  for key in valueDict)
        elif paramStyle == 'pyformat':
            valueParts = ','.join(
                '`' + str(key) + '`= %(' + str(key) + ')s' for key in valueDict)
        else:
            valueParts = ','.join('`' + str(key) + '`= :' + str(key)
                                  for key in valueDict)

        paramDict.update(tmpWhereDict)
        sql = valueParts
        if whereParts.strip():
            sql = valueParts + ' where ' + whereParts
        return sql, paramDict


def dict2whereSql(whereDict, paramStyle='pyformat'):
    parts = []
    notNoneDict = dict()
    for key in whereDict:
        if whereDict[key] is None:
            parts.append('`' + str(key) + '` is NULL')
        else:
            notNoneDict[key] = whereDict[key]

    if paramStyle == 'phpformat':
        parts.append(' and '.join('`' + str(key) + '`= $' +
                                  str(key) + '_w_h_e_r_e' for key in notNoneDict))
    elif paramStyle == 'pyformat':
        parts.append(' and '.join('`' + str(key) + '`= %(' +
                                  str(key) + '_w_h_e_r_e)s' for key in notNoneDict))
    else:
        parts.append(' and '.join('`' + str(key) + '`= :' +
                                  str(key) + '_w_h_e_r_e' for key in notNoneDict))
    return ' and '.join(parts)


def get_db(db_flag='slave', dbname=None, host='', conv=False, writable=True,
           user_flag=None, use_unicode=False):
    """
    :param db_flag: db标签,可选'master','slave','gis_slave'等
    :type db_flag: str
    :param dbname: default schema
    :type dbname: str
    :param host: host ip for db
    :type host: str
    :param conv:
    :param writable: 废弃参数，保留保证前向兼容
    :param user_flag: 用户标签
    :return: database connection instance

    suggested usage:
    >>>with get_db() as db:
    >>>    db.exec_sql('select * from a')

    """
    online_flag = True

    dc = db_conf(db_flag if online_flag else None, user_flag)

    print >> sys.stderr, "dbhost:", dc['host']
    log.debug('dbhost: %s' % dc['host'])
    dbname = dc['dbname'] if not dbname else dbname
    port = dc.get('port', 3306)
    db_host = dc.get('host', host)

    return mydb(db_host, dc['user'], dc['password'], dbname, port=port,
                db_flag=db_flag, conv=conv, unix_socket=dc['socket'],
                use_unicode=use_unicode)


def test():
    import time

    pydb = get_db()
    sql = 'delete from user_tel_sale'
    pydb.exec_sql(sql)
    pydb.commit()
    time.sleep(10)
    sql2 = "insert into user_tel_sale (userhp,userType) values (%s,%s)"
    param = (1, 1)
    sql3 = sql2 % param
    pydb.exec_sql(sql3)
    pydb.commit()
    time.sleep(10)
    param = (2, 2)
    pydb.exec_sql(sql2, param)
    pydb.commit()
    time.sleep(10)
    param = [(3, 3), (4, 4)]
    pydb.exec_sql(sql2, param)
    pydb.commit()
    time.sleep(10)

    paramDict = {'userhp': 5, 'userType': 5}
    pydb.insert('user_tel_sale', paramDict)
    pydb.commit()
    time.sleep(10)

    paramDict = {'userhp': 5, 'userType': 555}
    pydb.insert('user_tel_sale', paramDict, False)
    pydb.commit()
    time.sleep(10)

    paramDict = [{'userhp': 6, 'userType': 6}, {
        'userhp': 7, 'userType': 7}, {'userhp': 8, 'userType': 8}]
    pydb.insert_many('user_tel_sale', paramDict)
    pydb.commit()
    time.sleep(10)

    paramDict = [{'userhp': 6, 'userType': 66}, {
        'userhp': 7, 'userType': 777}, {'userhp': 8, 'userType': 8}]
    pydb.insert_many('user_tel_sale', paramDict, False)
    pydb.commit()
    time.sleep(10)
    pydb.close()


if __name__ == "__main__":
    # pydb = get_db('master')
    #
    # sql = 'select count(*) from orders;'
    # log.info(sql)
    # results = pydb.exec_sql(sql)
    # for r in results:
    # print r
    # pydb.close()
    test()
