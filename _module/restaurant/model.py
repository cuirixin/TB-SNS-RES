#!/usr/bin/env python2.7
#-*- coding:utf8 -*-
#
# 2013-12-4 by Victor
# Copyright 2013 Tubban
from _module._base_m_ import BaseModel
from _module._lib.common import Common

class RestaurantModel(BaseModel):
    def __init__(self, uid = None):
        self._uid = uid
        self._restaurant_table = 'restaurant'
        
    def get_by_fields(self, id, fields):
        select_str = self._gen_fields_str(fields)
        sql = "SELECT %s FROM %s WHERE `id`=%d" % (select_str, self._restaurant_table,id)
        return self.get_one_by_slave(sql)
    
    def get_by_id(self,bid):
        sql = "SELECT * FROM %s WHERE id=%s;" %(self._restaurant_table, bid)
        return self.get_one_by_slave(sql)
            
    def add(self, rest):
        sql="INSERT INTO %s"  % self._restaurant_table
        sql += "(`id`,`price_category`,`dining_option`,`cuisine_style`)VALUES(%s,%s,%s,%s);"
            
        ret = self.execute(sql,
                            rest.get('id',0),rest.get('price_category',0),
                            rest.get('dining_option',''),rest.get('cuisine_style',''),
                            )
        return ret
        """自动添加推荐
        if not ret[0]:
            return ret
        
        DishgroupModel().copy_sys_to_mine(rest['id'], rest['cuisine_style'])
        return ret
        """
   
    def edit(self, rest,bid):
        if rest.has_key('cuisine_style'):
            rest['cuisine_style'] = Common.add_comma_ids(rest['cuisine_style'])
        if rest.has_key('dining_option'):
            rest['dining_option'] = Common.add_comma_ids(rest['dining_option'])
        sql = "UPDATE %s SET " % self._restaurant_table
        for key in rest:
            sql += "%s=%%(%s)s," % (key,key)
        sql = sql[0:len(sql)-1] 
        sql += " WHERE id=%s" % bid
        return self.update(sql, **rest)
    
    
    def mod(self, restaurant):
        if not restaurant.has_key('business_id'):
            return False
        s = ''
        # TODO 暂时用最搓的方式处理； 如果分表需要另作处理
        if restaurant.has_key('cuisine_style'):
            s += " cuisine_style = '%s'," % (Common.add_comma_ids(restaurant['cuisine_style']))
        if restaurant.has_key('price_category'):
            s += " price_category = %s," % (restaurant['price_category'])
        if restaurant.has_key('dining_option'):
            s += " dining_option = '%s'," % (Common.add_comma_ids(restaurant['dining_option']))
        if restaurant.has_key('reservable'):
            s += " reservable = %d," % (restaurant['reservable'])
        if restaurant.has_key('reserve_ahead'):
            s += " reserve_ahead = %d," % (restaurant['reserve_ahead'])
        if restaurant.has_key('reserve_position'):
            s += " reserve_position = '%s'," % (restaurant['reserve_position'])
        if restaurant.has_key('has_menu'):
            s += " has_menu = %d," % (restaurant['has_menu'])
        if restaurant.has_key('menu_note'):
            s += " menu_note = '%s'," % (self.escape_string(restaurant['menu_note']))
        if restaurant.has_key('menu_note_dish_num'):
            s += " menu_note_dish_num = %d," % (restaurant['menu_note_dish_num'])
            
        if len(s) <= 0:
            return True
        s = s[0:len(s)-1]
        sql = "UPDATE %s SET %s WHERE id = %d" % (self._restaurant_table, s, int(restaurant['business_id']))
        sql = sql.replace('%', '%%')
        ret = self.update(sql)
        return ret[0]
    
    def delete(self,shopid):
        pass
        
        
        
