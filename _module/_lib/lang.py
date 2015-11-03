#!/usr/bin/env python2.7
#-*- coding:utf8 -*-
'''
Created on 2014-4-10

@author: cuirixin
'''

class Lang(object):
    
    support_langs = {
        7:'zh',
        12:'en',
        16:'fr',
        17:'de',
        26:'ko',
        2:'ar',
        34:'ru'
    }
    
    langcode_2_reqcode = {
        'en':'EN', # 英语
        'zh':'CN', # 汉语
        'fr':'FR', # 法语
        'de':'DE', # 德语
        'ar':'AR', # 阿拉伯语
        'ru':'RU', # 俄语
        'ko':'KO'  # 韩语
    }
    
    dbfield_2_langcode = {
        'EN':'en',
        'CN':'zh',
        'FR':'fr',
        'DE':'de',
        'AR':'ar',
        'RU':'ru',
        'KO':'ko'
    }
    
    # 通过获取redis中存储的语言key值
    @staticmethod
    def get_code_by_lanid(id=12):
        if not Lang.support_langs.has_key(id):
            return 'en'
        else:
            return Lang.support_langs[id]
        
    # 通过Request Header中的locale Language获取redis中存储的语言key值
    @staticmethod
    def get_code_by_req_code(userLang):
        code = 'en'
        if userLang:
            if userLang == 'zh_CN' or userLang.upper()=='ZH_CN' or userLang.upper() == 'CN':
                return 'zh'
            elif userLang == 'fr' or userLang.upper() == 'FR':
                return 'fr'
            elif userLang == 'de' or userLang.upper() == 'DE':
                return 'de'
            elif userLang == 'ar' or userLang.upper() == 'AR':
                return 'ar'
            elif userLang == 'ko' or userLang.upper() == 'KO':
                return 'ko'
            elif userLang == 'ru'or userLang.upper() == 'RU':
                return 'ru'
        return code
    
    # 获取redis中存储的语言key值
    @staticmethod
    def get_code_by_dbfield(dbfield):
        code = 'en'
        if Lang.dbfield_2_langcode.has_key(dbfield):
            return Lang.dbfield_2_langcode[dbfield]
        return code
    
    """
    Request Header中的locale Language映射到数据库字段
    """
    @staticmethod
    def get_db_field_name(userLang):
        field = 'EN'
        if userLang:
            if userLang == 'zh_CN' or userLang.upper() == 'ZH_CN' or userLang.upper() == 'CN':
                return "CN"
            elif userLang == 'fr' or userLang.upper() == 'FR':
                return 'FR'
            elif userLang == 'de'or userLang.upper() == 'DE':
                return 'DE'
            elif userLang == 'ar' or userLang.upper() == 'AR':
                return 'AR'
            elif userLang == 'ko' or userLang.upper() == 'KO':
                return 'KO'
            elif userLang == 'ru'or userLang.upper() == 'RU':
                return 'RU'
        return field
    