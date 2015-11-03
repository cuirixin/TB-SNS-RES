#!/usr/bin/env python2.7
#-*- coding:utf8 -*-
#
# Copyright 2015 Tubban
from _module import const
from _module._base_m_ import BaseModel
from _module._lib.common import Common

class RefundOrderModel(BaseModel):
    def __init__(self, uid = None):
        self._order_table = 'refund_order'

    def add(self, fields):
        return self._add(fields)

    def _add(self, fields):
        order = {
            'pay_order_id': {'type':'d', 'required': 1},
            'third_pay_id': {'type':'s', 'required': 1},
            'reason': {'type':'s', 'default':''},
            'reason_type': {'type':'d', 'required': 1},
            'status': {'type':'d', 'default': const.RefundOrder.STATUS_DOING},
            'order_id': {'type':'d', 'required': 1},
            'order_type': {'type':'d', 'required': 1},
            'tickets': {'type':'s', 'default': ''},
            'money': {'type':'f', 'required': 1},
            'add_time': {'type':'d', 'default':Common.get_current_time()},
        }
        
        ret = self._args_handle('insert', fields, order)               
        if not ret[0]:
            # todo:
            return ret
        return self._insert(self._order_table, order)
    
    def get_by_third_id(self, refund_id, charge_id):
        sql = "SELECT * FROM %s WHERE third_refund_id='%s' and third_pay_id='%s' LIMIT 1" % \
                (self._order_table, refund_id, charge_id)
        return self.get_one(sql)
    
    def mod(self, order_id, args):
        return self._mod(order_id, args)
    
    def _mod(self, order_id, args):
        order = {
            'status': {'type':'d'},
            'third_refund_id': {'type':'s'},
            'refund_time': {'type':'d'},
        }   
        if not order_id:
            return False

        ret = self._args_handle('update', args, order)               
        if not ret[0]:
            return False
        
        if len(order) == 0:
            return True
        
        where = "id=%d" % (int(order_id))
        ret = self._update(self._order_table, order, where)
        if not ret[0]:
            return False
        return True
        
    def get_by_id(self, id):
        sql = "SELECT * FROM %s WHERE id=%d" % (self._order_table, id)
        return self.get_one(sql)

