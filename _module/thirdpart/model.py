#!/usr/bin/env python2.7
#-*- coding:utf8 -*-
#
# 2014-2-13 by Victor
# Copyright 2014 Tubban
from _module._base_m_ import BaseModel
from _module._lib.common import Common

class ThirdpartAccountModel(BaseModel):
    
    def __init__(self, uid = None):
        self._thirdpart_account_table = "auth_thirdpart_account"
        self._uid = uid
        
    def find_by_openid(self, type, openid):
        sql = "SELECT uid, add_time from %s where type=%d and openid='%s' LIMIT 1" % \
                (self._thirdpart_account_table, type, self.escape_string(openid))
        return self.get_one(sql)
    
    def find_by_uid(self, type, uid):
        sql = "SELECT openid, add_time from %s where type=%d and uid=%d LIMIT 1" % \
                (self._thirdpart_account_table, type, uid)
        return self.get_one(sql)
    
    
    def add(self, fields):
        account = {
            'type': {'type':'d', 'default': 0, 'required': 1},
            'openid': {'type':'s', 'required': 1},
            'uid': {'type': 'd', 'required': 1},
            'add_time': {'type':'d', 'default': Common.get_current_time()},
        }
        
        ret = self._args_handle('insert', fields, account)               
        if not ret[0]:
            return ret
        return self._insert(self._thirdpart_account_table, account)

    def mod(self, type, openid, args):
        
        account = {
            'uid': {'type':'d'},
        }

        ret = self._args_handle('update', args, account)               
        if not ret[0]:
            return False
        where = " openid='%s' and type=%d " % (self.escape_string(openid), type)
        if len(account) > 0:
            ret = self._update(self._thirdpart_account_table, account, where)
            if not ret[0]:
                return False
        return True
