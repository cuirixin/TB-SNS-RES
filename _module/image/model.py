#!/usr/bin/env python2.7
#-*- coding:utf8 -*-
#
# 2013-12-4 by Victor
# Copyright 2013 Tubban
from _module import const
from _module._base_m_ import BaseModel
from _module._lib.common import Common
import config_base
import os

class ImageModel(BaseModel):
    
    def __init__(self, uid = None):
        self._tmp_image_table = 'image_tmp'
        self._image_id_generator = 'image_id_generator'
        self._image_ugc_id_generator = 'image_ugc_id_generator'
        
        self._image_table = 'b_image'
        self._image_ugc_table = 'b_image_ugc'
        self._uid = uid
        
    def gen_id(self):
        sql = "INSERT INTO %s(`add_time`) VALUES(%d)" % (self._image_id_generator, Common.get_current_time())
        id = self.execute(sql)[1]
        dir_index = int(id / 10000) + 1
        dir_path = config_base.setting['upload_image'] + str(dir_index)
        if not os.path.isdir(dir_path):
            os.makedirs(dir_path, 0777)
        return str(id)
    
    def gen_ugc_id(self):
        sql = "INSERT INTO %s(`add_time`) VALUES(%d)" % (self._image_ugc_id_generator, Common.get_current_time())
        id = self.execute(sql)[1]
        dir_index = int(id / 10000) + 1
        dir_path = config_base.setting['upload_image_ugc'] + str(dir_index)
        if not os.path.isdir(dir_path):
            os.makedirs(dir_path, 0777)
        return str(id)
         

    def add_tmp(self, uuid):
        sql = "INSERT INTO %s(`uuid`,`add_time`) VALUES('%s', %d)" \
                % (self._tmp_image_table, uuid, Common.get_current_time())
        return self.execute(sql)
    
    def del_tmp(self, uuid):
        sql = "DELETE FROM %s WHERE uuid='%s' " \
                % (self._tmp_image_table, uuid)
        return self.execute(sql)
    
    def delete_business_image(self, uuid):
        sql = "UPDATE %s SET status=%d WHERE uuid='%s' " \
                % (self._image_table, const.Image.STATUS_DELETE, uuid)
        return self.execute(sql)[0]

    def delete_business_ugc_image(self, uuid):
        sql = "UPDATE %s SET status=%d WHERE uuid='%s' " \
                % (self._image_ugc_table, const.Image.STATUS_DELETE, uuid)
        return self.execute(sql)[0]
        
    