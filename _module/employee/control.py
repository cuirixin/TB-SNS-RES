#!/usr/bin/env python2.7
#-*- coding:utf8 -*-
#
# 2014-2-9 by Victor
# Copyright 2014 Tubban
from _module._lib.lang import Lang
from _module.business.model import BusinessModel
from _module.employee.model import EmployeeModel
from _module.user.model import UserModel

class EmployeeControl:
    def __init__(self, uid = None,userLang=None):
        self._uid = uid
        self._bModel = BusinessModel(self._uid)
        self._eModel = EmployeeModel(self._uid)
        self._uModel = UserModel(self._uid)
        self._field = Lang.get_db_field_name(userLang)
        
    def get_list_by_business(self, business_id):
        return self._eModel.get_list(business_id)
    
    def add(self, user, employee, creator):
        ret = self._uModel.add(user, creator)
        if not ret[0]:
            return ret
        uid = ret[1]
        employee['uid'] = uid
        self._eModel.add(employee)
        return ret
    
    def add_employee(self,users):
        if users:
            for one in users:
                ret = self._uModel.add(one[0])
                if not ret[0]:
                    return ret[0]
                uid = ret[1]
                one[1]['uid'] = uid
                self._eModel.add(one[1])
        return True
                
    
    def get_detail(self, uid):
        return self._eModel.get_detail(uid)
        
    def mod(self, user, employee):
        if not self._uModel.mod(user):
            return False
        return self._eModel.mod(employee)
        
    def delete(self, uid):
        if not self._uModel.delete(uid):
            return False
        return self._eModel.delete(uid)
