#!/usr/bin/env python2.7
#-*- coding:utf8 -*-
#
# 2013-12-4 by Victor
# Copyright 2013 Tubban
from _module import const
from _module._lib.common import Common
from _module._lib.lang import Lang
from _module._lib.log import Log
from _module._lib.mem import Mem
from _module._lib.session import Session
from _module.friend.model import FriendModel
from _module.push.control import PushControl
from _module.role.model import RoleModel
from _module.user.model import UserModel
import json

class UserControl:
    def __init__(self, uid = None, userLang=None): 
        self._uid = uid
        self._uModel = UserModel(self._uid)
        self._fModel = FriendModel(self._uid)
        #self._mModel = MobileModel(self._uid)
        self._roleModel = RoleModel(self._uid)
        self._field = Lang.get_db_field_name(userLang)
        
        
    def get_brief_user_by_id(self, uid):    
        return self._uModel.get_brief_user_by_id(uid)
    
    #####################TODO
    # 添加新用户
    def add(self, user):
        # 添加到user表
        ret = self._uModel.add(user)
        if not ret[0]:
            return ret
        creator = ret[1]
        # 添加sys_role到auth_role
        if user['group_id'] == const.User.GROUP_ADMIN:
            self._roleModel.copy_sys_to_auth(creator)
        return ret
    
    def mod(self, uid, user):
        user['uid'] = uid
        return self._uModel.mod(user)
    
    def gen_username(self, preffix='tb_'):
        return self._uModel.gen_username(preffix)
    
    def send_dynamic_code(self, uid):
        # 生成动态码
        dynamic_code = str(Common.gen_random_int(length=4))
        # 存入MC， 过期时间为30分钟
        Mem.set("MOBILE_DYNAMIC_CODE-%d" % uid, dynamic_code, 30*60) # 30分钟 
        # TODO 推送
        
        return dynamic_code

    def check_dynamic_code(self, uid, code):
        dynamic_code = Mem.get("MOBILE_DYNAMIC_CODE-%d" % uid)
        if dynamic_code == code:
            Mem.delete("MOBILE_DYNAMIC_CODE-%d" % uid)
            return True
        return False
    
    
    def send_dynamic_code_alone(self, mobile, mobile_code):
        if not mobile or not mobile_code:
            return False
        # 生成动态码
        dynamic_code = str(Common.gen_random_int(length=6))
        # 存入MC， 过期时间为30分钟
        code_token = "DY_CODE-%s" % Common._md5(mobile_code+mobile)
        if not Mem.set(code_token, dynamic_code, 30*60): # 30分钟 
            return False
        
        # TODO 推送短信, 暂时不剥离
        msg = {
          "type": const.PUSH.CODE_MOBILE_CHECK,
          "code": "push_mobile_check",
          "receiver": 0,
          "content": "%s (您的动态验证码，一般人儿我不告诉他)" % dynamic_code,
          "extra": json.dumps({"mobile_code": mobile_code, "mobile": mobile})
        }
        PushControl().push_one(msg)
        Log.critical(msg['extra'])
        return dynamic_code
    
    def refresh_session(self, _request, _session, uid):
        user = self.get_brief_user_by_id(uid)
        if not user:
            return False
        user['_cache'] = {} # TODO self.get_catch_data(uid)
        tmp = {
            "id": user['id'],
            "username": user['username'],
            "group_id": user['group_id'],
            "mobile": user['mobile'],
            "creator": user['creator'],
            "mobile_code": user['mobile_code'],
            "email": user['email'],
            "sex": user['sex'],
            "icon": user['icon'],
            "login_ip": _request.remote_ip,
            "last_refresh": Common.get_current_datestr(),
            "_cache": user['_cache']
        }
        _session.set('user', tmp)
        
        # 更新用户SESSION正索引
        ids_str = Mem.get(str(user['id']))
        cur_sessionid = _session.get_sessionid()
        # Log.critical(cur_sessionid)
        ids = [cur_sessionid]
        if ids_str:
            ids = ids_str.split(',')
            if cur_sessionid in ids:
                ids.remove(cur_sessionid)
            ids.append(cur_sessionid)
            
            # Log.critical(ids)
            rm_arr = ids[:-3] # 最多三个设备登录
            # Log.critical(rm_arr) 
            
            # 删除Key
            for one in rm_arr:
                Mem.delete(one)
            
        # Log.critical(','.join(ids[-3:]))
        Mem.set(str(user['id']), ','.join(ids[-3:]))
        
        return tmp
        
    
    def set_catch_data(self, uid, value, key=None):
        ret = self.get_catch_data(uid, key)
        if not ret or not isinstance(ret, dict) :
            ret = {}

        ret[key] = value
        try:
            code_token = "USER_CACHE_%s" % uid
            ret = Mem.set(code_token, json.dumps(ret))
            if ret:
                ret = json.loads(ret)
                return ret[key]
        except Exception as e:
            print str(e)
            return False
        return True
        
        
    def get_catch_data(self, uid, key=None):
        try:
            code_token = "USER_CACHE_%s" % uid
            ret = Mem.get(code_token)
            if ret:
                ret = json.loads(ret)
                if key:
                    return ret[key]
                return ret
        except Exception as e:
            print str(e)
        return ''

    def check_dynamic_code_alone(self, mobile, mobile_code, code):
        code_token = "DY_CODE-%s" % Common._md5(mobile_code+mobile)
        dynamic_code = Mem.get(code_token)
        print code, dynamic_code
        if code == dynamic_code:
            Mem.delete(code_token)
            return True
        return False
    
    def login_by_mobile(self, mobile, mobile_code, password):
        return self._uModel.login_by_mobile(mobile, mobile_code, password)
        
        
    
    
    
    ############################################### 以上是一期在使用的方法
    
    
    def login(self, username, password):
        user = self._uModel.login(username, password)
        if user:
            if user['source'] == 3 or user['source'] == 4:
                user['is_facebook_user'] = 1
            else:
                user['is_facebook_user'] = 0
        user = self._uModel.filter([user])[0]
        return user
    
    
    def search(self, key, limit=10):
        users = self._uModel.search(key, limit)
        for user in users:
            if self._fModel.is_friend(self._uid, user['id']):
                user['is_friend'] = 1
            else:
                user['is_friend'] = 0
        return users
    
    def get_pager_list(self, pager, group_id=0, key='', status=0):
        
        pager = self._uModel.get_pager_list(pager, group_id, key, status)
        _list = pager['data']
        for one in _list:
            one['add_time'] = Common.seconds_to_str(one['add_time'], const.Date_Format.DATETIME)
        pager['data'] = _list
        return pager
        
    def get_by_mobile(self, mobile, code):
        return self._uModel.get_by_mobile(mobile, code)
    
    def get_by_username(self, username):
        return self._uModel.get_by_name(username)
