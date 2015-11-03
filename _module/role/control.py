#!/usr/bin/env python2.7
#-*- coding:utf8 -*-
#
# 2014-2-9 by Victor
# Copyright 2014 Tubban
from _module import const
from _module._lib.lang import Lang
from _module.business.model import BusinessModel
from _module.employee.model import EmployeeModel
from _module.role.model import RoleModel

class RoleControl:
    def __init__(self, uid = None,userLang=None):
        self._uid = uid
        self._bModel = BusinessModel(self._uid)
        self._eModel = EmployeeModel(self._uid)
        self._roleModel = RoleModel(self._uid)
        self._field = Lang.get_db_field_name(userLang)
    def get_role_by_creator(self, creator, business_category = None):
        role_type = None
        if not business_category:
            if business_category==const.Business.CATEGORY_RESTAURANT:
                role_type = const.Role.TYPE_RESTAURANT
            elif business_category==const.Business.CATEGORY_HOTEL:
                role_type = const.Role.TYPE_HOTEL
            elif business_category==const.Business.CATEGORY_SHOP:
                role_type = const.Role.TYPE_SHOP
        return self._roleModel.get_list_by_creator(creator, role_type)
    
    def get_by_id(self, id):
        return self._roleModel.get_by_id(id)
        