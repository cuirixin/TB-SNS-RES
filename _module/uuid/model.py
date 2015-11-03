#!/usr/bin/env python2.7
#-*- coding:utf8 -*-
#
# 2014-3-13 by Victor
# Copyright 2014 Tubban
from _module._base_m_ import BaseModel

class UUIDModel(BaseModel):
    
    def __init__(self, uid = None):
        self._uid = uid
        self._uuid_table = 'uuid'
    
    def add(self, uuid):
        sql = "INSERT INTO %s(`uuid`) VALUES('%s')" % (self._uuid_table, uuid)
        return self.execute(sql)   

    def get_uuid_by_id(self, id):
        sql = "SELECT `uuid` FROM %s WHERE id=%d " \
                %(self._uuid_table, id)
        return self.get_one(sql)['uuid']
    
    def is_uuid_exist(self, uuid):
        sql = "SELECT id FROM %s WHERE `uuid`='%s' LIMIT 1" \
                %(self._uuid_table, uuid) 
        if self.get_one(sql):
            return True
        return False
