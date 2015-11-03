#!/usr/bin/env python2.7
#-*- coding:utf8 -*-
#
# 2013-12-4 by Victor
# Copyright 2013 Tubban

from _module import const
from _module._lib.common import Common
from _module._lib.lang import Lang
from _module._lib.log import Log
from _module._lib.mem import Mem
from _module.business.model import BusinessModel
from _module.carte.model import CarteModel
from _module.dish.model import DishModel
from _module.dishgroup.model import DishgroupModel
from _module.image.model import ImageModel
from _module.name.control import NameControl
from _module.name.model import NameModel
from _module.price.model import PriceModel
from _module.sys_data.model import SysdataModel

class DishControl:
    def __init__(self, uid = None, userLang=None):
        self._uid = uid
        self._bModel = BusinessModel(self._uid)
        self._dModel = DishModel(self._uid)
        self._dgModel = DishgroupModel(self._uid)
        self._pModel = PriceModel(self._uid)
        self._cModel = CarteModel(self._uid)
        self._sysDataModel = SysdataModel()
        self._nModel = NameModel()
        self._imageModel = ImageModel(self._uid)
        self._language_id = None
        self._field = Lang.get_db_field_name(userLang)
        self._langcode = Lang.get_code_by_req_code(userLang)
        self._nameControl = NameControl()

    def get_by_id(self, id):
        return self._dModel.get_by_id(id)
    
    def like(self, uid, dish_id, remote_ip=''):
        key = "DL_%d_%d_%s" % (uid, dish_id, remote_ip)
        if not uid or uid == 0:
            if Mem.get(key):
                return False
        else:
            if self._dModel.has_like(uid, dish_id):
                return False
        if self._dModel.add_like(uid, dish_id):
            Mem.set(key, 1)
            return True
        else:
            return False
        
    def del_like(self, uid, dish_id, remote_ip=''):
        key = "DL_%d_%d_%s" % (uid, dish_id, remote_ip)
        if not uid or uid == 0:
            Mem.delete(key)
            
        if uid <> 0 and self._dModel.has_like(uid, dish_id):
            return self._dModel.remove_like(uid, dish_id)
        return True
    
    """
    Func: 判断是否已点赞。未登录用户用ip判断，登录用户从数据库中判断
    """
    def has_like(self, uid, dish_id, remote_ip=''):
        key = "DL_%d_%d_%s" % (uid, dish_id, remote_ip)
        if not uid or uid == 0:
            if Mem.get(key):
                return True
            
        if uid <> 0 and self._dModel.has_like(uid, dish_id):
            return True
        return False
    
    def get_by_number(self, carteid, number):
        return  self._dModel.get_by_number(carteid, number)
    
    def get_brief_recommend_by_restaurant(self, restid, limit=10, fields=None):
        dishes = self._dModel.get_brief_recommend_by_restaurant(restid, limit, fields)
        for one in dishes:
            name = self._nameControl.get_one(one['name'], self._langcode)
            one['name_i18n'] = ''
            if name.has_key(self._langcode):
                one['name_i18n'] = name[self._langcode]
        return dishes
    
    def get_recommend_by_restaurant(self, rest, limit=10):
        return  self._dModel.get_recommend_by_restaurant(rest, limit)
    def get_noRecommendButHasCoverDish(self, rest, limit=10):
        return  self._dModel.get_noRecommendButHasCoverDish(rest, limit)
    def get_noRecommendNoCoverDish(self, rest, limit=10):
        return  self._dModel.get_noRecommendNoCoverDish(rest, limit)
    
    def get_products_by_restaurant(self,rest,num):
        recommendDish = self.get_recommend_by_restaurant(rest,num)
        if len(recommendDish)<num:
            num1 = num-len(recommendDish)
            noRecommendButHasCoverDish = self.get_noRecommendButHasCoverDish(rest,num1)
            recommendDish = recommendDish + noRecommendButHasCoverDish
            if len(noRecommendButHasCoverDish)<num1:
                num2 = num1 - len(noRecommendButHasCoverDish)
                noRecommendNoCoverDish = self.get_noRecommendNoCoverDish(rest,num2)
                recommendDish = recommendDish + noRecommendNoCoverDish
        list = []
        for one in recommendDish:
            list.append(self._detail(one))
        return list
    
    
    def get_brief_all_list_by_restaurant(self, rid):
        return self._dModel.get_brief_all_list_by_restaurant(rid)
    
    # 带详细信息的推荐菜品方法
    def get_recommend_list(self, business_id, limit=10):
        _list = self._dModel.get_recommend_by_restaurant(business_id, limit)
        list = []
        for l in _list:
            list.append(self._brief_detail(l))
            #l['price'] = self._pModel.get_by_target(const.Price.TYPE_DISH, l['id'], self._field)
        return list
    
    """
    Func : 获取在某菜单中所有的菜品，按类别返回
    Author: Victor
    Date:2014-01-26
    """
    def get_list_by_carte(self, carte_id, visible=None):
        # 获取所有菜品类别
        types = self._dgModel.get_list_by_carte(carte_id, visible)
        for t in types:
            t['name_i18n'] = ''
            try:
                if t['refer_id']<>0:
                    t['name_i18n'] = self._dgModel.get_sys_by_id(t['refer_id'], self._field)['name']
                    t['name'] = t['name_i18n']
                else:
                    t['name_i18n'] = ''
                    name = self._nameControl.get_one(t['name'], self._langcode)
                    if name.has_key(self._langcode):
                        t['name_i18n'] = name[self._langcode]

            except Exception, e:
                pass
            t['dishes'] = []
            list = self._dModel.get_list(carte_id, t['id'], visible)
            for l in list:
                l = self._detail(l)
                t['dishes'].append(l)
        return types
    
    def get_list_by_dishgroup(self, carte_id, dishgroup_id, visible=None):
        _list = self._dModel.get_list(carte_id, dishgroup_id, visible)
        list = []
        for l in _list:
            list.append(self._detail(l))
            #l['price'] = self._pModel.get_by_target(const.Price.TYPE_DISH, l['id'], self._field)
        return list
    
    def add(self, dish):
        ret = self._dModel.add(dish)
        if not ret[0]:
            return ret
        # 更新name_dict数据库
        if not self._nModel.is_name_exist(dish['name']):
            self._nModel.add({"name": dish['name']})
        # 更新business版本
        self._bModel.update_menu_version(dish.get('restaurant_id',0)) 
        return ret
    
    def mod(self,dish):
        dishid = dish['id']
        _old = self.get_by_id(dishid)
        ret = self._dModel.mod(dish)
        if ret:
            if dish.has_key('cover') and len(dish['cover'])>0:
                cover = _old['cover']
                if cover<>dish['cover']:
                    # 新添加封面
                    # Common.remove_file(cover)
                    self._imageModel.del_tmp(cover)
                    self._imageModel.del_tmp(dish['cover'])
        # 更新name_dict数据库
        if dish.has_key('name') and not self._nModel.is_name_exist(dish['name']):
            self._nModel.add({"name": dish['name']})
        # 更新business版本
        self._bModel.update_menu_version(_old.get('restaurant_id',0))  
        return ret
    
    def _brief_detail(self, _dish):
        dish = _dish
        dish['name_i18n'] = ''
        name = self._nameControl.get_one(_dish['name'], self._langcode)
        if name.has_key(self._langcode):
            dish['name_i18n'] = name[self._langcode]

        portion_unit = self._sysDataModel.get_portionunit_by_id(_dish['price_unit'], self._field)
        if not portion_unit:
            portion_unit = self._sysDataModel.get_portionunit_by_id(101, self._field)
        portion_unit_name = portion_unit['name']
        dish['price'] = {"price":_dish['price'], 
                         "num": _dish['price_num'],
                         "portionunit_id": _dish['price_unit'],
                         "portionunit_name": portion_unit_name}
        del dish['price_num']
        del dish['price_unit']
        return dish
    
    def _detail(self, _dish):
        dish = _dish
        dish['name_i18n'] = ''
        name = self._nameControl.get_one(_dish['name'])
        if name.has_key(self._langcode):
            dish['name_i18n'] = name[self._langcode]

        # 封面
        dish['refer_cover'] = ''
        if dish['cover'] == '' and name.has_key('cover'):
            dish['refer_cover'] = name['cover']

        # 食材等，暂时不提供，为了兼容之前，暂时改为返回空
        dish['ingredient_ids'] = _dish['ingredient']
        dish['ingredient'] = []
        """
        if dish['ingredient_ids'].strip() <> '':
            dish['ingredient'] = self._sysDataModel.get_ingredient(_dish['ingredient'], self._field)
        else:
            dish['ingredient'] = []
        """
            
        dish['cooktechnique_ids'] = _dish['cooktechnique']
        dish['cooktechnique'] = []
        """
        if dish['cooktechnique_ids'].strip() <> '':
            dish['cooktechnique'] = self._sysDataModel.get_cooktechnique(_dish['cooktechnique'], self._field)
        else:
            dish['cooktechnique'] = []
        """
            
        dish['mouthfeel_ids'] = _dish['mouthfeel']
        dish['mouthfeel'] = []
        """
        if dish['mouthfeel_ids'].strip() <> '':
            dish['mouthfeel'] = self._sysDataModel.get_mouthfeel(_dish['mouthfeel'], self._field)
        else:
            dish['mouthfeel'] = []
        """
            
        #dish['sortrank'] = _dish['sortrank']
        portion_unit = self._sysDataModel.get_portionunit_by_id(_dish['price_unit'], self._field)
        if not portion_unit:
            portion_unit = self._sysDataModel.get_portionunit_by_id(101, self._field)
        portion_unit_name = portion_unit['name']
        dish['price'] = {"price":_dish['price'], 
                         "num": _dish['price_num'],
                         "portionunit_id": _dish['price_unit'],
                         "portionunit_name": portion_unit_name}
        del dish['price_num']
        del dish['price_unit']
        return dish
    
    def get_detail(self, id):
        """
        {
            'carte_id':1, # 所属菜单id
            'dishgroup_id':1, # 菜品组id
            'number':'菜品编号', # 菜品编号，例：001，当is_type为1时必填，is_type为0时不用传
            'name':'菜品名称', # 菜品名称
            'ingredient':[ # 材料
                {
                    "id":1,
                    "name":"Chicken",
                 },
                # ...
            ], 
            'cooktechnique':[ # 材料
                {
                    "id":1,
                    "name":"Chicken",
                 },
                # ...
            ],
            'mouthfeel':[ # 材料
                {
                    "id":1,
                    "name":"Chicken",
                 },
                # ...
            ],
            'price':
                {
                    'price_num':1,
                    'price':10.0, # 价格
                    'price_unit':1,
                }
        }
        """
        _dish = self._dModel.get_detail(id)
        if not _dish:
            return None
        dish = self._detail(_dish)
        return dish
                
    def delete(self, id):
        _dish = self._dModel.get_detail(id)
        if not _dish:
            return False
        if not self._dModel.delete(id):
            return False
        #self._rtModel.delete_by_ids(_dish['tag'])
        #self._pModel.delete_by_target(const.Price.TYPE_DISH, _dish['id'])
        # 更新business版本
        self._bModel.update_menu_version(_dish.get('restaurant_id',0)) 
        return True
    
    def delete_by_carte_source_id(self, sf_id):
        list = self._dModel.get_list_by_source_carte_id(sf_id)
        for l in list:
            self.delete(l['id'])
        return True
    
    def get_carte_id(self,dishid):
        return self._dModel.get_carte_id(dishid)
    
    def get_restaurant_id(self,dishid):
        carte_id = self.get_carte_id(dishid)
        if carte_id:
            return self._cModel.get_restaurant_id(carte_id)
        else:
            return None

    def get_price(self,dishid):
        return self._pModel.get_by_target(const.Price.TYPE_DISH, dishid, self._field)
    
    def recommended(self,dishid,recommended):
        _dish = self._dModel.get_by_id(dishid)
        if not _dish:
            return False
        # 更新business版本
        if self._dModel.set_recommend(dishid, recommended)[0]:
            self._bModel.update_menu_version(_dish.get('restaurant_id',0))  
            return True
        return False
    
    def set_order(self,orderIds):
        return self._dModel.set_order(orderIds)
    
        
    
    