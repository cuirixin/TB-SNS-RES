#!/usr/bin/env python2.7
#-*- coding:utf8 -*-
#
# 2013-12-4 by Victor
# Copyright 2013 Tubban
from _module import const
from _module._base_m_ import BaseModel
from _module._lib.common import Common

class DishgroupModel(BaseModel):
    def __init__(self, uid = None):
        self._dishgroup_table = 'r_dishgroup'
        self._dish_table = "r_dish"
        self._sys_dishgroup_table = 'sys_dishgroup'
        self._uid = uid
        
    def get_by_id(self,id):
        sql = "SELECT id, refer_id, restaurant_id, visible, name FROM %s WHERE id=%s AND status=%d" % (self._dishgroup_table, id, const.DishGroup.STATUS_VALID)
        return self.get_one(sql)
    
    def get_sys_by_id(self, id, field='EN'):
        sql = "SELECT `id`, `%s` as name FROM %s WHERE id=%d " % \
                (field, self._sys_dishgroup_table, id)
        return self.get_one(sql)
    
    def get_by_restaurant_and_sysdishgroup(self, rid, sys_dishgroup_id):
        sql = "SELECT id, name FROM %s WHERE restaurant_id=%d and refer_id=%d LIMIT 1" \
                % (self._dishgroup_table, rid, sys_dishgroup_id)
        return self.get_one(sql)
    
    """
    Func : 获取在某菜单中所有的菜品类别
    Author: Victor
    Date:2014-01-26
    """
    def get_list_by_restid(self, restid, field="EN", visible=None):
        sql_v = ''
        if visible is not None:
            sql_v = ' and visible=%d ' % visible
        sql = "SELECT * FROM %s WHERE restaurant_id=%s and status=%d %s order by sortrank asc" \
                % (self._dishgroup_table, restid, const.DishGroup.STATUS_VALID, sql_v)
        return self.get_rows(sql)
    
    def get_brief_list_by_carte(self, carte_id, visible=None):
        sql_v = ''
        if visible is not None:
            sql_v = ' and visible=%d ' % visible
        sql = "SELECT id, refer_id,sortrank FROM %s " \
                " WHERE id in " \
                "  (SELECT DISTINCT dishgroup_id FROM %s " \
                    " WHERE carte_id=%s AND status=%d) and status=%d %s order by sortrank asc" \
                % (self._dishgroup_table, self._dish_table, carte_id, \
                   const.Dish.STATUS_VALID, const.DishGroup.STATUS_VALID, \
                   sql_v)
        return self.get_rows(sql)
    
    """
    Func : 获取在某菜单中所有的菜品类别
    Author: Victor
    Date:2014-01-26
    """
    def get_list_by_carte(self, carte_id, visible=None):
        sql_v = ''
        if visible is not None:
            sql_v = ' and visible=%d ' % visible
        sql = "SELECT id, refer_id, restaurant_id, visible, name,sortrank FROM %s " \
                " WHERE id in " \
                "  (SELECT DISTINCT dishgroup_id FROM %s " \
                    " WHERE carte_id=%s AND status=%d) and status=%d %s order by sortrank asc" \
                % (self._dishgroup_table, self._dish_table, carte_id, \
                   const.Dish.STATUS_VALID, const.DishGroup.STATUS_VALID, \
                   sql_v)
        return self.get_rows(sql)
    
    def _add_dishgroup_i18n(self, dishgroup_id, refer_id):
        return {}
    
    def add(self, fields):
        return self._add(fields)

    def _add(self, fields):
        dishgroup = {
            'refer_id': {'type':'d', 'required':1},
            'restaurant_id': {'type':'s', 'default':0},
            'name': {'type':'s', 'default':''},
            'visible': {'type':'d', 'default':1},
            'sortrank': {'type':'d', 'default':0},
            'add_time': {'type':'d', 'default':Common.get_current_time()},
        }
        
        ret = self._args_handle('insert', fields, dishgroup)               
        if not ret[0]:
            # todo:
            return ret
        return self._insert(self._dishgroup_table, dishgroup)
    
    def mod(self, dishgroup):
        if not dishgroup.has_key('id'):
            return False
        s = ''
        if dishgroup.has_key('name'):
            s += " name = '%s'," % (dishgroup['name'])
        if dishgroup.has_key('visible'):
            s += " visible = %d," % (dishgroup['visible'])
        if len(s) <= 0:
            return True
        s = s[0:len(s)-1]
        sql = "UPDATE %s SET %s WHERE id = %d" % (self._dishgroup_table, s, dishgroup['id'])
        sql = sql.replace('%', '%%')
        ret = self.update(sql)
        return ret[0]
    
    def delete(self, id):
        sql = "UPDATE %s SET `status`=%d WHERE id=%s " %(self._dishgroup_table, const.DishGroup.STATUS_DELETE, id)
        ret = self.execute(sql)
        return ret[0]
    
    def get_recommend_list_by_cuisine_style(self, cuisine_style, field='EN'):
        if cuisine_style=='':
            cuisine_style = '0'
        else:
            cuisine_style='0,'+cuisine_style
        sql = " select `id`, `%s` as name from %s " \
                " where cuisine_id in (%s) " \
                % (field, self._sys_dishgroup_table, cuisine_style)
        return self.get_rows(sql)
    
    def copy_sys_to_mine(self, restaurant_id, ids):
        ids = Common.filter_comma_ids(ids)
        sql = "insert into %s(`refer_id`,`restaurant_id`,`name`,`add_time`,`visible`) " \
                " select id, %d, `EN`, %d , 1 from %s " \
                " where id in (%s) " \
                % (self._dishgroup_table, restaurant_id, Common.get_current_time(), 
                   self._sys_dishgroup_table, ids)
        try:
            self.execute(sql)
        except Exception, e:
            pass
        
    def set_order(self,orderIds):
        for i, Id in enumerate(orderIds):
            sql = "UPDATE %s SET `sortrank`=%s WHERE `id`=%s" % (self._dishgroup_table,i+1,Id)
            self.update(sql)
        return True
    
     
    #########一下为导入Excel用到的方法，有可能需要优化#############

    def get_one_by_refer(self, business_id, refer_id):
        sql = "SELECT * FROM %s WHERE restaurant_id=%d and refer_id=%d LIMIT 1" \
                % (self._dishgroup_table, business_id, refer_id)
        return self.get_one(sql)
    
    def verify_added(self,business_id, refer_id):
        sql = "SELECT id FROM %s WHERE restaurant_id=%d and refer_id=%d LIMIT 1" \
                % (self._dishgroup_table, business_id, refer_id)
        ret = self.get_one(sql)
        if ret:
            return True
        else:
            return False
        
    def get_name_by_id(self,refer_id,lang):
        sql = "select %s as name from sys_dishgroup where id='%s';"  % (lang,refer_id)
        ret = self.get_one(sql)
        if ret:
            return ret['name']
        else:
            return ''
        