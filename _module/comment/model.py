#!/usr/bin/env python2.7
#-*- coding:utf8 -*-
#
# 2014-3-8 by Victor
# Copyright 2014 Tubban
from _module import const
from _module._base_m_ import BaseModel
from _module._lib.common import Common

class BCommentModel(BaseModel):
    
    def __init__(self, uid = None):
        self._uid = uid
        self._user_talbe = 'auth_user'
        self._comment_table = 'b_comment'
        self._business_table = 'business'
    
    def get_pager_list(self, business_id, pager, lang_code=None):
        table = self._get_mo_split_table(business_id, self._comment_table, const.DB.B_COMMENT_SPLIT)
        size = pager['ps']
        offset = size*(pager['p']-1)
        
        where_sql = ' WHERE c.business_id=%d  ' % (business_id)
        if lang_code is not None and lang_code<>'':
            where_sql  = where_sql + " and c.lang_code='%s' " % lang_code
        count_sql = "SELECT count(1) as total FROM %s c " % table + where_sql
        count =  self.get_one_by_slave(count_sql)['total']
        if count<>0:
            # c.uid as user_id, c.username as user_name
            se_sql = "SELECT c.*, u.icon as user_icon, u.sex FROM %s c " \
                        " left join %s u on u.id=c.uid " \
                        " %s " \
                        " order by c.add_time desc " \
                        " limit %s,%s"  \
            % (table, self._user_talbe, where_sql, offset, size)
            rows = self.get_rows_by_slave(se_sql)
            return dict(total=count, data=rows)
        else:
            return dict(total=0, data=[])
        
    def get_comment_cnt(self, bid):
        table = self._get_mo_split_table(bid, self._comment_table, const.DB.B_COMMENT_SPLIT)
        sql = "SELECT count(1) as total FROM %s where business_id=%d" % (table, bid)
        ret = self.get_one_by_slave(sql)
        return ret['total']
    
    def get_latest_one_by_user(self, bid, uid):
        table = self._get_mo_split_table(bid, self._comment_table, const.DB.B_COMMENT_SPLIT)
        sql = "SELECT * FROM %s WHERE business_id=%d and uid=%d order by add_time desc limit 1 " % (table, bid, uid)
        return self.get_one_by_slave(sql)
    
    
    def update_comment_num(self, business_id):
        table = self._get_mo_split_table(business_id, self._comment_table, const.DB.B_COMMENT_SPLIT)
        sql = "SELECT count(1) as total FROM %s WHERE business_id=%d" % (table, business_id)
        total = self.get_one(sql)['total']
        
        sql = "UPDATE %s SET comment_num=%d WHERE id=%d" % (self._business_table, total, business_id)
        return self.execute(sql)[0]
        
    
    def add(self, fields):
        return self._add(fields)

    def _add(self, fields):
        
        table = self._get_mo_split_table(fields['business_id'], self._comment_table, const.DB.B_COMMENT_SPLIT)
        comment = {
            'source': {'type':'d', 'required':const.Common.SOURCE_TYPE_UGC},
            'lang_code': {'type':'s', 'default':''},
            'business_id': {'type':'d', 'required':1},
            'uid': {'type':'d', 'default':0},
            'username': {'type':'s', 'required':1},
            'score': {'type':'d', 'default':-1},
            'support': {'type':'d', 'default':0},
            'content': {'type':'s', 'default':''},
            'add_time': {'type':'d', 'default':Common.get_current_time()},
        }
        
        ret = self._args_handle('insert', fields, comment)               
        if not ret[0]:
            # todo:
            print ret[1]
            return ret
        return self._insert(table, comment)
    
    # TODO 添加其他删除操作
    def delete(self, business_id, id):
        table = self._get_mo_split_table(business_id, self._comment_table, const.DB.B_COMMENT_SPLIT)
        sql = "DELETE FROM %s WHERE id=%s " % (table, id)
        ret = self.execute(sql)
        if not ret[0]:
            return False
        return True

class MealCommentModel(BaseModel):
    
    def __init__(self, uid = None):
        self._uid = uid
        self._comment_table = 'r_meal_comment'
        self._user_talbe = 'auth_user'
    
    def get_pager_list(self, meal_id, pager, lang_code=None):
        table = self._get_mo_split_table(meal_id, self._comment_table, const.DB.R_MEAL_COMMENT_SPLIT)
        size = pager['ps']
        offset = size*(pager['p']-1)
        
        where_sql = ' WHERE c.meal_id=%d  ' % (meal_id)
        if lang_code is not None and lang_code<>'':
            where_sql  = where_sql + " and c.lang_code='%s' " % lang_code
        count_sql = "SELECT count(1) as total FROM %s c " % table + where_sql
        count =  self.get_one_by_slave(count_sql)['total']
        if count<>0:
            # c.uid as user_id, c.username as user_name
            se_sql = "SELECT c.*, u.icon as user_icon, u.sex FROM %s c " \
                        " left join %s u on u.id=c.uid " \
                        " %s " \
                        " order by c.add_time desc " \
                        " limit %s,%s"  \
            % (self._comment_table, self._user_talbe, where_sql, offset, size)
            rows = self.get_rows_by_slave(se_sql)
            return dict(total=count, data=rows)
        else:
            return dict(total=0, data=[])
            
    
    def add(self, fields):
        return self._add(fields)

    def _add(self, fields):
        
        table = self._get_mo_split_table(fields['meal_id'], self._comment_table, const.DB.R_MEAL_COMMENT_SPLIT)
        comment = {
            'lang_code': {'type':'s', 'default':''},
            'meal_id': {'type':'d', 'required':1},
            'meal_order_id': {'type': 'd', 'required': 1},
            'uid': {'type':'d', 'default':0},
            'username': {'type':'s', 'required':1},
            'score': {'type':'d', 'default':-1},
            'support': {'type':'d', 'default':0},
            'content': {'type':'s', 'default':''},
            'add_time': {'type':'d', 'default':Common.get_current_time()},
        }
        print comment
        ret = self._args_handle('insert', fields, comment)     
        print ret          
        if not ret[0]:
            return ret
        return self._insert(table, comment)
    
    # TODO 添加其他删除操作
    def delete(self, meal_id, id):
        table = self._get_mo_split_table(meal_id, self._comment_table, const.DB.R_MEAL_COMMENT_SPLIT )
        sql = "DELETE FROM %s WHERE id=%s " % (table, id)
        ret = self.execute(sql)
        if not ret[0]:
            return False
        return True
