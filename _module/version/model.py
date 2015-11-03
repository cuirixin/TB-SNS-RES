#!/usr/bin/env python2.7
#-*- coding:utf8 -*-
#
# 2013-12-4 by Victor
# Copyright 2013 Tubban
from _module._base_m_ import BaseModel

class VersionModel(BaseModel):
    
    def __init__(self, uid = None):
        self._version_table = 'version'
        self._uid = uid

    def get_version(self, name):
        sql = "select version from %s WHERE name='%s' " \
                % (self._version_table, name)
        return self.get_one(sql)
