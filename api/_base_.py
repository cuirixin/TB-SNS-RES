#!/usr/bin/env python2.7
#-*- coding:utf8 -*-
################################################################################
#
# Copyright (c) 2015 Tubban.com, Inc. All Rights Reserved
#
################################################################################
from _module import msg
from _module._lib.log import Log
from _module._lib.session import Session
from tornado import locale
from tornado.web import RequestHandler
import config_base
import functools
import hashlib
import json
import pprint
import tornado.escape
"""
API Base Controller Module.

Authors: cuirixin(rixin.cui@tubban.com)
Date:    2014/10/15
"""

def auth_app(method):
    """auth key verification decorator for common request.
    """
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if isinstance(self, RequestHandler):
            if self.auth_auth_key() == False:
                self.set_code(msg.API_Code.SYS_TOKEN_ERROR)
                self.set_message(msg.API_Desc.SYS_TOKEN_ERROR)
                self.display()
                self.finish()
                return
        return method(self, *args, **kwargs)
    return wrapper

def auth_user(method):
    """auth user sign in verification decorator for common request.
    """
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if isinstance(self, RequestHandler):
            if self.auth_auth_key() == False:
                self.set_code(msg.API_Code.SYS_TOKEN_ERROR)
                self.set_message(msg.API_Desc.SYS_TOKEN_ERROR)
                self.display()
                self.finish()
                return
            elif self.is_login() == False:
                self.set_code(msg.API_Code.SYS_ACCESS_EXPIRES)
                self.set_message(msg.API_Desc.SYS_ACCESS_EXPIRES)
                self.display()
                self.finish()
                return
        return method(self, *args, **kwargs)
    return wrapper

