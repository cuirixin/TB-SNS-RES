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
        self._image_avator = 'image_avator'

    def get_avator_id(self, uid):
        sql = "SELECT id FROM %s WHERE uid='%s'" % (self._image_avator, uid)
        one = self.get_one(sql)
        if one:
            return str(one['id'])
        sql = "INSERT INTO %s(`uid`) VALUES('%s')" % (self._image_avator, uid)
        id = self.execute(sql)[1]
        dir_index = int(id / 10000) + 1
        dir_path = config_base.setting['upload_avator'] + str(dir_index)
        if not os.path.isdir(dir_path):
            os.makedirs(dir_path, 0777)
        return str(id)
        
        
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

        
    