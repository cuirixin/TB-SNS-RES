#!/usr/bin/env python2.7
#-*- coding:utf8 -*-
#
# 2015-04-12 by Victor
# Copyright 2015 Tubban
from _module import const
from _module._base_m_ import BaseModel
from _module._lib.common import Common

class RTableModel(BaseModel):
    
    def __init__(self, uid = None):
        self._rtable_table = "r_table"
        self._uid = uid
    
    def is_table_exist(self, r_id, table_numer):
        table = self._get_mo_split_table(r_id, self._rtable_table, const.DB.R_TABLE_SPLIT)
        sql = "SELECT count(1) as total FROM %s WHERE r_id=%d AND number=%d" % (table, r_id, table_numer)
        if self.get_one(sql)['total'] == 0:
            return False
        return True
    
    def add(self, fields):
        table = self._get_mo_split_table(fields['r_id'], self._rtable_table, const.DB.R_TABLE_SPLIT)
        rtable = {
            'r_id': {'type':'d'},
            'number': {'type':'d'},
        }
        
        ret = self._args_handle('insert', fields, rtable)               
        if not ret[0]:
            return ret
        return self._insert(table, rtable)
    
    def delete(self, r_id, number):
        table = self._get_mo_split_table(r_id, self._rtable_table, const.DB.R_TABLE_SPLIT)
        sql = "DELETE FROM %s WHERE r_id=%d AND number=%d" % (table, r_id, number)
        return self.execute(sql)[0]
    
    def get_restaurant_table_cnt(self, r_id):
        table = self._get_mo_split_table(r_id, self._rtable_table, const.DB.R_TABLE_SPLIT)
        sql = "SELECT count(1) as total FROM %s WHERE r_id=%d" % (table, r_id)
        return self.get_one(sql)['total']
    
    def get_all_by_restaurant(self, r_id):
        table = self._get_mo_split_table(r_id, self._rtable_table, const.DB.R_TABLE_SPLIT)
        sql = "SELECT r_id, `number` FROM %s WHERE r_id=%d ORDER BY number asc limit 200" % (table, r_id)
        return self.get_rows(sql)
        
        
        
        
    