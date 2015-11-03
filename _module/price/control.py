#!/usr/bin/env python2.7
#-*- coding:utf8 -*-
#
# 2014-5-8 by Victor
# Copyright 2014 Tubban

from _module._lib.lang import Lang
from _module.price.model import PriceModel
from _module.sys_data.model import SysdataModel

class PriceControl:
    def __init__(self, uid = None, userLang=None):
        self._uid = uid
        self._priceModel = PriceModel(self._uid)
        self._field = Lang.get_db_field_name(userLang) # zh_CN => CN
        self._langcode = Lang.get_code_by_req_code(userLang) # zh_CN => zh
        self._sysDataModel = SysdataModel()
    
    def add(self, price):
        return self._priceModel.add(price)
    
    def mod(self, price):
        return self._priceModel.mod(price)
      
    def delete(self, id):
        return self._priceModel.delete_by_id(id) 
    
    """
    Func: 根据价格所属实体的类型和ID获取价格信息， 不包括关联信息和国际化语言信息
    Date: 2015-04-10
    @param target_type: int 实体类型， 1 - TYPE_DISH、 3 - TYPE_BEVERAGE
    @param target_id: int 实体ID
    """
    def get_brief_prices_by_target(self,  target_type, target_id):
        prices = self._priceModel.get_brief_by_target(target_type, target_id)
        if len(prices) == 0:
            return []
        currency_id = prices[0]['currency_id']
        currency = self._sysDataModel.get_currency(currency_id, self._field)
        if not currency:
            return []
        for price in prices:
            price['currency_iso_code'] = currency['iso_code']
        return prices
        
    """
    Func: 根据ID获取价格信息， 不包括关联信息
    Date: 2015-04-10
    @param id: int 
    @param field: string 语言字段
    """
    def get_brief_price_by_id(self, id):
        return self._priceModel.get_brief_by_id(id)
    
    
    def get_detail_price_by_id(self, id):
        price = self._priceModel.get_brief_by_id(id)
        if not price:
            return None
        price['currency'] = self._sysDataModel.get_currency(price['currency_id'], self._field)
        price['portionunit'] = self._sysDataModel.get_portionunit_by_id(price['portionunit_id'], self._field)
        del price['currency_id']
        del price['portionunit_id']
        return price
    
    """
    def add(self, order, dishes):
        ret = self._oModel.add(order)
        if not ret[0]:
            return ret
        order_id = ret[1]
        self._oModel.add_items(order_id, dishes)
        return ret
    
    def mod(self, order):
        return self._oModel.mod(order)
    
    def get_list_by_restaurant(self, business_id, start, end, type=0):
        list = self._oModel.get_list_by_restaurant(business_id, start, end, type)
        for one in list:
            one = self._format(one)
        return list
    
    def get_list_by_servant(self, servant, start, end):
        return []

    def _format(self, order):
        order['add_time'] = Common.seconds_to_str(order['add_time'])
        if order['arrive_time']<>0:
            order['arrive_time'] = Common.seconds_to_str(order['arrive_time'])
        else:
            order['arrive_time'] = ''
        return order

    def _format_item(self, item):
        name = NameControl().get_one(item['name'].strip(), self._langcode)
        if name.has_key(self._langcode):
            item['name'] = name[self._langcode]
        return item

    # 获取某月份订单列表
    def get_list_by_user(self, uid, start, end):
        list = self._oModel.get_list_by_user(uid, start, end)
        for one in list:
            one = self._format(one)
        return list

    def get_detail_by_sequence(self, sequence):
        order = self._oModel.get_by_sequence(sequence)
        if not order:
            return None
        order = self._format(order)
        order['items'] = self._oModel.get_order_items(order['id'])
        for one in order['items']:
            one = self._format_item(one)
        return order
    """
