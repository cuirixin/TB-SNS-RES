#!/usr/bin/env python2.7
#-*- coding:utf8 -*-
#
# 2015-5-21 by Victor
# Copyright 2014 Tubban
from _module.thirdpart.model_wx import ThirdpartWeixinModel
from _module.user.model import UserModel
import ConfigParser
import os

CURRENT_PATH = os.path.dirname(__file__)

class ThirdpartWeixinControl:
    def __init__(self):
        self.cf = ConfigParser.ConfigParser() 
        #read config
        self.cf.read(CURRENT_PATH+"/../config_src/weixin.conf") 
        self.APPID = self.cf.get("auth", "APPID")
        self.APPSECRET = self.cf.get("auth", "APPSECRET")
        self._wxModel = ThirdpartWeixinModel()
        self._uModel = UserModel()
         
        
        
    def login_by_openid(self, openid):
        auth_user = self._wxModel.get_by_openid(openid)
        if not auth_user:
            return None
        user = self._uModel.get_brief_user_by_id(auth_user['uid'])
        
        tmp = {
            "id": user['id'],
            "username": user['username'],
            "group_id": user['group_id'],
            "mobile": user['mobile'],
            "mobile_code": user['mobile_code'],
            "email": user['email'],
            "sex": user['sex'],
            "icon": user['icon'],
        }
                
        return tmp
        
        
    
    """
    def get_user_unionid_by_openid(self, openid):
        method = self.cf.get('func-get_user_info', 'METHOD')
        url = self.cf.get('func-get_user_info', 'URL')
        access_token = self._wxModel.get_access_token()
        params = {
            "access_token": access_token,
            "openid": openid
        }
        
        unionid = None
        ret = Common.sendRequest(method, url, params)
        try:
            #{"errcode":40013,"errmsg":"invalid appid"}
            user = json.loads(ret)
            unionid = user['unionid']
        except:
            pass
        return unionid
    """
    
            
            
            
        
    
    
