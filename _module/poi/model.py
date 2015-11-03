#!/usr/bin/env python2.7
#-*- coding:utf8 -*-
#
# 2013-12-4 by Victor
# Copyright 2013 Tubban
from _module import const
from _module._base_m_ import BaseModel
from _module._lib.common import Common
from _module._lib.lang import Lang

class POIModel(BaseModel):
    
    def __init__(self, uid = None):
        self._business_table = 'business'
        self._uid = uid
    
    
    def get_businesses_by_ids(self, ids):
        ids = ','.join(ids)
            
        sql="SELECT id, uuid, mobile, name, name_cn, status, phone, score, lat, " \
            " lon, description, address, category,cover, owner, country_id, city_id, currency_id, " \
            " like_num, wantgo_num, collect_num, menu_num, meal_num " \
            " FROM %s " \
            " WHERE `status`>%s AND `id` in (%s) " \
            % (self._business_table, const.Business.STATUS_DELETE, ids)

        return self.get_rows(sql)
        
    def get_business_by_id(self, id):
        sql="SELECT id, uuid, mobile, name, name_cn, status, phone, score, lat, " \
            " lon, description, address, category,cover, owner, country_id, city_id, currency_id, " \
            " like_num, wantgo_num, collect_num, menu_num, meal_num " \
            " FROM %s " \
            " WHERE `status`>%s AND `id`=%d " \
            % (self._business_table, const.Business.STATUS_DELETE, int(id))

        return self.get_one(sql)
        
