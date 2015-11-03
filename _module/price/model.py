#!/usr/bin/env python2.7
#-*- coding:utf8 -*-
#
# 2014-1-28 by Victor
# Copyright 2014 Tubban
from _module._base_m_ import BaseModel

class PriceModel(BaseModel):
    
    def __init__(self, uid = None):
        self._price_table = 'price'
        self._currency_table = 'sys_currency'
        self._portionunit_table = 'sys_portionunit'
        
    """
    Func: 根据价格所属实体的类型和ID获取价格信息， 不包括关联信息和国际化语言信息
    Date: 2015-04-10
    @param target_type: int 实体类型， 1 - TYPE_DISH、 3 - TYPE_BEVERAGE
    @param target_id: int 实体ID
    """
    def get_brief_by_target(self, target_type, target_id):
        fields = ['id', 'num', 'portionunit_id', 'price', 'currency_id']
        fields_str = self._gen_fields_str(fields)
        sql = "SELECT %s FROM %s " \
                " WHERE target_type=%s and target_id=%s " \
                % (fields_str, self._price_table, target_type, target_id)
        return self.get_rows(sql)
    
    
    """
    Func: 根据ID获取价格信息， 包括关联信息和国际化信息
    Date: 2015-04-10
    @param id: int 
    @param field: string 语言字段
    """
    def get_by_id(self, id, field='EN'):
        currency_field = 'EN'
        if field<>'CN' and field<>'EN':
            currency_field = 'EN'
        sql = "SELECT a.*,b.%s as currency_name,b.iso_code as currency_iso_code,c.%s as portionunit_name FROM %s a " \
                " LEFT JOIN %s b on b.id=a.currency_id " \
                " LEFT JOIN %s c on c.id=a.portionunit_id " \
                " WHERE a.id=%d " \
                % (currency_field, field, self._price_table, \
                   self._currency_table, self._portionunit_table, id)
        return self.get_one(sql)
    
    """
    Func: 根据ID获取价格信息， 不包括关联信息
    Date: 2015-04-10
    @param id: int 
    @param field: string 语言字段
    """
    def get_brief_by_id(self, id):
        fields = ['id', 'num', 'portionunit_id', 'price', 'currency_id']
        fields_str = self._gen_fields_str(fields)
        sql = "SELECT %s FROM %s " \
                " WHERE id=%s LIMIT 1" \
                % (fields_str, self._price_table, id)
        return self.get_one(sql)
    
    def add(self, price):
        sql = "INSERT INTO %s(`portionunit_id`,`price`,`currency_id`,`num`,`target_id`,`target_type`) values(%d,%s,%d,'%s',%d,%d) " \
                % (self._price_table,price['portionunit_id'],price['price'],price['currency_id'],price['num'],price['target_id'],price['target_type'])
        return self.execute(sql)
    
    def mod(self, price):
        if not price.has_key('id'):
            return True
        else:
            priceid = price['id']
            del price['id']
        
        sql = "UPDATE %s SET " % self._price_table
        
        for key in price:
            sql += "%s=%%(%s)s," % (key,key)
        sql = sql[0:len(sql)-1] 
        sql += " WHERE id=%s" % priceid
        return self.update(sql, **price)[0]
    
    ###################################### TODO
    
    
    def get_by_target(self, target_type, target_id, field='EN'):
        currency_field = field
        if field not in ['CN', 'EN']:
            currency_field = 'EN'
        sql = "SELECT a.*,b.%s as currency_name,b.iso_code as currency_iso_code,c.%s as portionunit_name FROM %s a " \
                " LEFT JOIN %s b on b.id=a.currency_id " \
                " LEFT JOIN %s c on c.id=a.portionunit_id " \
                " WHERE a.target_type=%s and a.target_id=%s " \
                % (currency_field, field, self._price_table, \
                   self._currency_table, self._portionunit_table, target_type, target_id)
        return self.get_rows(sql)
    
    def delete_by_target(self, target_type, target_id):
        sql = "DELETE FROM %s WHERE target_type=%s and target_id=%s" \
                % (self._price_table, target_type, target_id)
        return self.execute(sql)[0]
        
    def delete_by_id(self, id):
        sql = "DELETE FROM %s WHERE id=%s" \
                % (self._price_table, id)
        return self.execute(sql)[0]
    
    