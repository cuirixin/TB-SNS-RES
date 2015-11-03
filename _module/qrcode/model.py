#!/usr/bin/env python2.7
#-*- coding:utf8 -*-

from _module._base_m_ import BaseModel
from _module._lib.common import Common

class WxQRCodeModel(BaseModel):
    def __init__(self, uid = None):
        self._qr_table = 'qrcode_weixin'
        
    def get_all(self):
        sql = "select * from %s order by id asc"  % (self._qr_table)
        return self.get_rows(sql)
    
    def add(self, fields):
        return self._add(fields)

    def _add(self, fields):
        qrcode = {
            'title': {'type':'s', 'required':1},
            'ticket': {'type':'s', 'default':''},
            'description': {'type':'s', 'default':''},
            'add_time': {'type':'d', 'default':Common.get_current_time()},
        }
        
        ret = self._args_handle('insert', fields, qrcode)               
        if not ret[0]:
            return ret
        return self._insert(self._qr_table, qrcode)
    
    def mod(self, id, args):
        return self._mod(id, args)
    
    def _mod(self, id, args):
        qrcode = {
            'title': {'type':'s'},
            'ticket': {'type':'s'},
            'description': {'type':'s'},
            'edit_url': {'type':'s'},
            'show_url': {'type':'s'},
        }   

        ret = self._args_handle('update', args, qrcode)               
        if not ret[0]:
            return False
        
        if len(qrcode) == 0:
            return True
        
        where = "id=%d" % (int(id))
        ret = self._update(self._qr_table, qrcode, where)
        if not ret[0]:
            return False
        return True
    
    def add_scan_num(self, id):
        sql = "update %s set scan_num=scan_num+1 where id=%d" % (self._qr_table, int(id))
        return self.execute(sql)[0]

class QRModel(BaseModel):
    def __init__(self, uid = None):
        self._qr_table = 'qrcode'
        self._uid = uid
        
    def get_attr_by_uuid(self,uuid):
        sql = "select * from %s where uuid='%s' limit 1;"  % (self._qr_table,uuid)
        return self.get_one(sql)
    
    
    def add_attr_by_uuid(self,uuid,attr):
        sql = "insert into %s(uuid, fontcolor, backcolor)values('%s','%s','%s');"
        sql = sql % (self._qr_table,uuid,attr.get('fontcolor','#33aa33'),attr.get('backcolor','#ffffff'))
        return self.execute(sql)
    #每次只更改一个属性值
    def set_attr_by_uuid(self,uuid,attr):
        sql = "update %s set "  %  self._qr_table
        mutliattr = False
        if attr.has_key("fontcolor"):
            fontcolor = attr['fontcolor']
            sql = sql + "fontcolor='%s' " % fontcolor
            mutliattr = True
            
        if attr.has_key("backcolor"):
            backcolor = attr['backcolor']
            if mutliattr:
                sql +=", "
            sql = sql + " backcolor='%s'" % backcolor
            
        sql = sql + " where uuid = '%s'"  %  uuid
        return self.update(sql)
            
            
            
            
        
        