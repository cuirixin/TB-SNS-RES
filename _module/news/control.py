#!/usr/bin/env python2.7
#-*- coding:utf8 -*-
#
# 2013-12-4 by Victor
# Copyright 2013 Tubban
from _module import const
from _module._lib.lang import Lang
from _module.business.model import BusinessModel
from _module.news.model import BnewsModel

class BnewsControl:
    def __init__(self, uid = None,userLang=None):
        self._uid = uid
        self._nModel = BnewsModel(self._uid)
        self._bModel = BusinessModel(self._uid)
        self._field = Lang.get_db_field_name(userLang)
        
    def get_by_id(self, id):
        return self._nModel.get_by_id(id)
                
    def like(self, id, uid=None):
        if self._nModel.has_like(id, uid):
            return True
        
        ret =  self._nModel.add_like(id, uid)
        return ret
    
    def add(self, news):
        ret = self._bnModel.add(news)
        return ret
    
    def delete(self, id):
        return self._bnModel.change_status(id, const.Bnews.STATUS_DELETE)
        
    def add_news_image(self, image):
        ret = self._bnModel.add_image(image)
        if ret[0]:
            self._iModel.del_tmp(image['uuid'])
        return ret
    
    def get_news_images(self, news_id):
        return self._bnModel.get_news_images(news_id)
    
    def get_pager_list(self, pager, b_id):
        data = self._nModel.get_pager_list(pager, b_id)
        list = data['data']
        for one in list:
            one = self.filter(one)
        data['data'] = list
        return data
    
    def get_reply_pager_list(self, pager, news_id):
        return self._nModel.get_reply_pager_list(pager, news_id)
    
    def filter(self, news):
        news['has_like'] = 0
        if self._uid is not None and self._nModel.has_like(news['id'], self._uid):
            news['has_like'] = 1
        news['images'] = self._nModel.get_news_images(news['id'])
        return news
    
    def add_reply(self, news_id, content):
        reply = {
            "news_id" : news_id,
            "uid" : self._uid,
            "content" : content
        }
        return self._nModel.add_reply(reply)
        
    def get_reply_by_id(self, news_id, reply_id):
        return self._nModel.get_reply_by_id(news_id, reply_id)
    
    def delete_reply(self, news_id, reply_id):
        return self._nModel.delete_reply(news_id, reply_id)
    
    def detail(self, news_id):
        news = self._bnModel.get_by_id(news_id)
        if not news:
            return None
        news['images'] = self._bnModel.get_news_images(news_id)
        return news
