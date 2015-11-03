#!/usr/bin/env python2.7
#-*- coding:utf8 -*-
#
# 2013-7-8 by Victor
# Copyright 2013 Tubban
from _module._lib.log import Log
from _module._lib.mem import Mem
import MySQLdb
import config_base
import functools
import sys
import time
import torndb


def debug_db(method):
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if isinstance(self, BaseModel) == False:
            return method(self, *args, **kwargs)
        else:
            start = time.clock()
            ret = method(self, *args, **kwargs)
            finsh = time.clock()
            BaseModel.set_debug_info((finsh - start) * 1000)
            if self._debug_flag == True and isinstance(args, tuple) and len(args) > 0:
                Log.debug('SQL-Time: %s[%.3fms]', args[0], (finsh - start) * 1000)
            return ret
    return wrapper

class BaseModel(object):
    _db = None
    _db_slave = None
    _sql_num = 0
    _sql_time = 0
    _debug_flag = False
    
    _restarting = False
    
    @classmethod
    def _get_db(cls, db_conf):
        return torndb.Connection(
            host = '%s:%s' % (db_conf['host'], db_conf['port']),
            user = db_conf['uname'],
            password = db_conf['pwd'],
            database = db_conf['name'],
            connect_timeout = db_conf['time_out'],
            time_zone = "+8:00"
        )
        
    @classmethod
    def _get_slave_db(cls, slaves_conf):
        
        for db_conf in slaves_conf:
            try:
                _db =  torndb.Connection(
                    host = '%s:%s' % (db_conf['host'], db_conf['port']),
                    user = db_conf['uname'],
                    password = db_conf['pwd'],
                    database = db_conf['name'],
                    connect_timeout = db_conf['time_out'],
                    time_zone = "+8:00"
                )
                sql = "SET NAMES 'utf8'"
                _db.execute(sql)
                Log.critical('Mysql Slave(%s:%s) Ok', db_conf['host'], db_conf['host'])
                return _db
            except Exception as e:
                Log.critical('Mysql Slave Error(%s:%s)(%s)', db_conf['host'], db_conf['host'], str(e))
        return cls._db
        
    @classmethod
    def _restart(cls):
        print "Reconnect to Mysql..."
        cls._db = None
        while cls._db is None:
            time.sleep(5)
            cls._restarting = True
            cls.start()
        cls._restarting = False

    @classmethod
    def start(cls):
        
        master_conf = config_base.store['db_master']
        debug_flag = config_base.store['db_master']['debug']
        
        slaves_conf = []
        
        if config_base.store.has_key('db_slaves'):
            slaves_conf = config_base.store['db_slaves']
        
        #host, port, user, password, database, time_out = 3, debug_flag = False
        
        if cls._db is None:
            cls._debug_flag = debug_flag
            try:
                cls._db = cls._get_db(master_conf)
                sql = "SET NAMES 'utf8'"
                cls._db.execute(sql)
                Log.critical("Mysql Master(%s:%s) OK" % (master_conf['host'], master_conf['host']))
            except Exception, e:
                cls._db = None
                Log.critical('Mysql Error(%s:%s)(%s)', master_conf['host'], master_conf['host'], str(e))
        
        if cls._db_slave is None:
            cls._db_slave = cls._get_slave_db(slaves_conf)
        
        #if cls._db_slave is None:

    @classmethod
    def set_debug_info(cls, sql_time):
        cls._sql_num += 1
        cls._sql_time += sql_time

    @classmethod
    def get_debug_info(cls):
        return (cls._sql_num, cls._sql_time)

    def escape_string(self, s):
        return MySQLdb.escape_string(s)

    def escape_dict(self, kwarg):
        if isinstance(kwarg, dict) == False:
            return False
        for k in kwarg.keys():
            if isinstance(kwarg[k], str) == True:
                kwarg[k] = self.escape_string(kwarg[k])
        return True
    
    @debug_db
    def get_one(self, sql, *parameters, **kwparameters):
        # 目前重连是阻塞状态，所以这个判断不会生效，暂时保留
        if self._restarting == True:
            return None
        row = None
        try:
            row = self._db.get(sql, *parameters, **kwparameters)
        except Exception, e:
            print str(e)
            # 未连接DB或者连接DB失败触发重连
            if self._db is None or str(e).find('connect to MySQL')>=0 or str(e).find('MySQL server has gone away') >= 0:
                self._restart()
        return row
    
    @debug_db
    def get_rows(self, sql, *parameters, **kwparameters):
        if self._restarting == True:
            return []
        rows = []
        try:
            rows = self._db.query(sql, *parameters, **kwparameters)
        except Exception, e:
            Log.critical('Mysql get rows error(%s)(%s)', sql, str(e))
            if self._db is None or str(e).find('connect to MySQL') >= 0 or str(e).find('MySQL server has gone away') >= 0:
                self._restart()
        return rows
    
    @debug_db
    def execute(self, sql, *parameters, **kwparameters):
        if self._restarting == True:
            return [False, 0]
        
        ret = [False, 0]
        try:
            ret[1] = self._db.execute_lastrowid(sql, *parameters, **kwparameters)
            ret[0] = True
        except Exception, e:
            Log.critical('Mysql Error(%s)(%s)', sql, str(e))
            if self._db is None or str(e).find('connect to MySQL') >=0 or str(e).find('MySQL server has gone away') >= 0:
                self._restart()
        return ret
    
    @debug_db
    def update(self, sql, *parameters, **kwparameters):
        if self._restarting == True:
            return [False, 0]
        
        ret = [False, 0]
        try:
            ret[1] = self._db.execute_rowcount(sql, *parameters, **kwparameters)
            ret[0] = True
        except Exception, e:
            Log.critical('Mysql Error(%s)(%s)', sql, str(e))
            print self._db is None
            print str(e).find('connect to MySQL')
            print str(e).find('MySQL server has gone away')
            if self._db is None or str(e).find('connect to MySQL') >=0 or str(e).find('MySQL server has gone away') >= 0:
                self._restart()
        return ret
    
    
    ######## Slave ###########
    
    @debug_db
    def get_one_by_slave(self, sql, *parameters, **kwparameters):
        # 目前重连是阻塞状态，所以这个判断不会生效，暂时保留
        if self._restarting == True:
            return None
        row = None
        try:
            row = self._db_slave.get(sql, *parameters, **kwparameters)
        except Exception, e:
            Log.critical('Mysql get rows error(%s)(%s)', sql, str(e))
        return row
    
    @debug_db
    def get_rows_by_slave(self, sql, *parameters, **kwparameters):
        if self._restarting == True:
            return []
        rows = []
        try:
            rows = self._db_slave.query(sql, *parameters, **kwparameters)
        except Exception, e:
            Log.critical('Mysql get rows error(%s)(%s)', sql, str(e))
        return rows
    
    
    def set_cache(self, key, val, time_out):
        return Mem.set(key, val, time_out)

    def get_cache(self, key):
        return Mem.get(key)
    
    def clear_cache(self, key):
        Mem.delete(key)
    
    def _args_handle(self, type, args, fields):
        # TODO: what's meaning
        # self.escape_dict(args)
        
        if type == 'insert':
            missing_fields = [];
            for (k,v) in fields.items():
                if args.has_key(k):
                    v['value'] = args[k]
                    if v['type']=='d':
                        try:
                            v['value'] = int(args[k])
                        except Exception, e:
                            return [False, "key: %s's value is not an integer" % k]
                       
                    if v['type']=='f':
                        try:
                            v['value'] = float(args[k])
                        except Exception, e:
                            return [False, "key: %s's value is not a float" % k]
                        
                elif v.has_key('required') and v['required'] == 1:
                    missing_fields.append(k)
                elif v.has_key('default'):
                    v['value'] = v['default']
                else:
                    v['value'] = None
    
            if len(missing_fields) > 0:
                msg = "missing fields: "
                for i in missing_fields:
                    msg += i
                return [False, msg]
            else:
                return [True, fields]

        if type == 'update':
            for (k,v) in fields.items():
                if args.has_key(k):
                    v['value'] = args[k]
                else:
                    del(fields[k])
            return [True, fields]        
        
    def _insert(self, table, fields):
        # build insert sql        
        pattern = ""
        values = ""
        flag = False
        for (k, v) in fields.items():
            if v['value'] == None:
                continue

            if flag: 
                pattern += ", "
                values += ", "
            else:
                flag = True
            
            pattern += "`%s`" % k
            if v['type'] == 'd':
                values += "%d" % v['value']
            elif v['type'] == 'f':
                values += "%f" % v['value']
            elif v['type'] == 's':
                values += "'%s'" % self.escape_string(str(v['value']))
            else:
                # todo: error
                pass
        sql = "INSERT INTO %s(%s) VALUES(%s)" % (table, pattern, values)
        
        # TODO: what's meaning
        sql = sql.replace('%', '%%')
        # TODEL
        return self.execute(sql)
    
    def _replace(self, table, fields):
        # build insert sql        
        pattern = ""
        values = ""
        flag = False
        for (k, v) in fields.items():
            if v['value'] == None:
                continue

            if flag: 
                pattern += ", "
                values += ", "
            else:
                flag = True
            
            pattern += "`%s`" % k
            if v['type'] == 'd':
                values += "%d" % v['value']
            elif v['type'] == 'f':
                values += "%f" % v['value']
            elif v['type'] == 's':
                values += "'%s'" % self.escape_string(v['value'])
            else:
                # todo: error
                pass
        sql = "REPLACE INTO %s(%s) VALUES(%s)" % (table, pattern, values)
        
        # TODO: what's meaning
        sql = sql.replace('%', '%%')
        # TODEL
        return self.execute(sql)

    def _update(self, table, fields, where):
        #self.escape_dict(fields)    
        # build insert sql        
        s = ""
        flag = False
        for (k,v) in fields.items():
            if flag: 
                s += ", "
            else:
                flag = True
            
            if v['type'] == 'd':
                s += "`%s` = %d" % (k, v['value'])
            elif v['type'] == 'f':
                s += "`%s` = '%f'" % (k, v['value'])
            elif v['type'] == 's':
                s += "`%s` = '%s'" % (k, self.escape_string(v['value']))
            else:
                # todo: error
                pass
        sql = "UPDATE %s SET %s WHERE %s" % (table, s, where)
        # TODO: what's meaning
        sql = sql.replace('%', '%%')
        # TODEL
        return self.update(sql)

    """
    Func : 获取分表表名
    """
    def _get_mo_split_table(self, id, table, mo=10000): 
        if id is None:
            return table
        index = int(int(id) / int(mo))
        if index == 0:
            return table
        return table + "_" + str(index)
    
    """
    Func : Gen fields sql select string.
    Eg. 
         Input: prefix = u, fields= ["username", "email"]
         Output: u.`username`, u.`email`
    """
    def _gen_fields_str(self, fields, prefix=None):
        _f = []
        if prefix is not None and prefix <> '':
            _f = [prefix+'.`'+item+'`' for item in fields]
        else:
            _f = ['`'+item+'`' for item in fields]
        if len(_f) == 0:
            return ''
        return ",".join(_f)
    
    """
    删除key不在allow_arr中的数据
    """
    def _filt_array(self, arr, allow_arr):
        keys = arr.keys()
        for key in keys:
            if not key in allow_arr:
                del arr[key]
        return arr
        

def test_funct(sql, *parameters, **kwparameters):
    
    print parameters
    print kwparameters
    
if __name__ == "__main__":
    #Common.get_month_range_secs("201405")
    test_funct("sql", {"test": "name"}, False)
        