#!/usr/bin/env python2.7
#-*- coding:utf8 -*-
#
# 2014-2-13 by Victor
# Copyright 2014 Tubban
from _module._base_m_ import BaseModel
from _module._lib.common import Common

class StatisticModel(BaseModel):
    
    def __init__(self, uid = None):
        self._uid = uid
        self._user_online = 'statistic_user_online'
    
    def add_user_online_stcatistic(self, fields):
        return self._add_user_online_stcatistic(fields)

    def _add_user_online_stcatistic(self, fields):
        statistic = {
            'platform': {'type':'s', 'required':1},
            'product': {'type':'s', 'required':1},
            'num': {'type':'d', 'default':0},
            'gen_time' : {'type':'d', 'default':0}, 
        }
        ret = self._args_handle('insert', fields, statistic)               
        if not ret[0]:
            return ret
        return self._insert(self._user_online, statistic)
    
    def get_user_online_statistic(self, from_time, end_time):
        sql = "select * from %s where gen_time>=%d and gen_time<=%d order by gen_time asc" % (self._user_online, from_time, end_time)
        return self.get_rows(sql)

class RecordModel(BaseModel):
    
    def __init__(self, uid = None):
        self._uid = uid
        self._download_enter_table = 'record_dowload_enter'
        self._user_online = 'record_user_online'
    
    def get_download_enter(self, app, group_by):
        sql = "select %s, count(id) as cnt from %s where app='%s' group by %s" % (group_by, self._download_enter_table, app, group_by)
        return self.get_rows(sql)
    
    # 清理半小时前的用户
    def clear_user_online(self, delta = 600):
        sql = "DELETE FROM %s WHERE update_time < %d" % (self._user_online, Common.get_current_time() - delta)
        return self.execute(sql)[0]

    def get_user_online_cnt(self):
        sql = "SELECT platform, product, count(*) as cnt FROM %s group by platform, product" % (self._user_online)
        return self.get_rows(sql)