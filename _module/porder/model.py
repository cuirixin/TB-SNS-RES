#!/usr/bin/env python2.7
#-*- coding:utf8 -*-
#
# Copyright 2013 Tubban
from _module import const
from _module._base_m_ import BaseModel
from _module._lib.common import Common

class POrderModel(BaseModel):
    def __init__(self, uid = None):
        self._order_table = 'pay_order'
        
    def get_by_charge(self, order_id, order_type, charge_id):
        sql = "SELECT id, status, money FROM %s WHERE order_id=%d and order_type=%d and third_pay_id='%s' LIMIT 1" % \
                (self._order_table, order_id, order_type, charge_id)
        print sql
        return self.get_one(sql)
    
    def add(self, fields):
        return self._add(fields)

    def _add(self, fields):
        order = {
            'uid': {'type':'d', 'default':0},
            'order_id': {'type':'d', 'required':1},
            'order_type': {'type':'d', 'required':1},
            'third_pay_type': {'type':'d', 'required':1},
            'third_pay_channel': {'type':'s', 'required':1},
            'third_pay_bank': {'type':'s', 'default':''},
            'third_pay_id': {'type':'s', 'default':''},
            'source': {'type':'d', 'default':0},
            'money': {'type':'f', 'required':1},
            'extra': {'type':'s', 'default':'{}'},
            'currency': {'type':'d', 'default':19},
            'status': {'type':'d', 'default':const.PayOrder.STATUS_DOING},
            'add_time': {'type':'d', 'default':Common.get_current_time()},
        }
        
        ret = self._args_handle('insert', fields, order)               
        if not ret[0]:
            # todo:
            print ret
            return ret
        return self._insert(self._order_table, order)
    
    
    def mod(self, order_id, args):
        return self._mod(order_id, args)
    
    def _mod(self, order_id, args):
        order = {
            'third_pay_id': {'type':'s'},
            'time_expire': {'type': 'd'},
            'status': {'type': 'd'},
            'note': {'type':'s'},
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
        
    def finish_order(self, id, status, pay_time):
        sql = "UPDATE `%s` SET `status`=%s, `pay_time`=%s WHERE `id`=%d" % (self._order_table,status,pay_time,int(id))
        return self.execute(sql)
    
    def get_by_id(self, id):
        sql = "SELECT * FROM %s WHERE id=%d" % (self._order_table, id)
        return self.get_one(sql)
        
