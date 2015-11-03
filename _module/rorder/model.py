#!/usr/bin/env python2.7
#-*- coding:utf8 -*-
#
# 2014-5-8 by Victor
# Copyright 2014 Tubban
from _module import const
from _module._base_m_ import BaseModel
from _module._lib.common import Common
from _module._lib.log import Log
import json

class ROrderModel(BaseModel):
    def __init__(self, uid = None):
        self._order_table = 'r_order'
        self._order_dish_table = 'r_order_dish'
        self._order_item_table = 'r_order_item'
        self._order_item_tmp_table = 'r_order_item_tmp'
        
    def add(self, fields):
        return self._add(fields)
    
    def _add(self, fields):
        
        order = {
            'type': {'type':'d', 'required':1},
            'sequence': {'type':'s', 'required':1},
            'waiter' : {'type':'d', 'default':0},
            'currency_id':{'type':'s', 'required':1},
            'r_id': {'type':'d', 'required':1},
            'r_name': {'type':'s', 'required':1},
            'b_uuid': {'type':'s', 'required':1},
            'customer_id': {'type':'d', 'required':1},
            'customer_name': {'type':'s', 'required':1}, # 绑定信息，例如餐桌号
            'price': {'type':'f', 'required':1},
            'status': {'type':'d', 'default':const.ROrder.STATUS_QRCODE_GENERATED},
            'payed': {'type':'d', 'default':0},
            'people_cnt': {'type':'d', 'default':-1},
            'refer_code': {'type':'d', 'default':0},
            'note': {'type':'s', 'default':''},
            
            'extra': {'type':'s', 'default':''},
            'arrive_time': {'type':'d', 'default':0},
            'add_time': {'type':'d', 'default':Common.get_current_time()},
            'mod_time': {'type':'d', 'default':Common.get_current_time()},
            'scanned_time' : {'type':'d', 'default':0},
        }
        
        ret = self._args_handle('insert', fields, order)  
        if not ret[0]:
            # todo:
            return ret
        return self._insert(self._order_table, order)
    
    """
    Func: 获取重复的菜品信息
    @param order_id: 名称 
    @param dish_id: 菜品ID
    @return:
    """
    def _check_exist_item(self, order_id, dish_id):
        fields = ["id", "num", "price_discount"]
        fields_str = self._gen_fields_str(fields)
        sql = "SELECT %s FROM %s WHERE order_id=%d AND dish_id=%d LIMIT 1" % \
                (fields_str, self._order_item_table, order_id, dish_id)
        return self.get_one(sql)
    
    """
    Func: 更新Item
    @param item_id: 订单ID
    @param item: 
    @return:
    """
    def mod_item(self, id, item):
        return self._mod_item(id, item)
    
    def _mod_item(self, id, args):
        
        if not id:
            return False
        order_item = {
            'num': {'type':'d'},   # 数量
            'price_total': {'type':'f'}, # 总价格
            'note': {'type':'s'},  # 特殊需要
        }

        ret = self._args_handle('update', args, order_item)               
        if not ret[0]:
            return False
        where = "id=%d" % int(id)
        if len(order_item) > 0:
            ret = self._update(self._order_item_table, order_item, where)
            if not ret[0]:
                return False
        return True
    
    """
    Func: 添加菜品条目， 如果已有就追加
    @param order_id: 名称 
    @param fields: 菜品信息
    @return:
    """
    def _add_item(self, order_id, fields):
        
        item = self._check_exist_item(order_id, fields['dish_id'])
        if item:
            _num = item['num'] + fields['num']
            _total_price = item['price_discount'] * _num
            _item = {"num":_num, "price_total":_total_price}
            if not self._mod_item(item['id'], _item):
                Log.critical("Mod item error: %s" % json.dumps(_item))
            return True
        
        item = {
            'order_id' : {'type':'d', 'default':order_id},
            'dish_id': {'type':'s', 'required':1},
            'dish_name' : {'type':'s', 'required':1},
            'price_total': {'type':'f', 'required':1},
            'num': {'type':'d', 'required':1},
            'price': {'type':'f', 'required':1},
            'price_discount': {'type':'f', 'required':1},
            'price_num' : {'type':'s', 'required':1},
            'price_unit' : {'type':'d', 'required':1},
            'note': {'type':'s', 'default':''},
        }

        ret = self._args_handle('insert', fields, item)  
        if not ret[0]:
            # todo:
            return ret
        return self._insert(self._order_item_table, item)

    """
    Func: 添加菜品条目， 如果已有就追加
    @param order_id: 订单ID
    @param items: 菜品信息
        [{
            'dish_id': 521L,
            'dish_name': u'TATAR',
            'num': 2,
            'price': 19.0,
            'price_total': 38.0,
            'price_num': u'1.0',  # 38 CHF/ 1份
            'price_unit': 103L
        }]
    @return:
    """
    def add_items(self, order_id, items):
        for o in items:
            self._add_item(order_id, o)
        return True
    
    def refresh_price(self, order_id):
        sql = "SELECT sum(price_total) as price FROM %s WHERE order_id=%d " % \
                (self._order_item_table, int(order_id))
        price  = self.get_one(sql)['price']
        if not price:
            price = 0
        order = {"price":price}
        return self._mod(order_id, order)
    
    """
    Func: 通过未确认订单
    @param order_id: 订单ID
    @return:
    """
    def get_last_one(self, bid, uid):
        fields = ["id"]
        fields_str = self._gen_fields_str(fields)
        sql = "SELECT %s FROM %s WHERE status=%d and customer_id=%d and r_id=%d LIMIT 1" % \
                (fields_str, self._order_table, const.ROrder.STATUS_QRCODE_GENERATED, uid, bid)
        return self.get_one(sql)
            
    """
    Func: 通过ID获取订单信息
    @param order_id: 订单ID
    @return:
    """
    def get_by_id(self, order_id):
        fields = ["id", "status", "currency_id", "waiter", "customer_id", \
                  "r_id", "b_uuid", "refer_code", "payed", "note", "price", \
                  "add_time", "mod_time", "scanned_time"]
        fields_str = self._gen_fields_str(fields)
        sql = "SELECT %s FROM %s WHERE id=%d LIMIT 1" % \
                (fields_str, self._order_table, int(order_id))
        return self.get_one(sql)
    
    """
    Func: 获取所有未被服务员扫描或者接单的订单
    @param order_id: 订单ID
    @return:
    """
    def get_unscanned_orders(self, b_uuid, table_num):
        if not b_uuid:
            return []
        fields = ["id", "waiter", "customer_id", \
                  "r_id", "b_uuid", "refer_code", "payed"]
        fields_str = self._gen_fields_str(fields)
        sql = "SELECT %s FROM %s WHERE b_uuid='%s' AND refer_code=%d AND status=%d" % \
                (fields_str, self._order_table, b_uuid, int(table_num), const.ROrder.STATUS_QRCODE_GENERATED)
        print sql
        return self.get_rows(sql)
    
    """
    Func: 通过条目ID获取条目概要信息
    @param item_id: 订单条目ID
    @return:
    """
    def get_brief_item_by_id(self, item_id):
        fields = ["order_id", "num", "price_total", "price_discount", "price"]
        fields_str = self._gen_fields_str(fields)
        sql = "SELECT %s FROM %s WHERE id=%d LIMIT 1" % \
                (fields_str, self._order_item_table, int(item_id))
        return self.get_one(sql)

    def mod_dish(self, order_id, dishes):
        sql = "REPLACE INTO %s(`order_id`,`dishes`) VALUES(%d,'%s')" % (self._order_dish_table, order_id, dishes)
        return self.execute(sql)[0]
    
    def get_dishes(self, order_id):
        sql = "select dishes from %s where order_id=%d limit 1" % (self._order_dish_table, order_id)
        return self.get_one(sql)
    
    """
    Func: 修改订单信息
    @param order_id: 订单ID
    @param order: 修改项
    @return:
    """
    def mod(self, order_id, order):
        return self._mod(order_id, order)
    
    def _mod(self, order_id, args):
        
        if not order_id:
            return False
        
        order = {
            'waiter' : {'type':'d'},
            'currency_id':{'type':'s'},
            'price': {'type':'f'},
            'status': {'type':'d'},
            'payed': {'type':'d'},
            'people_cnt': {'type':'d'},
            'refer_code': {'type':'d'},
            'note': {'type':'s'},
            'extra': {'type':'s'},
            'arrive_time': {'type':'d'},
            'scanned_time': {'type':'d'},
        }

        ret = self._args_handle('update', args, order)               
        if not ret[0]:
            return False
        where = "id=%d" % order_id
        if len(order) > 0:
            order['mod_time'] = {'type': 'd', 'value': Common.get_current_time()}
            ret = self._update(self._order_table, order, where)
            if not ret[0]:
                return False
        # _mod success
        return True
    
    """
    Func: 获取我的订单列表
    @param type: 1 - 未确认的 2 - 已确认的 
    """
    def get_my_orders_pager_list(self, pager, customer_id, type=1):
        size = pager['ps']
        offset = size*(pager['p']-1)
        
        where_sql = ' WHERE customer_id=%d ' % customer_id
        
        if type == 1:
            where_sql = where_sql + " AND `status`=%d " % const.ROrder.STATUS_QRCODE_GENERATED
        elif type == 2:
            where_sql = where_sql + " AND `status`>%d  " % const.ROrder.STATUS_QRCODE_GENERATED
            
        count_sql = "SELECT count(1) as total FROM %s " % self._order_table + where_sql
        count =  self.get_one(count_sql)['total']
        if count<>0:
            fields = ["id", "r_id", "r_name", "mod_time"]
            fields_str = self._gen_fields_str(fields)
            se_sql = "SELECT %s " \
                        " FROM %s " \
                        " %s " \
                        " order by id desc "  \
                        " limit %s,%s "\
            % (fields_str, self._order_table, where_sql, offset, size)
            rows = self.get_rows(se_sql)
            return dict(total=count, data=rows)
        else:
            return dict(total=0, data=[])
    
    
    def get_brief_items(self, order_id):
        fields = ["id", "dish_id", "dish_name", "num", "price_total", \
                  "price_discount", "price", "price_num", "price_unit"]
        fields_str = self._gen_fields_str(fields)
        sql = "SELECT %s FROM %s WHERE order_id=%d AND `num`>0" % \
                (fields_str, self._order_item_table, order_id)
        return self.get_rows(sql)
    
    def get_customer_orders_pager_list(self, pager, customer_id, b_uuid=None, status=0):
        size = pager['ps']
        offset = size*(pager['p']-1)
        
        where_sql = ' WHERE customer_id=%d ' % customer_id
        
        if b_uuid is not None:
            where_sql = where_sql + " AND `b_uuid`='%s' " % b_uuid
        
        # STATUS_GRABBED_BY_WAITER + STATUS_QRCODE_GENERATED
        if status == -1:
            where_sql = where_sql + " AND `status` in (%d, %d)  " % (const.ROrder.STATUS_GRABBED_BY_WAITER, const.ROrder.STATUS_QRCODE_GENERATED)
        elif status == 0:
            where_sql = where_sql + " AND `status`>%d  " % const.ROrder.STATUS_DELETE
        else:
            where_sql = where_sql + " AND status=%d " % status
            
        count_sql = "SELECT count(1) as total FROM %s " % self._order_table + where_sql
        count =  self.get_one(count_sql)['total']
        if count<>0:
            fields = ["id", "status", "currency_id", "waiter", "customer_id", \
                      "r_id", "b_uuid", "refer_code", "payed", "note", "price", \
                      "add_time", "mod_time", "scanned_time"]
            fields_str = self._gen_fields_str(fields)
            se_sql = "SELECT %s " \
                        " FROM %s " \
                        " %s " \
                        " order by id desc "  \
                        " limit %s,%s "\
            % (fields_str, self._order_table, where_sql, offset, size)
            rows = self.get_rows(se_sql)
            return dict(total=count, data=rows)
        else:
            return dict(total=0, data=[])
        
    def get_table_orders_pager_list(self, pager, table_number, r_id=None, status=0):
        size = pager['ps']
        offset = size*(pager['p']-1)
        where_sql = " WHERE r_id=%d AND refer_code=%d AND status>%d " % (r_id, table_number, const.ROrder.STATUS_DELETE)
        
        count_sql = "SELECT count(1) as total FROM %s " % self._order_table + where_sql
        count =  self.get_one(count_sql)['total']
        if count<>0:
            fields = ["id", "status", "currency_id", "waiter", "customer_id", \
                      "r_id", "b_uuid", "refer_code", "payed", "note", "price", \
                      "add_time", "mod_time", "scanned_time"]
            fields_str = self._gen_fields_str(fields)
            se_sql = "SELECT %s " \
                        " FROM %s " \
                        " %s " \
                        " order by id desc "  \
                        " limit %s,%s "\
            % (fields_str, self._order_table, where_sql, offset, size)
            rows = self.get_rows(se_sql)
            return dict(total=count, data=rows)
        else:
            return dict(total=0, data=[])
        
    ########################### TODO 

    def get_list_by_restaurant(self, business_id, start, end, type=0):
        select = "SELECT id, lang_code, source_id, source_type, servant, uid, sequence, type, " \
                " restaurant_name, business_uuid, refer_code, " \
                " status, payed, address, refuse, note, price, " \
                " real_price, phone, contactor, add_time, item_num, " \
                " people_num, arrive_time " \
                " from %s " \
                 % self._order_table
                
        where = " where restaurant_id=%d and add_time>=%d and add_time<%d " % \
                (business_id, start, end)
        if type<>0:
            where = where + " and type=%d " % type
        
        orderby = " ORDER by `id` desc"
        sql = select + where + orderby
        return self.get_rows(sql)

    # 用户订单列表
    def get_list_by_user(self, uid, start, end):
        sql = "SELECT id, lang_code, source_id, source_type, servant, uid, sequence, type, " \
                " restaurant_name, business_uuid, refer_code, " \
                " status, payed, address, refuse, note, price, " \
                " real_price, phone, contactor, add_time, item_num, " \
                " people_num, arrive_time " \
                " from %s where uid=%d and add_time>=%d and add_time<%d " \
                " ORDER by `id` desc" % (self._order_table, uid, start, end)
        return self.get_rows(sql)

    def get_by_sequence(self, suquence):
        sql = "SELECT id, lang_code, source_id, source_type, servant, uid, sequence, type, " \
                " restaurant_name, business_uuid, refer_code, " \
                " status, payed, address, refuse, note, price, " \
                " real_price, phone, contactor, add_time, item_num, " \
                " people_num, arrive_time " \
                " from %s where sequence=%s " \
                % (self._order_table, suquence)
        return self.get_one(sql)
        
    def get_order_items(self, order_id):
        sql = "SELECT id, order_id, number, name, refer_id, note, " \
                " price, real_price, num, " \
                " `extra` " \
                " from %s where order_id=%s " \
                " order by id asc " \
                % (self._order_item_table, order_id)
        return self.get_rows(sql)
        
    ###############Temp order item#################
    
    def get_item_tmp(self, rid, uid, dishid):
        sql = "select id,num,price,price_num,price_unit from %s where rid=%d and uid=%d and refer_id=%d" \
                % (self._order_item_tmp_table, rid, uid, dishid)
        return self.get_one(sql)
    def add_item_tmp(self, fields):
        return self._add_item_tmp(fields)
    
    def _add_item_tmp(self, fields):
        item_tmp = {
            'rid' : {'type':'d', 'required':1},
            'uid' : {'type':'d', 'required':1},
            'number' : {'type':'s', 'required':1},
            'name': {'type':'s', 'required':1},
            'refer_id' : {'type':'d', 'default':0},
            'note' : {'type':'s', 'default':''},
            'price': {'type':'f', 'required':1},
            'price_num' : {'type':'s', 'required':1},
            'price_unit' : {'type':'d', 'required':1},
            'currency_iso_code':{'type':'s', 'required':1},
            'num': {'type':'d', 'required':1},
            'real_price': {'type':'f', 'required':1},
            'extra': {'type':'s', 'default':''},
            'add_time': {'type':'d', 'default':Common.get_current_time()},
            'mod_time': {'type':'d', 'default':Common.get_current_time()},
        }
        
        ret = self._args_handle('insert', fields, item_tmp)  
        if not ret[0]:
            # todo:
            print ret[1]
            return ret
        return self._insert(self._order_item_tmp_table, item_tmp)
    
    def mod_item_tmp(self, item_tmp):
        return self._mod_item_tmp(item_tmp)
    
    def _mod_item_tmp(self, args):
        item_tmp = {
            'note' : {'type':'s'},
            'num': {'type':'d'},
            'price': {'type':'f'},
            'real_price': {'type':'f'},
            'extra': {'type':'s'}
        }

        if not args.has_key('id'):
            return False

        ret = self._args_handle('update', args, item_tmp)               
        if not ret[0]:
            return False
        where = "id=%d" % args['id']
        if len(item_tmp) > 0:
            item_tmp['mod_time'] = {'type': 'd', 'value': Common.get_current_time()}
            ret = self._update(self._order_item_tmp_table, item_tmp, where)
            if not ret[0]:
                return False
        # _mod success
        return ret[0]
        
    def del_item_tmp(self, id):
        sql = "DELETE FROM %s WHERE id=%d LIMIT 1" \
                % (self._order_item_tmp_table, int(id))
        return self.execute(sql)[0]

    def clear_item_tmp(self, rid, uid):
        sql = "DELETE FROM %s WHERE rid=%d and uid=%d" \
                % (self._order_item_tmp_table, int(rid), int(uid))
        return self.execute(sql)[0]
    
    def get_item_tmp_list(self, rid, uid):
        sql = "SELECT * FROM %s WHERE rid=%d and uid=%d ORDER BY add_time asc" \
                % (self._order_item_tmp_table, rid, uid)
        return self.get_rows(sql)

    def get_item_tmp_by_id(self,  id):
        sql = "SELECT * FROM %s WHERE id=%d LIMIT 1" \
                % (self._order_item_tmp_table, int(id))
        return self.get_one(sql)
        

    def get_last_one_by_table(self, r_id, table_number):
        fields = ["id", "status", "waiter", "add_time", "mod_time", "scanned_time"]
        fields_str = self._gen_fields_str(fields)
        where_sql = " r_id=%d and refer_code=%d " % (int(r_id), int(table_number))
        se_sql = "SELECT %s " \
                    " FROM %s " \
                    " WHERE %s " \
                    " order by id desc "  \
                    " limit 1 "\
        % (fields_str, self._order_table, where_sql)
        return self.get_one(se_sql)

    def get_table_unclosed_orders(self, r_id, table_number):
        fields = ["id", "status", "currency_id", "waiter", "customer_id", \
                      "r_id", "b_uuid", "refer_code", "payed", "note", "price", \
                      "add_time", "mod_time", "scanned_time"]
        fields_str = self._gen_fields_str(fields)
        where_sql = " WHERE r_id=%d AND refer_code=%d AND status>%d AND status<%d " % (r_id, table_number, const.ROrder.STATUS_DELETE, const.ROrder.STATUS_PAYED_AND_CLOSE)
        se_sql = "SELECT %s " \
                    " FROM %s " \
                    " %s " \
                    " order by id desc "  \
        % (fields_str, self._order_table, where_sql)
        return  self.get_rows(se_sql)
