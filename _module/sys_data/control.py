#!/usr/bin/env python2.7
#-*- coding:utf8 -*-
#
# 2013-12-4 by Victor
# Copyright 2013 Tubban
from _module import const
from _module._lib.common import Common
from _module._lib.lang import Lang
from _module.sys_data.model import SysdataModel
class SysdataControl:
    def __init__(self, uid = None,userLang=None):
        self._uid = uid
        self._sysDataModel = SysdataModel()
        self._field = Lang.get_db_field_name(userLang)
        
    ###获取business级别  标准化数据 的函数
    def get_all_continents(self):
        return self._sysDataModel.get_all_continents(self._field)

    ###获取business级别  标准化数据 的函数
    def get_all_weekdays(self):
        return self._sysDataModel.get_all_weekdays(self._field)
    
    def get_all_paymenttool(self):
        return self._sysDataModel.get_all_paymenttool(self._field)
    
    def get_paymenttool(self,ids):
        ids = Common.filter_comma_ids(ids)
        paymenttool = self._sysDataModel.get_paymenttool(ids,self._field)
        if paymenttool is None:
            return tuple()
        items=[]
        for one in paymenttool:
            if one['name']:
                items.append(one['name'])
        return paymenttool
    
    def get_all_languages(self):
        return self._sysDataModel.get_all_languages(self._field)
    
    def get_servicelanguage(self,ids):
        ids = Common.filter_comma_ids(ids)
        servicelanguage = self._sysDataModel.get_servicelanguage(ids,self._field)
        if servicelanguage is None:
            return tuple()
        items=[]
        for one in servicelanguage:
            if one['name']:
                items.append(one['name'])
        return items

    def get_all_foodingredient(self):
        return self._sysDataModel.get_all_ingredient(self._field)
    
    def get_all_cooktechnique(self):
        return self._sysDataModel.get_all_cooktechnique(self._field)
    
    def get_all_mouthfeel(self):
        return self._sysDataModel.get_all_mouthfeel(self._field)

    def get_all_country(self):
        return self._sysDataModel.get_all_country(self._field)
    
    def get_all_city(self):
        cities =  self._sysDataModel.get_all_city(self._field)
        return cities

    def get_all_city_by_sort(self):
        cities =  self._sysDataModel.get_all_city_by_sort(self._field)
        return cities

    def get_all_city_with_index(self):
        cities = self._sysDataModel.get_all_city_with_index(self._field)
        _index_arr = []
        _city_dict = {}
        
        _tmp_arry = []
        _tmp_index = None
        for city in cities:
            if city['index'] not in _index_arr:
                _index_arr.append(city['index'])
                if len(_tmp_arry) > 0:
                    _city_dict[_tmp_index] = _tmp_arry
                _tmp_index = city['index']
                _tmp_arry = [city]
            else:
                _tmp_arry.append(city)
        
        if len(_tmp_arry) > 0:
            _city_dict[_tmp_index] = _tmp_arry
            _tmp_arry = [city]
        
        return (_index_arr, _city_dict)
    
    def get_top_hot_cities(self, limit=10):
        return self._sysDataModel.get_top_hot_cities(limit, self._field)
    
    
    def get_all_city_with_country(self):
        return self._sysDataModel.get_all_city_with_country(self._field)

    def get_country_name(self,cid):
        return self._sysDataModel.get_country_name(cid, self._field)
    
    def get_all_currency(self):
        return self._sysDataModel.get_all_currency(self._field)
    
    def get_currency(self, id):
        return self._sysDataModel.get_currency(id, self._field)
    
    def get_all_portionunit(self):
        return self._sysDataModel.get_all_portionunit(self._field)
    
    # 菜品价格unit
    def get_dish_portionunit(self):
        return self._sysDataModel.get_portionunit_by_group(const.Business.PORTIONUNIT_GROUP_DISH, self._field)
    # 饮料价格unit
    def get_beverage_portionunit(self):
        return self._sysDataModel.get_portionunit_by_group(const.Business.PORTIONUNIT_GROUP_BEVERAGE, self._field)
    
    
    def get_all_foodtypes(self, field=None):
        if not field:
            field = self._field
        return self._sysDataModel.get_all_foodtypes(field)
    
    def get_city_by_id(self, id, field=None):
        if not field:
            field = self._field
        return self._sysDataModel.get_city_by_id(id, field)
    
    def get_city_by_ids(self, ids, field=None):
        if not field:
            field = self._field
        ids = Common.filter_comma_ids(ids)
        return self._sysDataModel.get_city_by_ids(ids, field)
    
    def get_city_name(self, cid, field=None):
        if not field:
            field = self._field
        return self._sysDataModel.get_city_name(cid, field)
        
    def get_all_cartetypes(self, field=None):
        if not field:
            field = self._field
        return self._sysDataModel.get_all_cartetypes(field)
    

    def get_all_ingredient(self, field=None):
        if not field:
            field = self._field
        return self._sysDataModel.get_all_ingredient(field)
    
    def get_all_foodtype(self, field=None):
        if not field:
            field = self._field
        return self._sysDataModel.get_all_foodtype(field)

    def get_ingredient(self,ids, field=None):
        if not field:
            field = self._field
        ids = Common.filter_comma_ids(ids)
        return self._sysDataModel.get_ingredient(ids, field) 
    
    def get_cooktechnique(self,ids, field=None):
        if not field:
            field = self._field
        ids = Common.filter_comma_ids(ids)
        return self._sysDataModel.get_cooktechnique(ids, field)
    
    def get_mouthfeel(self,ids,field=None):
        if not field:
            field = self._field
        ids = Common.filter_comma_ids(ids)
        return self._sysDataModel.get_mouthfeel(ids, field)
    
    def get_dishgoup_by_id(self, id, field=None):
        if not field:
            field = self._field
        return self._sysDataModel.get_dishgoup_by_id(id, field)
    
    def get_all_dishgroups(self, field=None):
        if not field:
            field = self._field
        return self._sysDataModel.get_all_dishgroups(field)
    
    def get_all_diningOptions(self,field=None):
        if not field:
            field = self._field
        return self._sysDataModel.get_all_diningOptions(field)
    
    def get_all_rsubcategories(self,field=None):
        if not field:
            field = self._field
        return self._sysDataModel.get_all_rsubcategories(field)
    
    def get_dining_option(self,ids,field=None):
        if not field:
            field = self._field
        ids = Common.filter_comma_ids(ids)
        return self._sysDataModel.get_dining_option(ids, field)
    
    def get_all_cuisineStyle(self, field=None):
        if not field:
            field = self._field
        return self._sysDataModel.get_all_cuisineStyle(field)
    
    def get_cuisine_style(self, ids, field=None):
        if not field:
            field = self._field
        ids = Common.filter_comma_ids(ids)
        return self._sysDataModel.get_cuisine_style(ids, field)
    
    def get_all_reserve_positions(self, field=None):
        if not field:
            field = self._field
        return self._sysDataModel.get_all_reserve_positions(field)
    
    def get_reserve_position(self, ids, field=None):
        if not field:
            field = self._field
        ids = Common.filter_comma_ids(ids)
        return self._sysDataModel.get_reserve_position(ids, field)
    
    def get_all_business_district_type(self, field=None):
        if not field:
            field = self._field
        return self._sysDataModel.get_all_business_district_type(field)

    def is_country_phonecode_exist(self, phone_code):
        if self._sysDataModel.get_country_by_phone_code(phone_code):
            return True
        return False
    
    def mod_city_location(self, city_id, lat, lon):
        return self._sysDataModel.mod_city_location(city_id, lat, lon)
    
    def get_current_exchange_rate(self, currency_id):
        return self._sysDataModel.get_current_exchange_rate(currency_id)
    
    def get_all_currency_exchange(self):
        return self._sysDataModel.get_all_currency_exchange()
        
    def get_currency_exchange(self, currency_id):
        return self._sysDataModel.get_currency_exchange(currency_id)
    
    def get_all_topic_local_special_tags(self, field=None):
        if not field:
            field = self._field
        return self._sysDataModel.get_all_local_special_tags(field)
        
