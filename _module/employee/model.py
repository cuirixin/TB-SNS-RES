#!/usr/bin/env python2.7
#-*- coding:utf8 -*-
#
# 2014-2-9 by Victor
# Copyright 2014 Tubban
from _module._base_m_ import BaseModel

class EmployeeModel(BaseModel):
    
    def __init__(self, uid = None):
        self._user_table = 'auth_user'
        self._employee_table = "auth_employee"
        self._role_table = "auth_role"
        self._uid = uid
        
    def get_detail(self, uid):
        sql = "SELECT u.id as uid, u.username, u.sex, u.email, u.status, u.first_name, u.last_name, " \
                " r.id as role_id, r.name as role_name, e.business_id " \
                " FROM %s e " \
                " LEFT JOIN %s u on u.id=e.uid " \
                " LEFT JOIN %s r on r.id=e.role_id " \
                " WHERE e.uid=%d" % \
                (self._employee_table, self._user_table, self._role_table, uid)
        return self.get_one(sql)

    def get_list(self, business_id, role_id=None):
        sql = "SELECT u.id as uid, u.username, u.sex, u.email, u.status, u.first_name, u.last_name, " \
                " r.id as role_id, r.name as role_name " \
                " FROM %s e " \
                " LEFT JOIN %s u on u.id=e.uid " \
                " LEFT JOIN %s r on r.id=e.role_id " \
                " WHERE e.business_id=%d" % \
                (self._employee_table, self._user_table, self._role_table, business_id)
        if role_id:
            sql += " AND e.role_id=%d " % role_id
        return self.get_rows(sql)
    """
    employee = {
        'uid':1,
        'business_id':2,
        'role_id';1
    }
    """
    def add(self, employee):
        sql = "INSERT INTO %s" % self._employee_table 
        sql += "(`uid`,`business_id`,`role_id`) \
              VALUES(%s,%s,%s)"
        return self.execute(sql,
                            employee.get('uid', 0), 
                            employee.get('business_id', 0), 
                            employee.get('role_id', 0))  
    
    def mod(self, employee):
        if not employee.has_key('uid') and not employee.has_key('business_id'):
            return False
        s = ''
        if employee.has_key('role_id'):
            s += " role_id = %d," % (employee['role_id'])
        if len(s) <= 0:
            return True
        s = s[0:len(s)-1]
        sql = "UPDATE %s SET %s WHERE uid = %d and business_id=%d " % (self._employee_table, s, employee['uid'], employee['business_id'])
        sql = sql.replace('%', '%%')
        ret = self.update(sql)
        return ret[0]
        
    def delete(self, uid):
        sql = "DELETE FROM %s WHERE uid=%s" % (self._employee_table, uid)
        return self.execute(sql)[0]
        