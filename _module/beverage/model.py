#!/usr/bin/env python2.7
#-*- coding:utf8 -*-
#
# 2014-2-13 by Victor
# Copyright 2014 Tubban
from _module._base_m_ import BaseModel

class BeverageModel(BaseModel):
    
    def __init__(self, uid = None):
        self._sys_beverage_category_table = 'sys_beverage_category'
        self._beverage_table = "r_beverage"
        self._uid = uid
        
    def get_categories(self, field='EN', parent=None):
        sql = "SELECT id, parent, %s as name FROM %s " \
                " WHERE 1=1 " % (field, self._sys_beverage_category_table)
        if parent is not None:
            sql += " AND parent=%s " % parent
        return self.get_rows(sql)
    
    def get_categories_by_business(self, business_id, field='EN'):
        sql = "SELECT c.id, c.parent, c.%s as name FROM %s c " \
                " WHERE c.id in (" \
                " SELECT DISTINCT b.`category` " \
                "     FROM %s b " \
                "     WHERE  b.restaurant_id=%d " \
                " ) " % (field, self._sys_beverage_category_table, 
                self._beverage_table, business_id)
        return self.get_rows(sql)
    
    def add(self, beverage):
        sql = "INSERT INTO %s" % self._beverage_table 
        sql += "(`restaurant_id`,`name`,`visible`, `category`,`subcategory`,"\
                " `is_mix`,`mix`,`percentage`,`origin_place`,`origin_year`,`add_time`,`cover`) \
              VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        return self.execute(sql,
                            beverage.get('restaurant_id', 0), 
                            beverage.get('name', ''), 
                            beverage.get('visible', 0),
                            beverage.get('category', 0),
                            beverage.get('subcategory', 0),
                            beverage.get('is_mix', 0),
                            beverage.get('mix', ''),
                            beverage.get('percentage', ''),
                            beverage.get('origin_place', ''),
                            beverage.get('origin_year', ''),
                            beverage.get('add_time',''),
                            beverage.get('cover','')) 
    
    def get_list(self, business_id, category=None, field='EN'):
        sql = "SELECT b.id, b.restaurant_id, b.name, b.visible, b.category, c1.%s as category_name, " \
                " b.subcategory, c2.%s as subcategory_name, b.is_mix,b.mix,b.percentage,b.origin_place,b.origin_year,b.cover " \
                " FROM %s b " \
                " LEFT JOIN %s c1 on c1.id=b.category " \
                " LEFT JOIN %s c2 on c2.id=b.subcategory " \
                " WHERE b.restaurant_id=%d" % \
                (field, field, self._beverage_table, self._sys_beverage_category_table, 
                 self._sys_beverage_category_table, business_id)
        if category:
            sql += " AND b.category=%d  " % category
        sql += " order by b.subcategory"
        return self.get_rows(sql)
    
    def get_detail(self, id, field='EN'):
        sql = "SELECT b.id, b.restaurant_id, b.name, b.visible, b.category, c1.%s as category_name, " \
                " b.subcategory, c2.%s as subcategory_name, b.is_mix,b.mix,b.percentage,b.origin_place,b.origin_year,b.cover " \
                " FROM %s b " \
                " LEFT JOIN %s c1 on c1.id=b.category " \
                " LEFT JOIN %s c2 on c2.id=b.subcategory " \
                " WHERE b.id=%d" % \
                (field, field, self._beverage_table, self._sys_beverage_category_table, 
                 self._sys_beverage_category_table, id)
        return self.get_one(sql)
    
    def mod(self, beverage):
        if not beverage.has_key('id'):
            return False
        s = ''
        if beverage.has_key('name'):
            s += " `name` = '%s'," % (beverage['name'])
        if beverage.has_key('visible'):
            s += " `visible` = %d," % (beverage['visible'])
        if beverage.has_key('category'):
            s += " `category` = %d," % (beverage['category'])
        if beverage.has_key('subcategory'):
            s += " `subcategory` = %d," % (beverage['subcategory'])
        if beverage.has_key('is_mix'):
            s += " `is_mix` = %d," % (beverage['is_mix'])
        if beverage.has_key('mix'):
            s += " `mix` = '%s'," % (beverage['mix'])
        if beverage.has_key('percentage'):
            s += " `percentage` = '%s'," % (beverage['percentage'])
        if beverage.has_key('origin_place'):
            s += " `origin_place` = '%s'," % (beverage['origin_place'])
        if beverage.has_key('origin_year'):
            s += " `origin_year` = '%s'," % (beverage['origin_year'])
        if beverage.has_key('cover'):
            s += " `cover` = '%s'," % (beverage['cover'])
        if len(s) <= 0:
            return True
        s = s[0:len(s)-1]
        sql = "UPDATE %s SET %s WHERE id=%d " % (self._beverage_table, s, beverage['id'])
        sql = sql.replace('%', '%%')
        
        ret = self.update(sql)
        return ret[0]
        
    def delete(self, id):
        sql = "DELETE FROM %s WHERE id=%s" % (self._beverage_table, id)
        return self.execute(sql)[0]
        