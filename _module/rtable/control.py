#!/usr/bin/env python2.7
#-*- coding:utf8 -*-
#
# 2015-04-12 by Victor
# Copyright 2014 Tubban
from _module._lib.lang import Lang
from _module.rtable.model import RTableModel

class RTableControl:
    def __init__(self, uid = None, userLang=None):
        self._uid = uid
        self._tModel = RTableModel(self._uid)
        self._field = Lang.get_db_field_name(userLang)
        self._langcode = Lang.get_code_by_req_code(userLang)
    
    #-------------------Base Functions For All-----------------------
    """
    Func: 
    @param rtable: {"r_id":1, "number":2}
    """
    def add(self, rtable):
        if self.is_table_exist(rtable['r_id'], rtable['number']):
            return False
        return self._tModel.add(rtable)[0]
    
    def add_by_range(self, r_id, from_number, to_number):
        if from_number > to_number:
            return False
        cnt = self.get_restaurant_table_cnt(r_id)
        if to_number - from_number + cnt >= 200:
            return False
        
        for number in range(from_number, to_number+1):
            if not self.is_table_exist(r_id, number):
                self._tModel.add({"r_id": r_id, "number": number})
        return True
    
    def is_table_exist(self, r_id, table_id):
        return self._tModel.is_table_exist(r_id, table_id)
    
    def get_restaurant_table_cnt(self, r_id):
        return self._tModel.get_restaurant_table_cnt(r_id)
    
    def get_all_by_restaurant(self, r_id):
        return self._tModel.get_all_by_restaurant(r_id)
        
    def delete(self, r_id, number):
        return self._tModel.delete(r_id, number)
    
    #-------------------Super Functions Only For Operators-----------