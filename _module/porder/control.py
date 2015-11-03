#!/usr/bin/env python2.7
#-*- coding:utf8 -*-
#
# 2013-12-4 by Victor
# Copyright 2013 Tubban

from _module import const
from _module._lib.common import Common
from _module._lib.generator import Generator
from _module.morder.control import MealOrderControl
from _module.morder.model import MealOrderModel, MealTicketModel
from _module.porder.model import POrderModel

class POrderControl:
    def __init__(self, uid = None,userLang=None):
        self._uid = uid
        self._oModel = POrderModel(self._uid)
        self._mealOrderModel = MealOrderModel(self._uid)
        self._mealTicketModel = MealTicketModel(self._uid)
        
        self._mealOrderControl = MealOrderControl(self._uid)
    
    def add(self,order):
        return self._oModel.add(order)
    
    def get_by_charge(self, order_id, order_type, charge_id):
        return self._oModel.get_by_charge(order_id, order_type, charge_id)
    
    def do_order_payed(self, pay_order_id, order_id, order_type):
        # 修改支付成功
        if not self.mod(pay_order_id, {"status": const.PayOrder.STATUS_SUCCESS}):
            return False
        
        # 修改用户订单
        if order_type == const.ROrder.TYPE_MEAL:
            return self._mealOrderControl.do_order_payed(order_id)
            
            
        return True
        
        
    def mod(self, order_id, args):
        return self._oModel.mod(order_id, args)
    
    def finish_order(self, id, status, finish_time, pay_money=0):
        order = self.get_by_id(int(id))
        # 排除用户复制返回的付款链接重新设置meal为支付未使用状态的情况
        if not order or order['pay_time'] <> 0:
            return False
        if status == const.PayOrder.STATUS_SUCCESS:
            if order['order_type'] == const.ROrder.TYPE_MEAL:
                _meal_order = self._mealOrderModel.get_by_id(order['order_id'])
                if not _meal_order or _meal_order['price'] > pay_money:
                    print "[Error]: Pay money is less than order money."
                else:
                    tmp = {}
                    tmp['id'] = order['order_id']
                    tmp['status'] = const.MealOrder.STATUS_PAYED
                    tmp['payed_time'] = finish_time
                    tmp['payed'] = 1
                    tmp['pay_order_id'] = int(id)
                    self._mealOrderModel.mod(tmp)
        return self._oModel.finish_order(id, status, finish_time)
    
    def get_by_id(self, id):
        return self._oModel.get_by_id(id)