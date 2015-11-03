#!/usr/bin/env python2.7
#-*- coding:utf8 -*-
#
# 2014-2-9 by Victor
# Copyright 2014 Tubban
from _module import const
from _module._lib.common import Common
from _module._lib.lang import Lang
from _module.bill.model import BillModel
from _module.business.model import BusinessModel
from _module.morder.model import MealTicketModel
from _module.sys_data.model import SysdataModel

class BillControl:
    def __init__(self, uid = None,userLang=None):
        self._uid = uid
        self._bModel = BusinessModel(self._uid)
        self._mealTicketModel = MealTicketModel(self._uid)
        self._billModel = BillModel(self._uid)
        self._sysDataModel = SysdataModel()
        self._field = Lang.get_db_field_name(userLang)
        self._langcode = Lang.get_code_by_req_code(userLang)
    
    """
    Func: 获取餐厅的结账单列表
    """
    def get_pager_list_by_business(self, pager, bid, type=const.Bill.TYPE_PRODUCT, status=None):
        data = self._billModel.get_pager_list_by_business(pager, bid, type, status)
        for one in data['data']:
            one['currency'] = self._sysDataModel.get_currency(one['currency_id'], self._field)
        return data
    
    """
    Func: 创建结账单
    """
    def create(self, bid, type=const.Bill.TYPE_PRODUCT):
        business = self._bModel.get_brief_by_id(bid)
        if not business:
            return False
        if type == const.Bill.TYPE_PRODUCT:
            rows = self._mealTicketModel.get_unsettled_all_list_by_restaurant(bid)
            if len(rows) == 0:
                return [False, "Result Empty."]
            
            data = {}
            for one in rows:
                if one['currency_id'] <> 0:
                    if not data.has_key(one['currency_id']):
                        data[one['currency_id']] = [one]
                    else:
                        data[one['currency_id']].append(one)
            # 转成格式： {1L: [{'currency_id': 1L, 'price': 5.0, 'id': 11L}]}
            for currency_id in data:
                
                bill = {
                    "b_id": bid,
                    "type": type,
                    "b_name": business['name'],
                    "currency_id": currency_id,
                    "country_id": business['country_id'],
                    "city_id": business['city_id'],
                    "end_date": Common.get_current_datestr(const.Date_Format.DATE)
                }
                ret = self._billModel.add(bill)
                if not ret[0]:
                    return [False, "Create Bill Error."]
                bill_id = ret[1]
                tickets = data[currency_id]
                price = 0
                ids = []
                for ticket in tickets:
                    price += ticket['price']
                    ids.append(str(ticket['id']))
                self._billModel.mod(bill_id, {'price': price})
                self._mealTicketModel.mod_by_ids(ids, {"bill_id": bill_id})
            return [True, "Success"]
        
        return [False, "Failed"]
    
    """
    Func: 结账操作
    """
    def settle(self, id, type):
        bill = self._billModel.get_by_fields(id)
        if not bill or not self._billModel.mod(id, {"status": const.Bill.STATUS_SETTLED}):
            return [False, "Failed"]
        
        if type == const.Bill.TYPE_PRODUCT:
            self._mealTicketModel.mod_by_bill(id, {"bill_payed": 1})
            return [True, "Success"]
        return [False, "Failed"]
        