class BaseHandler(RequestHandler):  
    """Base Handler For API Controller
    """
    def initialize(self, method = ''):
        """Init private params
        """
        self._session = Session(self, config_base.store['memcached_user']['session']['app_time_out'])
        self._locale = self.get_user_locale()
        self._userLang = self._locale.code
        self._ret = {'SESSIONID':tornado.escape.url_escape(self._session.get_sessionid()),
                     'code':msg.API_Code.SYS_OK, 'message' : msg.API_Desc.SYS_OK, 'data' : None} 
        self._validate = dict(valid= 'false', message='Post argument missing.')
        # 版本信息
        self._version = self.get_argument('_vs_', '1')

    def get_user_locale(self):
        """Return current request locale 
        """
        localeLang = self.get_argument('_i18n_', '')
        if localeLang <> '':
            # self.request.headers["Accept-Language"] = localeLang
            return locale.get(localeLang)
        else:
            return self.get_browser_locale()
        
        
    def is_login(self):
        if self.get_current_user() is None:
            return False
        else:
            return True
        
    def get_current_user(self):
        """
        @overrite 
        Return current sign in user info 
        """
        return self._session.get('user')
    
    def get_current_uid(self):
        """Return current sign in user's id 
        """
        user = self.get_current_user()
        if not user:
            return None
        return user['_id']

    def get_num(self, param, default = 0):
        """Return integer param from the request 
        """
        num =  self.get_argument(param, default)
        ret = 0
        try:
            ret = int(num)
        except:
            pass
        return ret

    def pack_args(self, args=[]):
        """Parse 's' param from the request
        """
        # 验证s参数是否合法
        in_vals = self.get_argument("s", "{}")
        if in_vals.strip() == '' or in_vals.strip() == 'null':
            in_vals = "{}"
        try:
            in_vals = json.loads(in_vals)
        except Exception,e:
            return [False, "JSON Format Error."]
        
        if not isinstance(in_vals, dict):
            return [False, "JSON Format Error."]
        
        values = {}
        for (k,v) in args.items():
            val = None
            # 如果未传值，验证是否必须传值或者设置默认值
            if not in_vals.has_key(k):
                if v.has_key('required') and v['required'] == 1:
                    return [False, "key: %s is required" % k]
                if v.has_key('default'):
                    values[k] = v['default']
                    continue
            else:
                if v['type'] == 'd':
                    try:
                        val = int(in_vals[k])
                    except Exception as e:
                        return [False, "key: %s's value is not an integer" % k]
                    # 长度验证
                    if v.has_key('max'):
                        if val > v['max']:
                            return [False, "key: %s's larger than %d " % (k, v['max'])]
                    if v.has_key('min'):
                        if val < v['min']:
                            return [False, "key: %s's less than %d " % (k, v['min'])]
                    if v.has_key('range'):
                        if val > v['range'][1] or val < v['range'][0]:
                            return [False, "key: %s's is not in range [%d,%d] " % (k, v['range'][0], v['range'][1])]
                    if v.has_key('in'):
                        if not val in v['in']:
                            return [False, "key: %s's value must be in array %s " % (k, str(v['in']))]
                elif v['type'] == 'f':
                    try:
                        val = float(in_vals[k])
                    except Exception as e:
                        return [False, "key: %s's value is not a float" % k]
                elif v['type'] == 'dict':
                    try:
                        if isinstance(in_vals[k], dict):
                            val = in_vals[k]
                        elif isinstance(in_vals[k], str):
                            val = json.dumps(in_vals[k])
                    except Exception as e:
                        return [False, "key: %s's value is not a dict or dict json string" % k]
                elif v['type'] == 'list':
                    try:
                        if isinstance(in_vals[k], list):
                            val = in_vals[k]
                        elif isinstance(in_vals[k], str):
                            val = json.dumps(in_vals[k])
                        else:
                            raise Exception()

                        if v.has_key('maxsize'):
                            if len(val) > v['maxsize']:
                                return [False, "key: %s's size is more than %d " % (k, v['maxsize'])]

                    except Exception as e:
                        return [False, "key: %s's value is not a list or list json string" % k]

                else:
                    val = str(in_vals[k])
                    length = len(val)
                    # 长度验证
                    if v.has_key('maxlen'):
                        if length > v['maxlen']:
                            return [False, "key: %s's length is more than %d " % (k, v['maxlen'])]
                    if v.has_key('minlen'):
                        if length < v['minlen']:
                            return [False, "key: %s's length is less than %d " % (k, v['minlen'])]
                    if v.has_key('range'):
                        if length > v['range'][1] or length<v['range'][0]:
                            return [False, "key: %s's length is not in range [%d,%d] " % (k, v['range'][0], v['range'][1])]
                    if v.has_key('in'):
                        if not val in v['in']:
                            return [False, "key: %s's value must be in array %s " % (k, str(v['in']))]
            values[k] = val;
            
        return [True, values]

    def display(self):
        """
        @overrite 
        Return data for the request
        """
        try:
            if self._ret['data'] is not None:
                try:
                    if len(self._ret['data']) <= 0:
                        self._ret['data'] = []
                except:
                    pass
            #print self._ret
            self.write(tornado.escape.json_encode(self._ret))
        except Exception as e:
            print e
            
    def display_para_error(self, _msg=None):
        self.set_code(msg.API_Code.SYS_PARAM_ERROR)
        if _msg is None:
            self.set_message(msg.API_Desc.SYS_PARAM_ERROR)
        else:
            self.set_message(_msg)
        self.display()
        self.finish()
        
    def display_internal_error(self):  
        self.set_code(msg.API_Code.SYS_INTERNAL_ERROR)
        self.set_message(msg.API_Desc.SYS_INTERNAL_ERROR)
        self.display()
        self.finish()

    def display_code_error(self, code, msg="o(╯□╰)o"):
        self.set_code(code)
        self.set_message(msg)
        self.display()
        self.finish()

    def display_access_expires(self):
        self.set_code(msg.API_Code.SYS_ACCESS_EXPIRES)
        self.set_message(msg.API_Desc.SYS_ACCESS_EXPIRES)
        self.display()
        self.finish()
        
    def display_validate(self):
        self.write(json.dumps(self._validate))
            
    def set_data(self, val):
        self._ret['data'] = val
 
    def add_data(self, key, val, over = False):
        if over == True:
            self._ret['data'] = val
        else:
            if isinstance(self._ret['data'], dict) == False:
                self._ret['data'] = dict()
            self._ret['data'][key] = val
    
    def remove_key(self, key):
        if isinstance(self._ret['data'], dict) == True \
            and self._ret['data'].has_key(key) == True:
            del self._ret['data'][key]
    
    def set_code(self, error_code):
        self._ret['code'] = error_code
    
    def set_message(self, error_message):
        self._ret['message'] = error_message

    def auth_auth_key(self, key=config_base.store['memcached_user']['session']['app_auth_key']):
        sign = self.get_argument('sign', None)
        auth_key = self.get_argument('auth_key', None)
        if auth_key is None:
            # 进入sign验证
            s = self.get_argument('s', '')
            sha1obj = hashlib.sha1()
            sha1obj.update(s+key)
            _sign = sha1obj.hexdigest()
            if _sign <> sign:
                return False
        else:
            if auth_key <> key:
                return False
        return True

    # 取消cookir验证，接口部分必须加
    def check_xsrf_cookie(self):
        pass

    def get_pager(self, p=1,ps=20, sf=None,st=None):
        _pager=dict()
        
        ret = self.pack_args({
        'p': {'type': 'd', 'default': p},
        'ps': {'type': 'd', 'default': ps},
        })
        
        _pager['p']=ret[1]['p']
        _pager['ps']=ret[1]['ps']
        #_pager['st']=str(self.get_argument("st",sf))
        #_pager['sf']=str(self.get_argument("sf",st))
        #_pager['psum'] = 0 # 总共页数
        _pager['total'] =0 # 总数目
        return _pager

    def get_platform(self):
        _types = ['windows nt', 'iphone', 'ipad', 'android'] 
        platform = {'windows nt':'Web', 'iphone':'IOS', 'ipad':'IOS', 'android':'Android'}
        agent = self.request.headers['User-Agent'].lower()
        
        for type in _types:
            index = agent.find(type)
            if index <> -1:
                return platform[type]
        return 'Web'

    def prepare(self):
        """
        if self.request.headers["Content-Type"].startswith("application/json"):
            self.json_args = json.loads(self.request.body)
        else:
            self.json_args = None
        """
        pass
    
    """
    def _set_login_user(self, user):
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
            "login_ip": self.request.remote_ip,
            "_cache": user['_cache']
        }
        
        self._session.set('user', tmp)
        return tmp
    """
    