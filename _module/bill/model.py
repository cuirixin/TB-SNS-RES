#!/usr/bin/env python2.7
#-*- coding:utf8 -*-
#
# 2014-2-13 by Victor
# Copyright 2014 Tubban
from _module import const
from _module._base_m_ import BaseModel
from _module._lib.common import Common

class BillModel(BaseModel):
    
    def __init__(self, uid = None):
        self._bill_table = "bill"
        self._uid = uid
        
        
    def get_by_fields(self, id, fields=None):
        if fields is None:
            fields = ['id', 'b_id', 'b_name', 'type', 'price', 'currency_id', 'country_id', 'city_id', 'status', 'settle_time', 'end_date']
        
        fields_str = self._gen_fields_str(fields)
        sql = "SELECT %s FROM %s WHERE id=%d limit 1" % (fields_str, self._bill_table, id)
        return self.get_one(sql)
            
    def get_pager_list_by_business(self, pager, bid, type=const.Bill.TYPE_PRODUCT, status=None, fields=None):
        size = pager['ps']
        offset = size*(pager['p']-1)
        
        where_sql = ' WHERE b_id=%d and type=%d ' % (bid, type)
        
        if status is not None:
            where_sql = where_sql+ " and status=%d " % status 
                
        count_sql = "SELECT count(1) as total FROM %s " % self._bill_table + where_sql
        count =  self.get_one(count_sql)['total']
        
        if fields is None:
            fields = ['id', 'b_id', 'b_name', 'type', 'price', 'currency_id', 'country_id', 'city_id', 'status', 'settle_time']
        
        fields_str = self._gen_fields_str(fields)
        
        if count<>0:
            se_sql = "SELECT %s, DATE_FORMAT(end_date, '%%%%Y-%%%%m-%%%%d') end_date FROM %s " \
                        " %s" \
                        " order by end_date desc" \
                        " limit %s,%s"  \
            % (fields_str, self._bill_table, where_sql, offset, size)
            rows = self.get_rows(se_sql)
            return dict(total=count, data=rows)
        else:
            return dict(total=0, data=[])
    
    def _add(self, fields):
        
        bill = {
            'type': {'type':'d', 'required':1},
            'b_id': {'type':'d', 'required':1},
            'b_name': {'type':'s', 'required':1},
            'type': {'type':'d', 'default':1},
            'city_id': {'type':'d', 'required':1},
            'country_id': {'type':'d', 'required':1},
            'currency_id': {'type':'d', 'required':1},
            'price': {'type':'f', 'default':0},
            'status': {'type':'d', 'default':const.Bill.STATUS_UNSETTLED},
            'end_date' : {'type':'s', 'default': Common.get_current_datestr(const.Date_Format.DATE)},
        }
        
        ret = self._args_handle('insert', fields, bill)   
        if not ret[0]:
            # todo:
            return ret
        return self._insert(self._bill_table, bill)
    
    def add(self, kwarg):
        return self._add(kwarg)
    
    def mod(self, id, kwarg):
        return self._mod(id, kwarg)
    
    def _mod(self, id, args):
        bill = {
            'status': {'type':'d'},
            'price': {'type':'f'},
        }   
        if not id or id == 0:
            return False

        ret = self._args_handle('update', args, bill)               
        if not ret[0]:
            return False
        where = "id=%d" % int(id)
        
        if bill.has_key('status') and bill['status'] == const.Bill.STATUS_SETTLED:
            bill['settle_time'] = {'type': 'd', 'value': Common.get_current_time()}
        ret = self._update(self._bill_table, bill, where)
        if not ret[0]:
            return False
        return True
        