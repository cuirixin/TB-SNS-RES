#!/usr/bin/env python2.7
#-*- coding:utf8 -*-
#
# 2014-2-13 by Victor
# Copyright 2014 Tubban

######################

######暂时未用到

######################

from lib.log import Log
import functools
import redis
import sys
import time


def debug_db(method):
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if isinstance(self, RedisModel) == False:
            return method(self, *args, **kwargs)
        else:
            start = time.clock()
            ret = method(self, *args, **kwargs)
            finsh = time.clock()
            RedisModel.set_debug_info((finsh - start) * 1000)
            if self._debug_flag == True and isinstance(args, tuple) and len(args) > 0:
                Log.debug('Redis-Time: %s[%.3fms]', args[0], (finsh - start) * 1000)
            return ret
    return wrapper


class RedisModel(object):
    _pool = None
    _db = None

    @classmethod
    def start(cls, host, port, time_out = 3, debug_flag = False):
        if cls._db is None:
            cls._debug_flag = debug_flag
            try:
                cls._pool = redis.ConnectionPool(host=host, port=port)
                _db = redis.Redis(connection_pool=cls._pool)
            except Exception, e:
                Log.critical('Redis connect failed(%s:%s)(%s)', host, port, str(e))
                sys.exit()
            Log.info("Redis connect successfully. port:"+port)
                
    @classmethod
    def set_debug_info(cls, sql_time):
        cls._sql_num += 1
        cls._sql_time += sql_time

    @classmethod
    def get_debug_info(cls):
        return (cls._sql_num, cls._sql_time)
    
    @debug_db
    def set(self, key):
        return self._db.set(key)
        
    @debug_db
    def get(self, key):
        return self._db.get(key)
    
    