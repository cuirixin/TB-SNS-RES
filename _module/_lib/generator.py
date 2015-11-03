#!/usr/bin/env python2.7
#-*- coding:utf8 -*-
#
# 2013-7-8 by cuirixin
# Copyright 2013 Tubban
import datetime
import hashlib
import math
import random
import time
import uuid

class Generator:
    @staticmethod
    def getVersion():
        return 'v0.0.1'
    
   
    @staticmethod  
    def _md5(arg):
        return hashlib.new("md5", arg).hexdigest()
    
   
    @staticmethod 
    def generate_token():
        return Generator._md5(str(uuid.uuid1()))#base64.b64encode(uuid.uuid4().bytes + uuid.uuid4().bytes)
    
    @staticmethod
    def gen_random_int(length=4):
        start = math.pow(10, length-1)
        end = math.pow(10, length) - 1
        return random.randint(start, end)
    
    """
    Func: 生成ticket
    @param target_id: 前缀标识, 100取模构造两位前缀比如，01， 12
    """
    @staticmethod
    def gen_ticket(target_id, ):
        _ticket = ''
        p_int = int(target_id) % 100
        if p_int == 0:
            _ticket = '00'
        elif p_int < 10:
            _ticket = '0%d' % p_int
        else:
            _ticket = str(p_int)
        _ticket = "%s%s%s%s%s" % (_ticket, 
                                  int(time.time()*10) % 1000,   
                                  Generator.gen_random_int(2),
                                  datetime.datetime.now().microsecond % 1000,
                                  Generator.gen_random_int(2))
            
        for i in range(0, 12-len(_ticket)):
            _ticket = _ticket+'0'
            
        return _ticket

if __name__ == "__main__":
    
    for one in range(100):
        print Generator.gen_ticket(98823)
    
