#!/usr/bin/env python2.7
#-*- coding:utf8 -*-
#
# 2013-12-4 by Victor
# Copyright 2013 Tubban
from _module import const
from _module._lib.common import Common
from _module._lib.lang import Lang
from _module.business.model import BusinessModel
from _module.discover.model import DiscoverModel
from _module.image.model import ImageModel

class DiscoverControl:
    def __init__(self, uid = None,userLang=None):
        self._uid = uid
        self._dcModel = DiscoverModel(self._uid)
        self._bModel = BusinessModel(self._uid)
        self._iModel = ImageModel(self._uid)
        self._field = Lang.get_db_field_name(userLang)
        
    def get_by_id(self, id):
        return self._dcModel.get_by_id(id)
                
    def like(self, id, uuid=None, uid=None):
        
        if self._dcModel.has_like(id, uid):
            return -1
        
        ret =  self._dcModel.add_like(id, uid)
        # 相应的business图片添加like
        if ret:
            self._bModel.ugc_image_like(uuid)
        return ret
    
    def add(self, discover):
        ret = self._dcModel.add(discover)
        if ret[1]:
            self._iModel.del_tmp(discover['image_uuid'])
        return ret
    
    def delete(self, id):
        return self._dcModel.change_status(id, const.Discover.STATUS_DELETE)
        
    def get_pager_list(self, pager, order_type, position=None):
        if order_type <> 5:
            position=None
        data = self._dcModel.get_pager_list(pager, order_type, position)
        list = data['data']
        for one in list:
            one = self.filter(one, position)
        data['data'] = list
        return data
    
    def filter(self, discover, position=None):
        #if discover.has_key('add_time'):
        #    discover['add_time'] = Common.seconds_to_str(discover['add_time'], const.Date_Format.DATETIME)
        
        if position:
            discover['distance'] = Common.get_distance(discover['lat'], discover['lon'], position['lat'], position['lon'])
        discover['has_like'] = 0
        if self._uid is not None and self._dcModel.has_like(discover['id'], self._uid):
            discover['has_like'] = 1
        
        return discover
    