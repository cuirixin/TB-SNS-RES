#!/usr/bin/env python2.7
#-*- coding:utf8 -*-
#
# 2013-12-4 by Victor
# Copyright 2013 Tubban
from _module import const
from _module._base_m_ import BaseModel

class UConfigModel(BaseModel):
    
    INVIATION_NAME = "invitation"
    INVITATION_CONFIG = dict()
    INVITATION_CONFIG["type_visible"] = const.Invitation.TYPE_VISIBLE_ANYONE
    
    def __init__(self, uid = None):
        self._table = 'auth_user_config'
        self._uid = uid
        
    def _mod(self, fields):
        
        user_config = {
            'uid': {'type':'d', 'required':1},
            'name': {'type':'s', 'required':1},
            'info': {'type':'s', 'required':1},
        }
        
        ret = self._args_handle('insert', fields, user_config)   
        if not ret[0]:
            # todo:
            print ret[1]
            return ret
        return self._replace(self._table, user_config)
    
    def mod(self, kwarg):
        return self._mod(kwarg)
    
    # 获取用户某config
    def detail(self, uid, config_name):
        fields = "`uid`,`name`,`info`"
        where = "uid=%d and `name`='%s' " % (int(uid), config_name)
        sql = "select %s from %s where %s" % (fields, self._table, where)
        return self.get_one(sql)
