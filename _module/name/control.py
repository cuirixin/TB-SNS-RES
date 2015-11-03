#!/usr/bin/env python2.7
#-*- coding:utf8 -*-
#
# 2013-12-4 by Victor
# Copyright 2013 Tubban
from _module._lib.common import Common
from _module._lib.lang import Lang
from _module._lib.log import Log
from _module._lib.rds import Rds
from _module.name.model import NameModel
import json

class NameControl(object):
    
    def __init__(self, uid = None, userLang=None):
        self._uid = uid
        self._nameModel = NameModel()
        self._field = Lang.get_db_field_name(userLang)
        
    #-------------------Base Functions For All-----------------------

    def get_support_languages(self):
        return self._nameModel.get_support_languages(self._field)
    
    def is_name_exist(self, name):  
        name = name.strip()
        return self._nameModel.is_name_exist(name)
    
    def get_by_id(self, id):
        return self._nameModel.get_by_id(id)

    def get_one(self, name, lang='all'):
        if lang <> 'all' and lang not in Lang.langcode_2_reqcode.keys():
            return {}
        name = name.strip()
        # 优先从redis中获取
        ret = Rds.get(name.lower())
        data = {}
        if ret <> False:
            try:
                ret = json.loads(ret)
            except:
                ret = {}
            if lang == 'all':
                data = ret
            elif ret.has_key(lang):
                data = {lang:ret[lang]}
            return data

        # 如果redis链接失败，从数据库中查询
        return self._nameModel.get_name(name, lang)
    
    
    def get_one_image(self, name):
        name = name.strip()
        # 优先从redis中获取
        ret = Rds.get(name.lower())
        if ret <> False:
            try:
                ret = json.loads(ret)
            except:
                return ''
            if not ret.has_key("cover"):
                return ''
            else:
                return ret['cover']

        # 如果redis链接失败，从数据库中查询
        return self._nameModel.get_name_image(name)
    
    def add(self, name, name_dict):
        name = name.strip()
        name_dict['name'] = name
        ret = self._nameModel.add(name_dict)
        if ret[0]:
            self.refresh_cache_by_name(name)
        return ret
    
    def auto_complete_list(self, key, lang=None):
        names = self._nameModel.search(key, lang)
        _l = []
        for one in names:
            _l.append(one['name'])
        return _l
            
    
    def filter(self, names):
        for one in names:
            if one.has_key('tm_add'):
                one['tm_add'] = Common.seconds_to_str(one['tm_add'])
            if one.has_key('tm_mod'):
                one['tm_mod'] = Common.seconds_to_str(one['tm_mod'])
        return names
    
    #-------------------Super Functions Only For Operators---------------------
    """
    Func: 获取名称分页
    @param pager: 分页信息 Eg. {"ps":"10", "p":"1"}
    @param status: 名称状态，-1为全部
    @param key: 模糊匹配关键词 
    """
    def get_pager_list(self, pager, status=-1, key=None):
        pager = self._nameModel.get_pager_list(pager, status, key)
        pager['data'] = self.filter(pager['data'])
        return pager
    
    
    def get_pager_list_CN(self, pager, key=None):
        return self._nameModel.get_pager_list_CN(pager, key)
    
    def set_name_cover(self, name, cover):
        ret = self._nameModel.mod_by_cn_name(name, {"cover": cover})
        if ret:
            names = self._nameModel.get_by_cn_name(name)
            for one in names:
                self.refresh_cache_by_name(one['name'])
        return ret
        
    def mod(self, name, name_dict):
        name = name.strip()
        name_dict['name'] = name
        ret = self._nameModel.mod_by_name(name, name_dict)
        if ret:
            self.refresh_cache_by_name(name)
        return ret
    
    def mod_by_id(self, id, name_dict):
        name = self.get_by_id(id)
        if not name:
            return False
        name_dict['id'] = id
        ret = self._nameModel.mod_by_id(id, name_dict)
        if ret:
            if not self.refresh_cache_by_name(name['name']):
                Log.critical("Refresh name redis error: %s" % name['name'])
        return ret
    
    """
    # 同步所有名称数据到Redis
    """
    def refresh_cache(self):
        try:
            names = self._nameModel.get_all_names()
            for name in names:
                self.refresh_cache_by_name(name['name'])
        except Exception as e:
            print e
            return False
        return True
    
    """
    # 同步单个名称数据到Redis
    """
    def refresh_cache_by_name(self, name):
        name = name.strip()
        name_dict = self._nameModel.get_name(name, "all")
        if len(name_dict) == 0:
            return True
        #Rds.delete(name)
        return Rds.set(name.lower(), json.dumps(name_dict))
    
    
    # 目前Thrift模式有性能风险，查询依然采用直接从缓存redis库中选择
    """
    def get_name_by_langcode(self, name, langcode):
        if not name or name.strip() == '':
            return ''
        try:
            name = name.decode('gbk', 'ignore').encode('utf-8') # TODO trick 解决thrift夯住问题
            ret = Rocket.call_service("NameService", "get_one", name=name, language=langcode)
            #ret = Rocket('localhost', 30303).call_service("NameService", "get_one", name=name, language=langcode) 
            if ret[0] == ResultCode.SUCCESS and ret[2].has_key(langcode):
                return ret[2][langcode]
        except Exception, e:
            print str(e)
        return ''
    
    """
