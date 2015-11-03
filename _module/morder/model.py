#!/usr/bin/env python2.7
#-*- coding:utf8 -*-
#
# 2014-3-8 by Victor
# Copyright 2014 Tubban
from _module import const
from _module._base_m_ import BaseModel
from _module._lib.common import Common
from _module._lib.log import Log

class MealOrderModel(BaseModel):
    
    
    def __init__(self, uid = None):
        self._uid = uid
        self._meal_table = 'r_meal'
        self._meal_order_table = 'r_meal_order'
        self._meal_ticket_table = 'r_meal_ticket'
    
    def add(self, fields):
        return self._add(fields)

    def _add(self, fields):
        
        order = {
            'uid': {'type':'d', 'default':0},
            'username': {'type':'s', 'required':1},
            'sequence': {'type':'s', 'required':1},
            'mobile': {'type':'s', 'default': ''},
            'title': {'type':'s', 'default': ''},
            'r_id': {'type':'d', 'required':1},
            'r_name': {'type':'s', 'required':1},
            'b_uuid': {'type':'s', 'required':1},
            'status': {'type':'d', 'default':0},
            'status_comment': {'type':'d', 'default':0},
            'currency': {'type':'d', 'required':1},
            'price': {'type':'f', 'default':0},
            'arrive_time': {'type':'d', 'default':0},
            'pay_order_id': {'type':'d', 'default':0},
            'meal_id': {'type':'d', 'default':0},
            'meal_num': {'type':'d', 'default':1},
            'note': {'type':'s', 'default':''},
            'add_time': {'type':'d', 'default':Common.get_current_time()},
        }
        
        ret = self._args_handle('insert', fields, order)               
        if not ret[0]:
            return ret
        return self._insert(self._meal_order_table, order)
    
    def get_pager_list_by_restaurant(self, pager, bid, status=None):
        size = pager['ps']
        offset = size*(pager['p']-1)
        
        where_sql = " WHERE o.r_id=%d " % bid
        
        if status and status <> 0:
            where_sql += " AND o.status=%d" % status
            
        count_sql = "SELECT count(1) as total FROM %s o %s" % (self._meal_order_table, where_sql)
        count =  self.get_one(count_sql)['total']
        if count<>0:
            fields = ['id', 'title', 'uid', 'username', 'sequence', 'status', 'price', 'price_rmb', 'payed', \
                      'payed_time', 'pay_order_id', 'meal_id', 'meal_num', \
                      'used_num', 'used_time', 'arrive_time', 'mobile']
            select_str = self._gen_fields_str(fields, 'o')
        
            se_sql = "SELECT %s FROM %s o" \
                        " %s " \
                        " order by o.add_time desc " \
                        " limit %s,%s"  \
            % (select_str, self._meal_order_table, where_sql, offset, size)
            rows = self.get_rows(se_sql)
            return dict(total=count, data=rows)
        else:
            return dict(total=0, data=[])
        
    def get_my_pager_list(self, pager, uid, status=None, status_comment=None):
        size = pager['ps']
        offset = size*(pager['p']-1)
        
        where_sql = " WHERE o.uid=%d " % uid
        
        if status is not None and status <> -1:
            where_sql += " AND o.status=%d" % status
        else:
            where_sql += " AND o.status>%d" % const.MealOrder.STATUS_DELETE
            
        if status_comment:
            where_sql += " AND o.status_comment=%d" % status_comment
            
        count_sql = "SELECT count(1) as total FROM %s o %s" % (self._meal_order_table, where_sql)
        
        count =  self.get_one(count_sql)['total']
        if count<>0:
            se_sql = "SELECT o.id, o.uid, o.username, o.r_id, o.status, o.price, o.price_rmb, o.payed, o.payed_time, "\
                        " o.add_time, o.meal_id, o.meal_num, o.title, o.currency, o.used_num, o.status_comment, o.mobile FROM %s o" \
                        " %s " \
                        " order by o.add_time desc " \
                        " limit %s,%s"  \
            % (self._meal_order_table, where_sql, offset, size)
            rows = self.get_rows(se_sql)
            return dict(total=count, data=rows)
        else:
            return dict(total=0, data=[])
        
    def get_by_id(self, id):
        fields = ['id', 'title', 'uid', 'username', 'sequence', 'status', 'r_id', 'r_name', 'currency', 'status_comment', 'price', 'payed', \
                      'payed_time', 'pay_order_id', 'meal_id', 'meal_num', \
                      'used_num', 'used_time', 'add_time', 'mobile', 'price_rmb']
        select_str = self._gen_fields_str(fields)
        sql = "SELECT %s FROM %s WHERE id=%d " % (select_str, self._meal_order_table, id)
        return self.get_one(sql)
    
    def get_by_fields(self, order_id, fields):
        select_str = self._gen_fields_str(fields)
        sql = "SELECT %s FROM %s WHERE `id`=%d" % (select_str, self._meal_order_table, order_id)
        return self.get_one(sql)
        
    def get_by_sequence(self, sequence):
        sql = "SELECT * FROM %s WHERE `sequence`='%s' and `status`>%d" % (self._meal_order_table, 
                                                                          self.escape_string(sequence),
                                                                          const.MealOrder.STATUS_DELETE)
        return self.get_one(sql)
        
    def mod(self, order):
        return self._mod(order)
    
    def _mod(self, args):
        order = {
            'status': {'type':'d'},
            'status_comment': {'type':'d'},
            'payed': {'type':'d'},
            'payed_time': {'type':'d'},
            'pay_order_id': {'type':'d'},
            'price_rmb': {'type': 'f'},
            'used_time': {'type':'d'},
            'used_num': {'type':'d'},
        }

        if not args.has_key('id'):
            return False

        ret = self._args_handle('update', args, order)               
        if not ret[0]:
            return ret
        where = "id=%d" % args['id']
        if len(order) > 0:
            ret = self._update(self._meal_order_table, order, where)
            if not ret[0]:
                return ret
        # _mod success
        return ret
    
    #########################For Op##########################################
    def get_pager_list_by_daterange(self, pager, start_sec, end_sec, status=None):
        size = pager['ps']
        offset = size*(pager['p']-1)
        
        fields = ['id', 'r_id', 'uid', 'username', 'price', 'title', 'meal_id', 'meal_num', 'used_num', 'currency', 'status', 'add_time', 'used_time']
        select_str = self._gen_fields_str(fields)
        where_sql = " WHERE `add_time`>=%d and `add_time`<%d " %  (start_sec, end_sec)
        if status is not None:
            where_sql = where_sql + " and status=%d " % int(status)
            
        count_sql = "SELECT count(1) as total FROM %s  " % self._meal_order_table + where_sql
        count =  self.get_one(count_sql)['total']
        if count<>0:
            se_sql = "SELECT %s " \
                " FROM %s " \
                " %s order by add_time desc limit %d,%d"\
                % (select_str, self._meal_order_table, where_sql, offset, size)
            rows = self.get_rows(se_sql)
            return dict(total=count, data=rows)
        else:
            return dict(total=0, data=[])

