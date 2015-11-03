#!/usr/bin/env python2.7
#-*- coding:utf8 -*-
#
# 2014-2-9 by Victor
# Copyright 2014 Tubban
from _module import const
from _module._lib.common import Common
from _module._lib.rds import Rds
import json

class PushControl:
    def __init__(self):
        pass
    
    """
    msg = {
          "type": const.PUSH.TYPE_PHONE_MESSAGE,
          "code": const.PUSH.CODE_MOBILE_CHECK,
          "receiver": 0,
          "content": "%s (您的动态验证码，一般人儿我不告诉他)" % dynamic_code,
          "extra": json.dumps({"mobile_code": mobile_code, "mobile": mobile})
        }
    """
    def push_one(self, message):
        
        if not message.has_key('code') or message['code'] not in const.PUSH.CODES:
            return False
        key = message['code']
        value = json.dumps(message)
        Rds.push(key, value)
        return True
    
    def push_patch(self, messages):
        pass
    
    def pop_one(self, key):
        if not key or key not in const.PUSH.CODES:
            return None
        value = Rds.pop(key)
        if value == False:
            return None
        return value
        
    def pop_patch(self, size=10):
        pass
    
        
        
    
    
        
