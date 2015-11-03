#!/usr/bin/env python2.7
#-*- coding:utf8 -*-
#
# 2013-12-4 by Victor
# Copyright 2013 Tubban
from _module._lib.common import Common
from _module._lib.lang import Lang
from _module.business.model import BusinessModel
from _module.carte.model import CarteModel
from _module.dish.model import DishModel
from _module.dishgroup.model import DishgroupModel
from _module.name.control import NameControl
from _module.restaurant.model import RestaurantModel
from _module.sys_data.model import SysdataModel

class DishgroupControl:
    def __init__(self, uid = None, userLang=None):
        self._uid = uid
        self._rModel = RestaurantModel(self._uid)
        self._bModel = BusinessModel(self._uid)
        self._cModel = CarteModel(self._uid)
        self._dgModel = DishgroupModel(self._uid)
        self._dModel = DishModel(self._uid)
        self._sysDataModel = SysdataModel()
        self._field = Lang.get_db_field_name(userLang)
        self._langcode = Lang.get_code_by_req_code(userLang)
    
    def get_by_id(self,dgid):
        return self._dgModel.get_by_id(dgid)
    
    def get_by_restaurant_and_sysdishgroup(self, rid, sys_dishgroup_id):
        sys_dishgroup = self.get_sys_by_id(sys_dishgroup_id)
        if not sys_dishgroup:
            return None
        dishgroup = self._dgModel.get_by_restaurant_and_sysdishgroup(rid, sys_dishgroup_id)
        if not dishgroup:
            dishgroup = {}
            dishgroup['restaurant_id'] = rid
            dishgroup['name'] = sys_dishgroup['name']
            dishgroup['refer_id'] = sys_dishgroup_id
            dishgroup['visible'] = 1
            dc = DishgroupControl()
            ret = dc.add(dishgroup, [])
            dishgroup['id'] = ret[1]
        return dishgroup
    
    def get_sys_by_id(self, dgid):
        return self._dgModel.get_sys_by_id(dgid, self._field)
    
    def get_detail(self, id, language_id=None):
        _dishgroup = self.get_by_id(id)
        if not _dishgroup:
            return {}
        dishgroup= {}
        dishgroup['id'] = _dishgroup['id']
        dishgroup['refer_id'] = _dishgroup['refer_id']
        dishgroup['visible'] = _dishgroup['visible']
        # TODO 改成国际化语言
        dishgroup['name'] = _dishgroup['name']
        #国际化语言
        dishgroup['name_i18n'] = ''
        try:
            if dishgroup['refer_id']<>0:
                dishgroup['name_i18n'] = self._sysDataModel.get_dishgoup_by_id(dishgroup['refer_id'], self._field)['name']
                dishgroup['name'] = dishgroup['name_i18n']
            else:
                name = NameControl().get_one(dishgroup['name'], self._langcode)
                if name.has_key(self._langcode):
                    dishgroup['name_i18n'] = name[self._langcode]
        except Exception, e:
            pass

        return dishgroup
    
    def get_list(self, business_id, is_type=None, language_id=None, visible=None):
        _list = self._dgModel.get_list_by_restid(business_id,self._field, visible)
        list = []
        for _dishgroup in _list:
            dishgroup= {}
            dishgroup['id'] = _dishgroup['id']
            dishgroup['refer_id'] = _dishgroup['refer_id']
            dishgroup['visible'] = _dishgroup['visible']
            dishgroup['sortrank'] = _dishgroup['sortrank']
            #国际化语言
            dishgroup['name'] = _dishgroup['name']
            dishgroup['name_i18n'] = ''
            try:
                if dishgroup['refer_id']<>0:
                    dishgroup['name_i18n'] = self._sysDataModel.get_dishgoup_by_id(dishgroup['refer_id'], self._field)['name']
                    dishgroup['name'] = dishgroup['name_i18n']
                else:
                    name = NameControl().get_one(dishgroup['name'], self._langcode)
                    if name.has_key(self._langcode):
                        dishgroup['name_i18n'] = name[self._langcode]
            except Exception, e:
                pass
            #
            list.append(dishgroup)
        return list

    
    """
    Func : 获取在某菜单中所有的菜品类别
    Author: Victor
    Date:2014-01-26
    """
    def get_list_by_carte(self, carte_id, visible=None):
        return self._dgModel.get_list_by_carte(carte_id, visible)
    
    def get_recommend_list(self, restaurant_id):
        restaurant = self._rModel.get_by_id(restaurant_id)
        cuisine_style = Common.filter_comma_ids(restaurant['cuisine_style'])
        return self._dgModel.get_recommend_list_by_cuisine_style(cuisine_style, self._field)
    
    """
    refer_id      int 对应的sys_dishgroup ID
    name          str 名称，默认名称
    restaurant_id int 餐馆id
    visible       int 是否可见
    """
    def add(self, dishgroup, tags=[]):
        dishgroup['add_time'] = Common.get_current_time()
        self._bModel.update_menu_version(dishgroup.get('restaurant_id',0))
        return self._dgModel.add(dishgroup)
    
    def add_by_recommend(self, restaurant_id, ids):
        return self._dgModel.copy_sys_to_mine(restaurant_id, ids)
    
    def mod(self, dishgroup):
        ret = self._dgModel.mod(dishgroup)
        if not ret:
            return False
        dishgroup = self._dgModel.get_by_id(dishgroup['id'])
        self._bModel.update_menu_version(dishgroup.get('restaurant_id',0))
        return True

    def delete(self, id):
        _dishgroup = self.get_detail(id)
        if not _dishgroup:
            return True
        # 如果有关联菜品则不允许删除
        if len(self._dModel.get_list(None, _dishgroup['id'])) > 0:
            return False
        
        if not self._dgModel.delete(id):
            return False
        
        # 更新business版本
        self._bModel.update_menu_version(_dishgroup.get('restaurant_id',0))        
        return True
    
    def set_order(self,orderIds):
        return self._dgModel.set_order(orderIds)
    
    def verify_added(self,rid,dgid):
        return self._dgModel.verify_added(rid,dgid)
    
    def get_name_by_id(self,ref_id,lang):
        return self._dgModel.get_name_by_id(ref_id,lang)
