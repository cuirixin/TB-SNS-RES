#!/usr/bin/env python2.7
#-*- coding:utf8 -*-

'''
    redis操作库
'''
from _module._lib.log import Log
import pymongo
import sys

class MgDB:
    
    _client = None
    _db = None
    _port = None
    _host = None
    
    _db_name = 'tubban'

    @classmethod
    def start(cls, host="127.0.0.1", port=27017):
        cls._host = host
        cls._port = port
        #Log.info('Start connect to MongoDB server (%s:%s).', host, port)
        if cls._client is None:
            try:
                cls._client = pymongo.MongoClient(host,port)
            except Exception, e:
                Log.critical('Mongodb(%s:%s) connect failed. \n %s', host, port, str(e))
                sys.exit()
            Log.critical('Mongodb(%s:%s) Ok.', host, port)
    
    @classmethod
    def get_client(cls):
        if cls._client is None:
            cls._client = pymongo.MongoClient(cls._host, cls._port)
        return cls._client
    
    
    