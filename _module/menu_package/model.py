#!/usr/bin/env python2.7
#-*- coding:utf8 -*-
#
# 2014-2-13 by Victor
# Copyright 2014 Tubban
from _module._base_m_ import BaseModel
from _module._lib.common import Common

class MenuPackageModel(BaseModel):
    
    def __init__(self, uid = None):
        self._buffer_menu_package_table = "buffer_menu_package"
        self._uid = uid
        
    
    def add(self, fields):
        return self._add(fields)

    def _add(self, fields):
        
        order = {
            'rid': {'type':'d', 'default':0},
            'version': {'type':'d', 'default':0},
            'package': {'type':'s', 'default':0},
            'mod_time': {'type':'d', 'default':Common.get_current_time()},
        }
        
        ret = self._args_handle('insert', fields, order)               
        if not ret[0]:
            return ret
        return self._insert(self._buffer_menu_package_table, order)
    
    def get_by_rid(self, rid):
        sql = "SELECT version, package FROM %s WHERE rid=%d limit 1" % (self._buffer_menu_package_table, rid)
        return self.get_one(sql)
        
    def mod(self, order):
        return self._mod(order)
    
    def _mod(self, args):
        package = {
            'version': {'type':'d'},
            'package': {'type':'s'}
        }

        if not args.has_key('rid'):
            return False

        ret = self._args_handle('update', args, package)               
        if not ret[0]:
            return ret
        where = "rid=%d" % args['rid']
        if len(package) > 0:
            package['mod_time'] = {'type': 'd', 'value': Common.get_current_time()}
            ret = self._update(self._buffer_menu_package_table, package, where)
            if not ret[0]:
                return ret
        return ret

    