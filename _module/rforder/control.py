#!/usr/bin/env python2.7
#-*- coding:utf8 -*-
#
# 2013-12-4 by Victor
# Copyright 2013 Tubban

from _module import const
from _module.morder.model import MealOrderModel
from _module.rforder.model import RefundOrderModel


class RefundOrderControl:
    def __init__(self, uid = None,userLang=None):
        self._uid = uid
        self._refundOrderModel = RefundOrderModel(self._uid)
        self._mealOrderModel = MealOrderModel(self._uid)

    def add(self, order):
        return self._refundOrderModel.add(order)
    
    def do_order_refunded(self, refund_order_id, order_id, order_type):
        # 修改支付成功
        if not self.mod(refund_order_id, {"status": const.RefundOrder.STATUS_SUCCESS}):
            return False
        
        # 修改用户订单
        if order_type == const.ROrder.TYPE_MEAL:
            return self._mealOrderModel.mod({"id": order_id, "status": const.MealOrder.STATUS_REFUND})
            
        return True
    
    def mod(self, refund_order_id, args):
        return self._refundOrderModel.mod(refund_order_id, args)
    
    def get_by_third_id(self, refund_id, charge_id):
        return self._refundOrderModel.get_by_third_id(refund_id, charge_id)
    
    
    def get_by_id(self, id):
        return self._refundOrderModel.get_by_id(id)
    