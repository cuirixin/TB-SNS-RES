#!/usr/bin/env python2.7
#-*- coding:utf8 -*-
#
# 2013-12-4 by Victor
# Copyright 2013 Tubban
from _module import const
from _module._base_m_ import BaseModel
from _module._lib.common import Common
from _module._lib.lang import Lang

class NameModel(BaseModel):
    
    def __init__(self, uid = None):
        self._name_table = 'dict_name'
        self._language_table = 'sys_language'
        self._uid = uid
    
    def _add(self, fields):
        dict_name = {
            'name': {'type':'s', 'required':1},
            'en': {'type':'s', 'default':''},
            'zh': {'type':'s', 'default':''},
            'de': {'type':'s', 'default':''},
            'fr': {'type':'s', 'default':''},
            'ru': {'type':'s', 'default':''},
            'ar': {'type':'s', 'default':''},
            'ko': {'type':'s', 'default':''},
            'status': {'type':'d', 'default':const.Name.STATUS_NEW},
            'tm_add' : {'type':'d', 'default':Common.get_current_time()}
        }
        
        ret = self._args_handle('insert', fields, dict_name)   
        if not ret[0]:
            return ret
        return self._insert(self._name_table, dict_name)

    def _mod_by_name(self, name, args):
        if not name or name == '':
            return False
        dict_name = {
            'en': {'type':'s'},
            'zh': {'type':'s'},
            'de': {'type':'s'},
            'fr': {'type':'s'},
            'ru': {'type':'s'},
            'ar': {'type':'s'},
            'ko': {'type':'s'},
            'status': {'type':'d'},
            'tm_mod' : {'type':'d'},
        }   
        # 添加修改时间
        args['tm_mod'] = Common.get_current_time()
        
        ret = self._args_handle('update', args, dict_name)               
        if not ret[0]:
            return False

        where = "name='%s'" % self.escape_string(name)
        if len(dict_name) > 0:
            ret = self._update(self._name_table, dict_name, where)
            if ret[0]:
                return True
            else:
                return False
        return True
    
    def get_by_cn_name(self, name):
        sql = "SELECT id, name FROM %s where `zh`='%s' " % (self._name_table, self.escape_string(name))
        return self.get_rows(sql)
    
    def mod_by_cn_name(self, name, args):
        if not name or name == '':
            return False
        dict_name = {
            'en': {'type':'s'},
            'zh': {'type':'s'},
            'de': {'type':'s'},
            'fr': {'type':'s'},
            'ru': {'type':'s'},
            'ar': {'type':'s'},
            'ko': {'type':'s'},
            'status': {'type':'d'},
            'cover': {'type': 's'},
        }   
        # 添加修改时间
        args['tm_mod'] = Common.get_current_time()
        
        ret = self._args_handle('update', args, dict_name)               
        if not ret[0]:
            return False

        where = "`zh`='%s'" % self.escape_string(name)
        if len(dict_name) > 0:
            ret = self._update(self._name_table, dict_name, where)
            if ret[0]:
                return True
            else:
                return False
        return True
    
    def _mod_by_id(self, id, args):
        if not id:
            return False
        
        dict_name = {
            'id': {'type':'d'},
            'name': {'type':'s'},
            'en': {'type':'s'},
            'zh': {'type':'s'},
            'de': {'type':'s'},
            'fr': {'type':'s'},
            'ru': {'type':'s'},
            'ar': {'type':'s'},
            'ko': {'type':'s'},
            'status': {'type':'d'},
            'tm_mod' : {'type':'d'},
        }   
        # 添加修改时间
        args['tm_mod'] = Common.get_current_time()
        
        ret = self._args_handle('update', args, dict_name)               
        if not ret[0]:
            return False

        where = "id=%d" % id
        if len(dict_name) > 0:
            ret = self._update(self._name_table, dict_name, where)
            if ret[0]:
                return True
            else:
                return False
        return True  
    
    """
    Func: 名字是否存在
    @param name: 名称 
    @return: 1/0
    """
    def is_name_exist(self, name):
        if not name or name.strip() == '':
            False
        sql = "select id from %s where `name`='%s' limit 1" % (self._name_table, self.escape_string(name.strip()))
        if self.get_one(sql):
            return True
        return False
    
    """
    Func: 名字是否存在
    @param name: 名称 
    @param language: ttypes.LANGUAGE_FIELD
    @return: {} / {"en":"Good", "zh":"好"}
    """
    def get_name(self, name, language='all'):
        # sql构建
        fields = ['en', 'zh', 'de', 'fr', 'ru', 'ar', 'ko', 'cover']
        if language <> 'all':
            fields = [language]
        select_str = self._gen_fields_str(fields)
        sql = "SELECT %s " \
                " FROM %s " \
                " WHERE `name`='%s' "\
                " LIMIT 1" % (select_str, self._name_table, self.escape_string(name.strip()))
        one = self.get_one(sql)
        if not one:
            return {}
        _names = {}
        for lan in one:
            if not one[lan] or one[lan].strip() == '':
                continue
            _names[lan] = one[lan]
        return _names
    
    def get_name_image(self, name):
        # sql构建
        sql = "SELECT `cover` " \
                " FROM %s " \
                " WHERE `name`='%s' "\
                " LIMIT 1" % (self._name_table, self.escape_string(name.strip()))
        one = self.get_one(sql)
        if not one:
            return ''
        return one['cover']
    
    def get_by_id(self, id):
        sql = "select * from %s where id=%d" % (self._name_table, id)
        return self.get_one(sql)

    def search(self, key, lang=None, limit=12):
        key = key.strip()
        if lang is None:
            sql = "SELECT `name` FROM %s WHERE `name` like '%%%%%s%%%%' limit %d" % (self._name_table, self.escape_string(key), limit)
        else:
            if lang not in Lang.langcode_2_reqcode.keys():
                return []
            sql = "SELECT distinct `%s` as `name` FROM %s WHERE `%s` like '%%%%%s%%%%' limit %d" % \
                (lang, self._name_table, lang, self.escape_string(key), limit)
        return self.get_rows(sql)
    
    """
    Func: 添加
    @param name_dict: Eg. {"name":"good", "en":"good", "zh":"好"}
    @return: [True/False, Data, Message]
    """
    def add(self, name_dict):
        return self._add(name_dict)

    """
    Func: 通过name修改
    Date: 2015-01-01
    @param name: 
    @param name_dict: Eg. {"en":"good", "zh":"好"}
    @return: [True/False, Data, Message]
    """
    def mod_by_name(self, name, name_dict):
        return self._mod_by_name(name, name_dict)
    
    """
    Func: 通过id修改
    Date: 2015-01-01
    @param name_dict: Eg. {"id":1, "en":"good", "zh":"好"}
    @return: [True/False, Data, Message]
    """
    def mod_by_id(self, id, name_dict):
        return self._mod_by_id(id, name_dict)

    def get_all_names(self):
        sql = "SELECT `name` FROM %s " % self._name_table
        return self.get_rows(sql)
        
    def get_support_languages(self, field='EN'):
        ids = []
        for id in Lang.support_langs.keys():
            ids.append(str(id))
        ids = ','.join(ids)
        sql = "SELECT id, icon,iso_code, %s as name FROM %s WHERE id in (%s) order by id asc" \
                % (field, self._language_table, ids)
        return self.get_rows(sql)
    
    """
    Func: 获取分页数据
    Date: 2015-04-08
    @param pager: Eg. {"ps":"10", "p":"1"}
    @param status: 名称状态，-1为全部
    @param key: 模糊匹配关键词 
    """
    def get_pager_list(self, pager, status=None, key=None):
        
        size = pager['ps']
        offset = size*(pager['p']-1)
        
        wsql = ' WHERE 1=1 '
        if status is not None and status <> -1:
            wsql += "AND `status`=%s " % status 
        if key is not None and key.strip() <> '':
            wsql += "AND `name` like '%s%%%%'" % self.escape_string(key)
        
        count_sql = "SELECT count(1) as total FROM %s " % self._name_table + wsql
        count =  self.get_one(count_sql)['total']
        if count<>0:
            #fields = ['name', 'en']
            #fields_str = self._gen_fields_str(fields)
            fields_str = '*'
            se_sql = "SELECT %s FROM %s " \
                        " %s " \
                        " limit %s,%s"  \
            % (fields_str, self._name_table, wsql, offset, size)
            rows = self.get_rows(se_sql)
            return dict(total=count, data=rows)
        else:
            return dict(total=0, data=[])
        
        
    def get_pager_list_CN(self, pager, key=None):
        
        size = pager['ps']
        offset = size*(pager['p']-1)
        
        wsql = " WHERE `zh`!='' "
        if key is not None and key.strip() <> '':
            wsql += "AND `zh` like '%%%%%s%%%%'" % (self.escape_string(key))
        count_sql = "SELECT count(1) as total FROM %s " % self._name_table + wsql
        count =  self.get_one(count_sql)['total']
        if count<>0:
            fields = ['id', 'name', 'zh', 'cover']
            fields_str = self._gen_fields_str(fields)
            se_sql = "SELECT %s FROM %s " \
                        " %s " \
                        " order by cover desc " \
                        " limit %s,%s"  \
            % (fields_str, self._name_table, wsql, offset, size)
            rows = self.get_rows(se_sql)
            return dict(total=count, data=rows)
        else:
            return dict(total=0, data=[])
        