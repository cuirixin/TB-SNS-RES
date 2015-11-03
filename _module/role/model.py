#!/usr/bin/env python2.7
#-*- coding:utf8 -*-
#
# 2014-2-9 by Victor
# Copyright 2014 Tubban
from _module._base_m_ import BaseModel
from _module import const

class RoleModel(BaseModel):
    
    def __init__(self, uid = None):
        self._sys_role_table = 'sys_role'
        self._auth_role_table = 'auth_role'
        self._uid = uid
        
    def copy_sys_to_auth(self, creator):
        sql = "insert into %s(`name`,`type`,`creator`,`perms`, `status`) " \
                " select `name`,`type`, %d ,`perms`, %d from %s " \
                % (self._auth_role_table, creator, const.Role.STATUS_VALID, self._sys_role_table)
        ret = self.execute(sql)
        return ret[0]

    def add(self, role):
        pass
    
    def get_by_id(self, id):
        sql = "select * from %s where id=%d" % (self._auth_role_table, id)
        return self.get_one(sql)
    
    def get_list_by_creator(self, creator, type=None):
        sql = "SELECT id, type, name, status FROM %s WHERE creator=%d " \
                % (self._auth_role_table, creator)
        if type:
            sql += " and type=%d " % type
        return self.get_rows(sql)
        