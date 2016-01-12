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
from hashlib import md5
from datetime import datetime

import MySQLdb as mdb
from MySQLdb import converters

from tornado.log import app_log

tracking_table_prefix = 'tracking_'

def dict_value_pad(key):
    return "%(" + str(key) + ")s"

class mydb:
    """ simple db class """

    def __init__(self, host, user, passwd, dbname, port=3306,
                 coding='utf8', db_flag='slave', conv=False,
                 unix_socket=None):
        self.db_flag = db_flag
        convs = converters.conversions.copy()
        if conv:
            convs[246] = float  # decimal
            convs[10] = str  # date
            convs[8] = int  # long long
        if unix_socket:
            self.conn = mdb.Connection(
                host='localhost', user=user, passwd=passwd, db=dbname, port=port,
                conv=convs, unix_socket=unix_socket)
        else:
            self.conn = mdb.Connection(
                host=host, user=user, passwd=passwd, db=dbname, port=port, conv=convs)
        self.conn.set_character_set(coding)

    def exec_sql(self, sqlstr, params=None, resultFormat='dict',
                 needCommit=False, returnAffectedRows=False):
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
                result = curor.fetchall()[:]
        except mdb.Error as e:
            result = []
            app_log.error('%s\nsql: %s' % (e, sqlstr))
        except:
            result = []
            app_log.error('unknown failure: %s,\nsql: %s' % (sys.exc_info()[0], sqlstr))
        curor.close()
        if returnAffectedRows:
            return affected_rows
        else:
            return result

    def insert(self, table_name, param_dict, on_duplicate_ignore=True):
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
        fields = '(' + ','.join('`' + str(key) + '`' for key in keys) + ') values'
        symbols = '(' + ','.join(dict_value_pad(key) for key in keys) + ')'
        parts.append(fields)
        parts.append(symbols)
        affected_rows = 0
        if not on_duplicate_ignore:
            update_part = "on duplicate key update "
            update_part += ','.join('`' + str(key) + '`' + "=" + dict_value_pad(key) for key in keys)
            parts.append(update_part)
        sql = ' '.join(parts)
        try:
            affected_rows = cursor.execute(sql, param_dict)
            if self.db_flag == 'master':
                self.conn.commit()
        except:
            app_log.error('failed sql: %s' % sql)
        cursor.close()
        return affected_rows

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
            postfix, paramDict = genUpdateSql(condition, value_dict, paramStyle='pyformat')
            parts.append(postfix)
            sql = ' '.join(parts)
            try:
                affected_rows = cursor.execute(sql, paramDict)
            except:
                app_log.error('failed sql: %s' % sql)
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
            newParamList = self.formatData(param_list)
            keys = newParamList[0].keys()
            fields = '(' + ','.join('`' + key + '`' for key in keys) + ') values'
            symbols = '(' + ','.join(dict_value_pad(key) for key in keys) + ')'
            parts.append(fields)
            parts.append(symbols)
            sql = ' '.join(parts)
            try:
                affected_rows = cursor.executemany(sql, newParamList)
                # affected_rows = self.conn.affected_rows()
                if self.db_flag == 'master':
                    self.conn.commit()
            except:
                app_log.error('failed sql: %s' % sql)
            cursor.close()
        else:
            for param_dict in param_list:
                affected_rows += self.insert(table_name, param_dict, False)
        return affected_rows

    def tmp_table(self, table, select_stmt, index_fields=[], temporary=False):
        self.exec_sql('drop table if exists %s' % table)
        index_stmts = ''
        if index_fields:
            stmts = []
            for f in index_fields:
                stmts.append('index (%s)' % f)
            index_stmts = '(%s)' % ',\n'.join(stmts)
        self.exec_sql('create %s table %s %s %s' % (
            'temporary' if temporary else '',
            table, index_stmts, select_stmt))

    def formatData(self, param_list):
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

        return result

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
            valueParts = ','.join('`' + str(key) + '`= $' + str(key) for key in valueDict)
        elif paramStyle == 'pyformat':
            valueParts = ','.join('`' + str(key) + '`= %(' + str(key) + ')s' for key in valueDict)
        else:
            valueParts = ','.join('`' + str(key) + '`= :' + str(key) for key in valueDict)

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
        parts.append(' and '.join('`' + str(key) + '`= $' + str(key) + '_w_h_e_r_e' for key in notNoneDict))
    elif paramStyle == 'pyformat':
        parts.append(' and '.join('`' + str(key) + '`= %(' + str(key) + '_w_h_e_r_e)s' for key in notNoneDict))
    else:
        parts.append(' and '.join('`' + str(key) + '`= :' + str(key) + '_w_h_e_r_e' for key in notNoneDict))
    return ' and '.join(parts)


