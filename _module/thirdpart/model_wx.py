#!/usr/bin/env python2.7
#-*- coding:utf8 -*-
#
# 2014-2-13 by Victor
# Copyright 2014 Tubban
from _module import const
from _module._base_m_ import BaseModel
from _module._lib.common import Common

class ThirdpartWeixinModel(BaseModel):
    
    def __init__(self, uid = None):
        self._thirdpart_config_table = "thirdpart_config"
        self._thirdpart_account_table = 'auth_thirdpart_account'
        self._uid = uid
        
    
    def get_access_token(self):
        sql = "SELECT `value` from %s where code='%s'" % \
                (self._thirdpart_config_table, 'wx_access_token')
        return self.get_one(sql)['value']
    
    def get_by_openid(self, openid):
        sql = "SELECT uid, openid FROM %s WHERE openid='%s' and type=%d LIMIT 1" % \
                (self._thirdpart_account_table, openid, const.ThirdpartAccount.TYPE_WEIXIN)
        return self.get_one(sql)