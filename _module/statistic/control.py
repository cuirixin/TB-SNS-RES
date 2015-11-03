#!/usr/bin/env python2.7
#-*- coding:utf8 -*-
#
# 2014-2-9 by Victor
# Copyright 2014 Tubban
from _module import const
from _module._lib.common import Common
from _module._lib.lang import Lang
from _module.business.model import BusinessModel
from _module.meal.model import MealModel
from _module.morder.model import MealOrderModel
from _module.statistic.model import StatisticModel
from _module.sys_data.model import SysdataModel
from _module.user.model import UserModel

class StatisticControl:
    def __init__(self, uid = None, userLang=None):
        self._uid = uid
        self._statisticModel = StatisticModel(self._uid)
        self._sysDataModel = SysdataModel()
        self._mealOrder = MealOrderModel()
        self._mealModel = MealModel()
        self._bModel = BusinessModel()
        self._uModel = UserModel()
        self._field = Lang.get_db_field_name(userLang)
        
    # type 1:Day 2:Week 3:Month 4:Year
    def get_online_user_statistic(self, type=1):
        if type == 1:
            from_time = Common.get_0clock_time()
            end_time = Common.get_current_time()
        rows = self._statisticModel.get_user_online_statistic(from_time, end_time)
        ss = {}
        cc = {}
        for one in rows:
            cc[one['gen_time']] = 1
            if one['product']+'_'+one['platform'] in ss:
                ss[one['product']+'_'+one['platform']].append(one['num'])
            else:
                ss[one['product']+'_'+one['platform']] = [one['num']]
        cc = sorted(list(cc))
        categories = []
        for c in cc:
            #categories.append(Common.seconds_to_str(c, "%H:%M:"))
            categories.append(str(c))
        series = []
        for s in ss:
            series.append({"name":s, "list":ss[s]})
        data = {"categories":categories, "series":series}
        return data
    
    def get_business_data_statistic_by_city(self, cities):
        
        # TODO
        """
        items = self._sysDataModel.get_all_city(self._field)
        cities = []
        categories = []
        for one in items:
            cities.append(one['id'])
            categories.append(one['name'])
        """
        categories = []
        
        series = []
        
        for one in cities:
            categories.append(self._sysDataModel.get_city_name(one, self._field))

        # 无中文简介
        values = []
        for one in cities:
            values.append(self._bModel.get_desc_cn_empty_cnt(one))
        series.append({
            "name": '无中文简介',
            "data": values,
            "stack": 'desc_cn'      
        }) 
        
        # 有中文简介
        values = []
        for one in cities:
            values.append(self._bModel.get_desc_cn_not_empty_cnt(one))
        series.append({
            "name": '有中文简介',
            "data": values,
            "stack": 'desc_cn'      
        })
        
        # 需要上传菜单-未上传
        values = []
        for one in cities:
            values.append(self._bModel.get_menu_need_not_upload(one))
        series.append({
            "name": '需要上传菜单-未上传',
            "data": values,
            "stack": 'menu_upload'      
        })
        
        # 已上传菜单
        values = []
        for one in cities:
            values.append(self._bModel.get_menu_upload_num(one))
        series.append({
            "name": '已上传菜单',
            "data": values,
            "stack": 'menu_upload'      
        })
        
        return {"categories": categories, "series": series}

    def get_unconsumed_morder_pager_list(self, pager, start_sec, end_sec, status=None):
        
        data = self._mealOrder.get_pager_list_by_daterange(pager, start_sec, end_sec, const.MealOrder.STATUS_PAYED)
        
        for one in data['data']:
            one['currency'] = self._sysDataModel.get_currency(one['currency'], 'CN')
            #one['consumer'] = self._uModel.get_brief_user_by_id(one['uid'])
            one['business'] = self._bModel.get_brief_by_id(one['r_id'])
            one['add_time'] = Common.seconds_to_str(one['add_time'])
        return data
    
    def get_unconsumed_morder_detail_for_op(self, id):
        morder = self._mealOrder.get_by_id(id)
        morder['currency'] = self._sysDataModel.get_currency(morder['currency'], 'CN')
        morder['consumer'] = self._uModel.get_brief_user_by_id(morder['uid'])
        #morder['business'] = self._bModel.get_brief_by_id(morder['r_id'])
        morder['meal'] = self._mealModel.get_brief_by_id(morder['meal_id'])
        morder['add_time'] = Common.seconds_to_str(morder['add_time'])
        return morder
        
        
