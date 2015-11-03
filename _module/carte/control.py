#!/usr/bin/env python2.7
#-*- coding:utf8 -*-
#
# 2013-12-4 by Victor
# Copyright 2013 Tubban
from _module import const
from _module._lib.common import Common
from _module._lib.lang import Lang
from _module.business.model import BusinessModel
from _module.carte.model import CarteModel, CarteSourceModel
from _module.dish.control import DishControl
from _module.dishgroup.control import DishgroupControl
from _module.restaurant.control import RestaurantControl
from _module.restaurant.model import RestaurantModel
from _module.sys_data.model import SysdataModel

class CarteControl:
    def __init__(self, uid = None, userLang=None):
        
        self._uid = uid
        self._rModel = RestaurantModel(self._uid)
        self._bModel = BusinessModel(self._uid)
        self._cModel = CarteModel(self._uid)
        self._sysDataModel = SysdataModel()
        self._field = Lang.get_db_field_name(userLang)
        
        self._rControl = RestaurantControl(self._uid)
                
    def get_by_id(self,cid,lang=None):
        carte = self._cModel.get_by_id(cid,self._field)
        return carte
    
    def get_by_restaurant_and_syscarte(self, rid, sys_carte_id):
        sys_carte = self._sysDataModel.get_sys_carte_by_id(sys_carte_id)
        if not sys_carte:
            return None
        carte = self._cModel.get_by_restaurant_and_syscarte(rid, sys_carte_id)
        if not carte:
            carte = {}
            carte['restaurant_id'] = rid
            carte['name'] = sys_carte['name']
            carte['type_id'] = sys_carte_id
            ret = self.add(carte)
            carte['id'] = ret[1]
        return carte
    
    def get_detail(self, id, language_id=None):
        _carte = self.get_by_id(id)
        if not _carte:
            return {}
        carte = {}
        carte['id'] = _carte['id']
        carte['name'] = _carte['name']
        tag = [] #self._rtModel.get_list(_carte['tag'], language_id, RestaurantTagModel.TYPE_CARTE)
        carte['tag'] = tag
        return carte
    
    def add(self, carte, tags=[]):
        tagids = []
        for tag in tags:
            ret = self._rtModel.add(tag)
            if ret[0]:
                tagids.append(str(ret[1]))
        carte['tag'] = ','.join(tagids)
        carte['add_time'] = Common.get_current_time()
        carte['version'] = Common.get_current_time()
        ret = self._cModel.add(carte)
        if ret[0]:
            self._rControl.update_menu_num(carte.get('restaurant_id',0))
            self._bModel.update_menu_version(carte.get('restaurant_id',0))
        return ret
    
    def mod(self, carte):
        ret = self._cModel.mod(carte)
        if not ret:
            return False
        carte = self._cModel.get_by_id(carte['id'])
        self._bModel.update_menu_version(carte.get('restaurant_id',0))
        return True
    
    def edit(self,db):
        pass
 
    def get_list(self, business_id, lang=None):
        _list = self._cModel.get_list_by_restid(business_id,self._field)
        list = []
        for _carte in _list:
            carte = {}
            carte['id'] = _carte['id']
            carte['type_id'] = _carte['type_id']
            carte['name'] = _carte['name']
            #tag = self._rtModel.get_list(_carte['tag'], language_id, RestaurantTagModel.TYPE_CARTE)
            #carte['tag'] = tag
            list.append(carte)
        return list
    
    
    
    #获取餐单详情（包含菜，类别，套餐信息）
    def get_carte_detail(self, carte_id, lang=None):
        carte={}
        carte['carte'] = self.get_by_id(carte_id,self._field)
        dgc =  DishgroupControl(self._uid,self._field)
        dishtype = dgc.get_list_by_carte(carte_id)
        carte['dishtype'] = dishtype
        dc = DishControl(self._uid,self._field)
        dishes={}
        for one in dishtype:
            one['name'] = dgc.get_name_by_id(one['refer_id'],self._field)
            dish_in_type = dc.get_list_by_dishgroup(carte_id, one['id'])
            dished =[]
            for item in dish_in_type:
                item1 = dc.get_detail(item['id'])
                dished.append(item1) 
            #print dish_in_type
            dishes[one['id']] = dished
        carte['dish'] = dishes
        """
                       套餐信息暂时挂起
        sc = SetmealControl(self._uid,self._field)
        setmeal = sc.get_list(carte_id)
        for one in setmeal:
            dishgroups = dgc.get_list_by_setmeal(one['id'])
            for item in dishgroups:
                dish_in_setmeal = dc.get_list_by_dishgroup(carte_id, one['id'])
            
        """
        return carte
    
    
    #获取餐单所属的餐馆
    def get_restaurant_by_id(self, carte_id):
        rest = self._cModel.get_restaurant_by_id(carte_id)
        if rest:
            return rest['restaurant_id']
        else:
            return None
        
    # 自定义菜单排序
    def set_order(self,orderIds):
        return self._cModel.set_order(orderIds)
        
class CarteSourceControl:
    def __init__(self, uid = None, userLang=None):
        
        self._uid = uid
        self._csModel = CarteSourceModel(self._uid)
        self._dControl = DishControl(self._uid)
        self._field = Lang.get_db_field_name(userLang)
                
    def add(self, cartesource):
        return self._csModel.add(cartesource)
    
    def get_list(self, business_id):
        _list = self._csModel.get_list_by_restid(business_id)
        return _list
    
    def change_status(self, id, status):
        ret = self._csModel.change_status(id, status)
        if not ret:
            return False
        if status == const.CarteSource.STATUS_UNHANDLED:
            self._dControl.delete_by_carte_source_id(id)
        return True
    
    def get_by_id(self, id):
        return self._csModel.get_by_id(id)
    
    def get_by_pure_name(self, name):
        return self._csModel.get_by_pure_name(name)
    
    def get_pager_list(self, pager, status=None, key=None):
        return self._csModel.get_pager_list(pager, status, key)
    
    def find_next_num(self, rid):
        source = self._csModel.find_last(rid)
        if not source:
            return 1
        else:
            a1 = source['md5_file'].split('_')
            if len(a1)<=1:
                return 1
            else:
                return int(a1[1].split('.')[0]) + 1