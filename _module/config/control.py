#!/usr/bin/env python2.7
#-*- coding:utf8 -*-
#
# 2013-12-4 by Victor
# Copyright 2013 Tubban
from _module.config.model import UConfigModel
import copy
import json

class UConfigControl:
    def __init__(self, uid = None,userLang=None):
        self._uid = uid
        self._ucModel = UConfigModel(self._uid)

    def mod(self, uconfig):
        try:
            info = json.loads(uconfig['info'])
        except Exception, e:
            return False
        return self._ucModel.mod(uconfig)
    
    def _init_default(self, uid, config_name):
        uconfig = dict()
        uconfig['uid'] = uid
        uconfig['name'] = config_name
        if config_name == UConfigModel.INVIATION_NAME:
            uconfig['info'] = UConfigModel.INVITATION_CONFIG
            
        if not uconfig.has_key('info'):
            return None
        
        _config = copy.deepcopy(uconfig)
        _config['info'] = json.dumps(_config['info'])
        self._ucModel.mod(_config)
        return uconfig

    # 详情
    def detail(self, uid, config_name):
        uconfig = self._ucModel.detail(uid, config_name)
        if uconfig is None:
            return self._init_default(uid, config_name)
        return self._format(uconfig)
        
    def _format(self, uconfig):
        
        if not uconfig:
            return None
        else:
            if uconfig.has_key('info'):
                try:
                    uconfig['info'] = json.loads(uconfig['info'].replace("\\",""))
                except Exception, e :
                    print str(e)
                    return None
            return uconfig
                