class MealTicketModel(BaseModel):
    
    def __init__(self, uid = None):
        self._uid = uid
        self._meal_ticket_table = 'r_meal_ticket'
        self._meal_order_table = 'r_meal_order'
    
    def get_brief_by_id(self, id):
        fields = ['id', 'order_id', 'uid', 'username', 'meal_id', 'status', 'add_time', 'used_time']
        select_str = self._gen_fields_str(fields)
        sql = "SELECT %s " \
                " FROM %s " \
                " WHERE `id`=%d "\
                " LIMIT 1" % (select_str, self._meal_ticket_table, id)
        return self.get_one(sql)
        
    def get_by_id(self, id):
        # sql构建
        fields = ['id', 'order_id', 'uid', 'username', 'meal_id', 'r_id', 'status', 'add_time', 'used_time']
        select_str = self._gen_fields_str(fields)
        sql = "SELECT %s " \
                " FROM %s " \
                " WHERE `id`=%d "\
                " LIMIT 1" % (select_str, self._meal_ticket_table, id)
        return self.get_one(sql)
    
    def get_by_sequence(self, r_id, sequence):
        fields = ['id', 'sequence', 'order_id', 'uid', 'username', 'meal_id', 'r_id', 'status', 'add_time', 'used_time']
        select_str = self._gen_fields_str(fields)
        sql = "SELECT %s " \
                " FROM %s " \
                " WHERE `r_id`=%d and `sequence`='%s' "\
                " LIMIT 1" % (select_str, self._meal_ticket_table, r_id, self.escape_string(sequence))
        return self.get_one(sql)
    
    def get_all_by_meal_order(self, order_id):
        fields = ['id', 'sequence', 'meal_id', 'r_id', 'status', 'add_time', 'used_time']
        select_str = self._gen_fields_str(fields)
        sql = "SELECT %s " \
                " FROM %s " \
                " WHERE `order_id`=%d "\
                 % (select_str, self._meal_ticket_table, order_id)
        return self.get_rows(sql)
    
    
    def add(self, fields):
        return self._add(fields)

    def _add(self, fields):
        
        order = {
            'sequence': {'type':'s', 'required':1},
            'order_id': {'type':'d', 'required':1},
            'meal_id': {'type':'d', 'required':1},
            'uid': {'type':'d', 'required':1},
            'username': {'type':'s', 'default':''},
            'r_id': {'type':'d', 'required':1},
            'status': {'type':'d', 'default':const.MealTicket.STATUS_NOT_USED},
            'add_time': {'type':'d', 'default':Common.get_current_time()},
            'used_time': {'type':'d', 'default':0},
            'validity_from' : {'type':'s', 'required':1},
            'validity_to' : {'type':'s', 'required':1},
            'price': {'type':'f', 'required':1},
            'currency_id': {'type':'d', 'required':1},
        }
        
        ret = self._args_handle('insert', fields, order)               
        if not ret[0]:
            return ret
        return self._insert(self._meal_ticket_table, order)
    
    def mod(self, id, ticket):
        return self._mod(id, ticket)
    
    def _mod(self, id, args):
        if not id:
            return False
        order = {
            'status': {'type':'d'},
            'used_time': {'type':'d'},
            'bill_id': {'type':'d'},
            'bill_payed': {'type':'d'},
        }

        ret = self._args_handle('update', args, order)               
        if not ret[0]:
            return ret
        where = "id=%d" % int(id)
        if len(order) > 0:
            ret = self._update(self._meal_ticket_table, order, where)
            if not ret[0]:
                return ret
        # _mod success
        return ret
    
    def mod_by_ids(self, ids, args):
        if not ids or len(ids) == 0:
            return False
        ids_str = ','.join(ids)
        order = {
            'used_time': {'type':'d'},
            'bill_id': {'type':'d'},
            'bill_payed': {'type':'d'},
        }

        ret = self._args_handle('update', args, order)               
        if not ret[0]:
            return ret
        where = "id in (%s)" % ids_str
        if len(order) > 0:
            ret = self._update(self._meal_ticket_table, order, where)
            if not ret[0]:
                return ret
        return ret
    
    def mod_by_bill(self, bill_id, args):
        if not bill_id or bill_id == 0:
            return False
        ticket = {
            'bill_payed': {'type':'d'},
        }
        ret = self._args_handle('update', args, ticket)               
        if not ret[0]:
            return ret
        where = "bill_id=%d" % bill_id
        print where
        if len(ticket) > 0:
            ret = self._update(self._meal_ticket_table, ticket, where)
            if not ret[0]:
                return ret
        return ret

    def get_used_cnt_by_orderid(self, order_id):
        cnt_sql = "SELECT count(1) as total FROM %s WHERE order_id=%d and status=%d" % (self._meal_ticket_table, int(order_id), const.MealTicket.STATUS_USED)
        return self.get_one(cnt_sql)['total']
    
    
    def get_pager_list_by_restaurant(self, pager, bid, status=None):
        size = pager['ps']
        offset = size*(pager['p']-1)
        
        where_sql = " WHERE o.r_id=%d " % bid
        
        if status and status <> 0:
            where_sql += " AND o.status=%d" % status
            
        count_sql = "SELECT count(1) as total FROM %s o %s" % (self._meal_ticket_table, where_sql)
        count =  self.get_one(count_sql)['total']
        if count<>0:
            fields = ['id','uid', 'username', 'meal_id', 'order_id', 'sequence', 'status', 'add_time', 'used_time', 'bill_payed', 'bill_id']
            select_str = self._gen_fields_str(fields, 'o')
        
            se_sql = "SELECT %s, DATE_FORMAT(validity_from, '%%%%Y-%%%%m-%%%%d') validity_from, DATE_FORMAT(validity_to, '%%%%Y-%%%%m-%%%%d') validity_to FROM %s o" \
                        " %s " \
                        " order by o.used_time desc " \
                        " limit %s,%s"  \
            % (select_str, self._meal_ticket_table, where_sql, offset, size)
            rows = self.get_rows(se_sql)
            return dict(total=count, data=rows)
        else:
            return dict(total=0, data=[])
        
    def get_pager_list_by_user(self, pager, uid, status):
        size = pager['ps']
        offset = size*(pager['p']-1)

        where_sql = " WHERE t.uid=%d " % uid

        if status and status <> 0:
            where_sql += " AND t.status=%d" % status

        count_sql = "SELECT count(1) as total FROM %s t %s" % (self._meal_ticket_table, where_sql)
        count =  self.get_one(count_sql)['total']

        if count<>0:
            fields = ['id','sequence', 'order_id', 'meal_id', 'status', 'add_time', 'r_id']
            select_str = self._gen_fields_str(fields, 't')
        
            se_sql = "SELECT %s, DATE_FORMAT(validity_from, '%%%%Y-%%%%m-%%%%d') validity_from, DATE_FORMAT(validity_to, '%%%%Y-%%%%m-%%%%d') validity_to FROM %s t" \
                        " %s " \
                        " order by t.add_time desc " \
                        " limit %s,%s"  \
            % (select_str, self._meal_ticket_table, where_sql, offset, size)
            rows = self.get_rows(se_sql)
            return dict(total=count, data=rows)
        else:
            return dict(total=0, data=[])
    
    def get_unsettled_pager_list_by_restaurant(self, pager, bid):
        size = pager['ps']
        offset = size*(pager['p']-1)

        where_sql = " WHERE r_id=%d and status=%d and bill_id=0 " % (bid, const.MealTicket.STATUS_USED)

        count_sql = "SELECT count(1) as total FROM %s %s" % (self._meal_ticket_table, where_sql)
        count =  self.get_one(count_sql)['total']
        if count<>0:
            fields = ['id','sequence', 'order_id', 'meal_id', 'status', 'add_time', 'r_id', 'currency_id', 'price', 'used_time']
            select_str = self._gen_fields_str(fields)
        
            se_sql = "SELECT %s " \
                        " FROM %s " \
                        " %s " \
                        " order by used_time desc " \
                        " limit %s,%s"  \
            % (select_str, self._meal_ticket_table, where_sql, offset, size)
            rows = self.get_rows(se_sql)
            return dict(total=count, data=rows)
        else:
            return dict(total=0, data=[])
        
    def get_pager_log_list(self, pager):
        size = pager['ps']
        offset = size*(pager['p']-1)
        where_sql = ' WHERE r_id!=278049 '
        count_sql = "SELECT count(1) as total FROM %s %s" % (self._meal_ticket_table, where_sql)
        count =  self.get_one(count_sql)['total']
        if count<>0:
            fields = ['id','sequence', 'order_id', 'meal_id', 'status', 'add_time', 'r_id', 'currency_id', 'price', 'used_time', 'username']
            select_str = self._gen_fields_str(fields)
        
            se_sql = "SELECT %s " \
                        " FROM %s " \
                        " %s " \
                        " order by add_time desc " \
                        " limit %s,%s"  \
            % (select_str, self._meal_ticket_table, where_sql, offset, size)
            rows = self.get_rows(se_sql)
            return dict(total=count, data=rows)
        else:
            return dict(total=0, data=[])
        
        
    def get_unsettled_count_by_restaurant(self, b_id):
        where_sql = " WHERE r_id=%d and status=%d and bill_id=0 " % (b_id, const.MealTicket.STATUS_USED)
        count_sql = "SELECT count(1) as total FROM %s %s" % (self._meal_ticket_table, where_sql)
        return self.get_one(count_sql)['total']
    
    def get_unsettled_all_list_by_restaurant(self, bid):
        fields = ['id', 'currency_id', 'price']
        select_str = self._gen_fields_str(fields)
        where_sql = " WHERE r_id=%d and status=%d and bill_id=0 " % (bid, const.MealTicket.STATUS_USED)
        se_sql = "SELECT %s " \
                    " FROM %s " \
                    " %s " \
        % (select_str, self._meal_ticket_table, where_sql)
        return self.get_rows(se_sql)
    
    def get_all_by_bill(self, bill_id):
        fields = ['id', 'sequence', 'price', 'used_time']
        select_str = self._gen_fields_str(fields)
        where_sql = " WHERE bill_id=%d " % bill_id
        se_sql = "SELECT %s " \
                    " FROM %s " \
                    " %s " \
        % (select_str, self._meal_ticket_table, where_sql)
        return self.get_rows(se_sql)
        