#!/usr/bin/env python2.7
#-*- coding:utf8 -*-
from _module.qrcode.model import QRModel, WxQRCodeModel

class WxQRCodeControl(object):
    def __init__(self, uid = None,userLang=None):
        self._uid = uid
        self._qrModel = WxQRCodeModel(self._uid)
        
    def get_all(self):
        return self._qrModel.get_all()
    
    def add(self, qrcode):
        return self._qrModel.add(qrcode)
    
    def mod(self, id, qrcode):
        return self._qrModel.mod(id, qrcode)
    
    def increase_scan_num(self, id):
        return self._qrModel.add_scan_num(id)

    
class QRCodeControl(object):
    def __init__(self, uid = None,userLang=None):
        self._uid = uid
        self._qrModel = QRModel(self._uid)
        
        
    def get_attr_by_uuid(self,uuid):
        return self._qrModel.get_attr_by_uuid(uuid)
    
    def add_attr_by_uuid(self,uuid,attr):
        return self._qrModel.add_attr_by_uuid(uuid,attr)
    
    def set_attr_by_uuid(self,uuid,attr):
        return self._qrModel.set_attr_by_uuid(uuid,attr)