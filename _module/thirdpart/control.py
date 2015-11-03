#!/usr/bin/env python2.7
#-*- coding:utf8 -*-
#
# 2014-2-9 by Victor
# Copyright 2014 Tubban
from _module._lib.log import Log
from _module.thirdpart.model import ThirdpartAccountModel
from _module.user.control import UserControl
from _module.user.model import UserModel

class ThirdpartAccountControl:
    def __init__(self, uid = None):
        self._uid = uid
        self._tdAccountModel = ThirdpartAccountModel(uid)
        self._userControl = UserControl()
        self._userModel = UserModel()
    
    """
    account : {
        "type": 1,
        "openid": "xxx",
        "uid": 1
    }
    """
    def bound_thirdpart_account(self, account):
        one = self._tdAccountModel.find_by_openid(account['type'], account['openid'])
        if not one:
            if not self._tdAccountModel.add(account)[0]:
                return False
        return self._tdAccountModel.mod(account['type'], account['openid'], account)

    def login_by_openid(self, type, openid):
        one = self._tdAccountModel.find_by_openid(type, openid)
        if not one:
            return None
        uid = one['uid']
        if uid == 0:
            return None
        user = self._userModel.get_brief_user_by_id(uid)
        user['current_city'] = self._userControl.get_catch_data(user['id'], 'current_city')
        return user
        
    def get_openid_by_uid(self, type, uid):
        account = self._tdAccountModel.find_by_uid(type, uid)
        if not account:
            return None
        return account['openid']
    
        
