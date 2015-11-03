#!/usr/bin/env python2.7
#-*- coding:utf8 -*-
#
# 2014-2-9 by Victor
# Copyright 2014 Tubban
from _module import const
from _module._lib.common import Common
from _module._lib.lang import Lang
from _module.beverage.model import BeverageModel
from _module.business.model import BusinessModel
from _module.image.model import ImageModel
from _module.name.control import NameControl
from _module.price.model import PriceModel
from _module.user.model import UserModel

class BeverageControl:
    def __init__(self, uid = None,userLang=None):
        self._uid = uid
        self._bModel = BusinessModel(self._uid)
        self._pModel = PriceModel(self._uid)
        self._brgModel = BeverageModel(self._uid)
        self._uModel = UserModel(self._uid)
        self._imageModel = ImageModel(self._uid)
        self._field = Lang.get_db_field_name(userLang)
        self._langcode = Lang.get_code_by_req_code(userLang)
    
    def get_categories(self, parent=None):
        return self._brgModel.get_categories(self._field, parent)
    
    """
    Function： 如果category为0，返回参观下所有有酒水的类别以及各类别下的酒水列表信息，如果不为0返回此类别下酒水列表
    """
    def get_list_by_business(self, business_id, category):
        if category<>0:
            list = self._brgModel.get_list(business_id, category, self._field)
            for l in list:
                l['name_i18n'] =  ''
                name = NameControl().get_one(l['name'], self._langcode)
                if name.has_key(self._langcode):
                    l['name_i18n'] = name[self._langcode]
                l['price'] = self._pModel.get_by_target(const.Price.TYPE_BEVERAGE, l['id'], self._field)
            return list
        else:
            categories = self.get_beverage_categories(business_id)
            for one in categories:
                one['beverage_list'] = []
                list = self._brgModel.get_list(business_id, one['id'], self._field)
                for l in list:
                    l['name_i18n'] = ''
                    name = NameControl().get_one(l['name'], self._langcode)
                    if name.has_key(self._langcode):
                        l['name_i18n'] = name[self._langcode]
                    l['price'] = self._pModel.get_by_target(const.Price.TYPE_BEVERAGE, l['id'], self._field)
                    one['beverage_list'].append(l)
            return categories
    
    """
    Function： 获取某餐馆中所有“创建有酒水”的酒水类别
    """
    def get_beverage_categories(self, business_id):
        return self._brgModel.get_categories_by_business(business_id, self._field)
    
    def add(self, beverage, prices):
        ret = self._brgModel.add(beverage)
        if not ret[0]:
            return ret
        beverageid = ret[1]
        # 添加封面
        if beverage.has_key('cover') and len(beverage['cover'])>0:
            self._imageModel.del_tmp(beverage['cover'])
        # 添加价格
        for price in prices:
            price['target_type'] = const.Price.TYPE_BEVERAGE
            price['target_id'] = beverageid
            _ret = self._pModel.add(price)
            
        return ret
    
    def get_detail(self, id):
        _beverage = self._brgModel.get_detail(id)
        beverage = _beverage
        beverage['price'] = self._pModel.get_by_target(const.Price.TYPE_BEVERAGE, id, self._field)
        beverage['name_i18n'] = ''
        name = NameControl().get_one(beverage['name'], self._langcode)
        if name.has_key(self._langcode):
            beverage['name_i18n'] = name[self._langcode]
        return beverage
        
    def mod(self, beverage, prices=[]):
        _old = self.get_detail(beverage['id'])
        ret = self._brgModel.mod(beverage)
        if ret:
            if beverage.has_key('cover') and len(beverage['cover'])>0:
                cover = _old['cover']
                if cover<>beverage['cover']:
                    # 新添加封面
                    Common.remove_file(cover)
                    self._imageModel.del_tmp(beverage['cover'])
            if len(prices)>0:
                self._pModel.delete_by_target(const.Price.TYPE_BEVERAGE, beverage['id'])
                for price in prices:
                    price['target_id'] = beverage['id']
                    price['target_type'] = const.Price.TYPE_BEVERAGE
                    _ret = self._pModel.add(price)
        return ret
        
    def delete(self, id):
        if not self._brgModel.delete(id):
            return False
        return self._pModel.delete_by_target(const.Price.TYPE_BEVERAGE, id)
    
    def get_price(self,bevId):
        return self._pModel.get_by_target(const.Price.TYPE_BEVERAGE, bevId, self._field)
