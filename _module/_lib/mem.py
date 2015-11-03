#!/usr/bin/env python2.7
#-*- coding:utf8 -*-

'''
    memcache操作库
'''
from _module._lib.log import Log
import memcache
import sys
class Mem:
    __mc_conn_str = None
    __mc_conn = None

    @classmethod
    def start(cls, host, port):
        if cls.__mc_conn is None:
            cls.__mc_conn_str = "%s:%s" % (host, port)
            try:
                cls.__mc_conn = memcache.Client([cls.__mc_conn_str])
                mc_stats = cls.__mc_conn.get_stats()
                if mc_stats is None or len(mc_stats) <= 0:
                    Log.critical('memcache(%s) connect failed', cls.__mc_conn_str)
                    sys.exit()
            except Exception, e:
                print e
                Log.critical('memcache connection error(%s)(%s)', cls.__mc_conn_str, str(e))
                sys.exit()
            Log.critical('Memcatched(%s:%s) Ok.', host, port)

    @classmethod
    def __reconnect(cls):
        if cls.__mc_conn is not None:
            try:
                cls.__mc_conn.disconnect_all()
            except Exception, e:
                Log.warning('memcache disconnect(%s)', str(e))
            cls.__mc_conn = None
        try:
            cls.__mc_conn = memcache.Client([cls.__mc_conn_str])
        except Exception, e:
            cls.__mc_conn = None
            Log.critical('memcache re_connection error(%s)(%s)', cls.__mc_conn_str, str(e))
 
    @classmethod
    def get(cls, key):
        val = None
        try:
            val = cls.__mc_conn.get(key)
        except Exception, e:
            Log.warning('memcache get %s failed(%s)', key, str(e))
            cls.__reconnect()
            try:
                val = cls.__mc_conn.get(key)
            except Exception, e1: 
                val = None
                Log.warning('memcache re-get %s failed(%s)', key, str(e1))
        return val
    
    @classmethod
    def set(cls, key, val, time_out = 0):
        ret = True
        try: 
            cls.__mc_conn.set(key, val, time_out)
        except Exception, e:
            Log.warning('memcache set %s failed(%s)', key, str(e))
            cls.__reconnect()
            try:
                cls.__mc_conn.set(key, val, time_out)
            except Exception, e1:
                ret = False
                Log.warning('memcache re-set %s failed(%s)', key, str(e1))
        return ret
    
    @classmethod
    def delete(cls, key):
        try:
            cls.__mc_conn.delete(key)
        except Exception, e:
            Log.warning('memcache delete %s failed(%s)', key, str(e))
            cls.__reconnect()
            try:
                cls.__mc_conn.delete(key)
            except Exception, e1:
                Log.warning('memcache re-delete %s failed(%s)', key, str(e1))