def db_conf(db_flag, writable=False):
    '''@return
    {
        'host': host,
        'user': user,
        'passwd': passwd,
        'dbname': dbname,
        'socket': socket
    }
    '''
    conf = {
        'host': 'localhost',
        'dbname': 'icars_zh',
        'user': 'reader',
        'passwd': 'reader!ppzuche',
        'socket': None
    }
    if writable:
        conf['user'] = 'production'
        conf['passwd'] = 'BEEQXXTGICARSCLU'
    if db_flag == 'master':
        conf['host'] = '10.144.55.23'
        conf['dbname'] = 'icars_zh'
    elif db_flag == 'slave':
        conf['host'] = '10.163.241.98'
        conf['dbname'] = 'icars_zh'
    elif db_flag == 'gis_slave':
        conf['host'] = '10.161.41.41'
        conf['dbname'] = 'gis'
    elif db_flag == 'gis01':
        conf['host'] = '10.129.27.137'
        conf['dbname'] = 'gis'
    elif db_flag == 'entrust':
        conf['host'] = '10.169.23.165'
        conf['dbname'] = 'agent'
    elif db_flag == 'ppdata':
        conf['host'] = '10.163.241.98'
        conf['dbname'] = 'ppdata'
    elif db_flag == 'testj':
        conf['dbname'] = 'icars_jqian'
        conf['socket'] = '/home/work/log/mysql/mysql.sock'
    elif db_flag == 'testsx':
        conf['dbname'] = 'icars_sx'
        conf['socket'] = '/home/work/log/mysql/mysql.sock'
    else:
        conf['host'] = '127.0.0.1'
        conf['dbname'] = 'icars_sx'
    return conf


def get_db(db_flag='slave', dbname='icars_zh', host='', conv=False, writable=True):
    """
    :param db_flag: db标签,可选'master','slave','gis_slave'
    :type db_flag: str
    :param dbname: default schema
    :type dbname: str
    :param host:
    :return: database connection instance

    suggested usage:
    >>>with get_db() as db:
    >>>    db.exec_sql('select * from a')

    """
    dc = db_conf(db_flag, writable)

    app_log.debug('dbhost(%s): %s' % (db_flag, dc['host']))
    return mydb(dc['host'], dc['user'], dc['passwd'], dc['dbname'],
                db_flag=db_flag, conv=conv, unix_socket=dc['socket'])


def get_gis_table(number):
    '''
    返回车辆gis所在表名

    :param number: 车辆盒子号码
    :return:
    '''

    return tracking_table_prefix + md5(str(number.strip())).hexdigest()[:2]


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

    paramDict = [{'userhp': 6, 'userType': 6}, {'userhp': 7, 'userType': 7}, {'userhp': 8, 'userType': 8}]
    pydb.insert_many('user_tel_sale', paramDict)
    pydb.commit()
    time.sleep(10)

    paramDict = [{'userhp': 6, 'userType': 66}, {'userhp': 7, 'userType': 777}, {'userhp': 8, 'userType': 8}]
    pydb.insert_many('user_tel_sale', paramDict, False)
    pydb.commit()
    time.sleep(10)
    pydb.close()


if __name__ == "__main__":
    # pydb = get_db('master')
    #
    # sql = 'select count(*) from orders;'
    # app_log.info(sql)
    # results = pydb.exec_sql(sql)
    # for r in results:
    # print r
    # pydb.close()
    test()
