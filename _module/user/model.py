#!/usr/bin/env python2.7
#-*- coding:utf8 -*-
#
# 2013-12-4 by Victor
# Copyright 2013 Tubban
from _module import const
from _module._base_m_ import BaseModel
from _module._lib.common import Common

class UserModel(BaseModel):
    def __init__(self, uid = None):
        self._table = 'auth_user'
        self._table_friends = 'auth_user_friends'
        self._table_online = 'record_user_online'
        self._table_online = 'record_user_online'
        self._table_group = 'auth_group'
        self._uid = uid
    
    def get_brief_user_by_id(self, uid, fields=None):
        if fields is None:
            fields = ["id", "username", "creator", "sex", "email", "group_id","status", "icon", "mobile", "mobile_code", "last_name", "first_name"]
        fields_str = self._gen_fields_str(fields)
        sql = "SELECT %s FROM %s WHERE id=%d LIMIT 1" % (fields_str, self._table, uid)
        return self.get_one(sql)
    
    ##############################TODO
    
    def get_by_id(self, uid):
        sql = "SELECT u.* FROM auth_user u WHERE u.id=%d LIMIT 1" % (int(uid))
        one = self.get_one(sql)
        if one:
            del one['password']
            del one['nike']
        return one
        
    def _add(self, fields):
        
        user = {
            'username': {'type':'s', 'required':1},
            'email': {'type':'s', 'default':''},
            'mobile': {'type':'s', 'default':''},
            'mobile_code': {'type':'s', 'default':'+86'},
            'sex': {'type':'d', 'default':-1},
            'password': {'type':'s', 'default':''},
            'status': {'type':'d', 'default':const.User.STATUS_NORMAL},
            'first_name': {'type':'s', 'default':''},
            'last_name': {'type':'s', 'default':''},
            'last_login': {'type':'d', 'default': 0},
            'group_id':{'type':'d', 'default':const.User.GROUP_NORMAL},
            'add_time': {'type':'d', 'default':Common.get_current_time()},
            'nike':{'type':'s', 'default':''},
            'source': {'type':'d', 'default':const.User.SOURCE_NORMAL},
            'source_channel_id': {'type':'d', 'default':0},
            'reg_platform': {'type':'s', 'default':const.User.REG_PLAT_WEB},
            'opd': {'type':'s', 'default':''},
        }
        
        ret = self._args_handle('insert', fields, user)     
        
        if not ret[0]:
            # todo:
            print ret[1]
            return ret
        return self._insert(self._table, user)
    
    # creator区分是否为注册方式添加
    def add(self, kwarg, creator=None):
        ret = self._add(kwarg)
        if not ret[0]:
            return ret
        uid = ret[1]
        if creator is None:
            self.mod({'uid':uid, 'creator':uid})
        else:
            self.mod({'uid':uid, 'creator':creator})
        return ret
    
    def gen_username(self, preffix="tb_"):
        sql = "SELECT id FROM %s ORDER BY id desc LIMIT 1" % self._table
        user = self.get_one(sql)
        if not user:
            return preffix+str(0)
        username = preffix+str(user['id'])
        while 1:
            if self.get_by_name(username):
                username = username + str(Common.gen_random_int(4))
            else:
                break
        return username
        
    
    def login_by_mobile(self, mobile, mobile_code, password):
        fields = ["id","username", "sex", "email", "group_id", "creator", "icon", \
                  "mobile_code", "mobile", "source", "first_name", "last_name"]
        sql = "SELECT %s FROM %s u " \
                " WHERE u.mobile='%s' " \
                " AND u.mobile_code='%s' " \
                " AND u.password='%s' " \
                " AND u.status!=%d LIMIT 1 " % \
                (self._gen_fields_str(fields), 
                 self._table, 
                 self.escape_string(mobile), 
                 self.escape_string(mobile_code), 
                 self.escape_string(password), 
                 const.User.STATUS_DESTROYED)
        user = self.get_one(sql)
        if user:
            self.mod({'uid':user['id'], 'last_login':Common.get_current_time()})
        return user

    def login(self, username, password):
        fields = ["id","username", "sex", "email", "group_id", "creator", "icon", \
                  "mobile_code", "mobile", "source", "first_name", "last_name"]
        sql = "SELECT "+ self._gen_fields_str(fields) +" FROM auth_user u " \
                " WHERE (u.username=%s or u.email=%s) " \
                " AND u.password=%s " \
                " AND u.status!=%s LIMIT 1"
        user = self.get_one(sql, 
                            self.escape_string(username), 
                            self.escape_string(username), 
                            self.escape_string(password),
                            const.User.STATUS_DESTROYED)
        if user:
            self.mod({'uid':user['id'], 'last_login':Common.get_current_time()})
        return user
    
    def login_with_perms(self, username, password):
        sql = "SELECT u.*, g.perms " \
                " FROM auth_user u " \
                " LEFT JOIN auth_group g ON g.id=u.group_id " \
                " WHERE (u.username=%s or u.email=%s) AND u.password=%s AND u.status!=%s "\
                " LIMIT 1"
        return self.get_one(sql, username, username, password, const.User.STATUS_DESTROYED)

    def password_valid(self, uid, password):
        sql = "SELECT * " \
                " FROM %s u "\
                " WHERE u.`id`=%s AND u.`password`='%s' LIMIT 1" \
                %(self._table, uid, password)
        return self.get_one(sql)
    
    def get_by_name(self, username):
        sql = "SELECT u.* FROM auth_user u WHERE u.username='%s' LIMIT 1" % (self.escape_string(username))
        return self.get_one(sql)

    def get_by_email(self, email, fields=None):
        if fields is None:
            sql = "SELECT * FROM auth_user WHERE email='%s' LIMIT 1" % (self.escape_string(email))
        else:
            fields_str = self._gen_fields_str(fields)
            sql = "SELECT %s FROM auth_user WHERE email='%s' LIMIT 1" % (fields_str, self.escape_string(email))
        return self.get_one(sql)
    
    def get_by_mobile(self, mobile, code='+86'):
        sql = "SELECT u.* FROM auth_user u WHERE u.mobile='%s' and mobile_code='%s' LIMIT 1" % (self.escape_string(mobile), code)
        return self.get_one(sql)

    def edit(self, kwarg):
        self.escape_dict(kwarg)
        pass

    def delete(self, uid):
        sql = "UPDATE %s SET status=%s WHERE id=%s" % (self._table, const.User.STATUS_DESTROYED, uid)
        ret = self.execute(sql)
        return ret[0]
    
    # 彻底删除
    def delete_by_id(self, uid):
        sql = "DELETE FROM %s WHERE id=%d" % (self._table, uid)
        return self.execute(sql)[0]

    def get_detail(self, uid):
        sql = "SELECT u.* FROM %s u WHERE u.id=%s LIMIT 1" % (self._table, uid)
        return self.get_one(sql)

    def get_pager_list(self, pager, group_id=0, key='', status=0):
        size = pager['ps']
        offset = size*(pager['p']-1)

        where_sql = ' WHERE 1=1 '
        if status==0:
            where_sql = where_sql + " AND u.`status` != %d " % const.User.STATUS_DESTROYED
        else:
            where_sql = where_sql + " AND u.`status` = %d " % status
        
        if group_id <> 0:
            where_sql = where_sql + " AND u.`group_id` = %d " % group_id
        
        if key is not None and key<>'':
            #where_sql = where_sql+" AND uuid like '%%%s%%' " % (key)
            where_sql = where_sql+" AND (username like '%%%%%s%%%%' or email like '%%%%%s%%%%' or mobile='%s')" % \
                        (self.escape_string(key), self.escape_string(key), self.escape_string(key))
        
        count_sql = "SELECT * FROM auth_user u " + where_sql
        count =  self._db.execute_rowcount(count_sql)
        if count<>0:
            se_sql = "SELECT u.*, g.`name` as group_name" \
                        " FROM %s u " \
                        " LEFT JOIN %s g ON g.id=u.group_id" \
                        " %s " \
                        " ORDER BY u.id DESC LIMIT %s, %s" % (self._table, self._table_group, where_sql, offset, size)
            rows = self.get_rows(se_sql)
            return dict(total=count, data=rows)
        else:
            return dict(total=0, data=[])
    
    def change_pwd_nike(self, uid, password, nike):
        sql = "UPDATE auth_user SET password=%s, nike=%s WHERE id=%s "
        return self.execute(sql, password, nike, uid)[0]

    def change_pwd(self, uid, password, nike):
        sql = "UPDATE auth_user SET password=%s, nike=%s WHERE id=%s "
        return self.execute(sql, password, nike, self._uid)[0]
    
    def mod(self, kwarg):
        return self._mod(kwarg)
    
    def _mod(self, args):
        user = {
            'username': {'type':'s'},
            'email': {'type':'s'},
            'mobile': {'type':'s'},
            'sex': {'type':'d'}, # 
            'status': {'type':'d'}, # 
            'creator': {'type':'d'},
            'first_name': {'type':'s'},
            'last_name': {'type':'s'},
            'password': {'type':'s'},
            'nike': {'type':'s'},
            'icon': {'type':'d'},
            'source': {'type':'d'},
            'last_login': {'type':'d'},
        }   

        if not args.has_key('uid'):
            return False

        ret = self._args_handle('update', args, user)               
        if not ret[0]:
            return False
        
        where = "id=%d" % args['uid']
        if len(user) > 0:
            ret = self._update(self._table, user, where)
            if not ret[0]:
                return False
        return True

    def filter(self, users):
        return users

    def set_token(self, token):
        sql = "REPLACE INTO auth_device_token(`token`,`device`,`up_time`,`uid`) VALUES" \
                "('%s','%s', %d, %d)" % (token.get('token',''), token.get('device',''),Common.get_current_time(), token.get('uid', 0))
        return self.update(sql)
    
    def set_online(self, uid, product='user', platform='Android'):
        sql = "SELECT uid, last_time, update_time FROM %s WHERE uid=%d and product='%s' and platform='%s' limit 1" % \
                (self._table_online, uid, product, platform)
        one  = self.get_one(sql)
        last_time = 0
        cur_time = Common.get_current_time()
        if one:
            last_time = one['last_time'] + cur_time - one['update_time']
        
        sql = "REPLACE INTO %s(`uid`, `product`,`platform`,`last_time`,`update_time`) VALUES(%d,'%s','%s',%d,%d)" % \
                (self._table_online, int(uid), product, platform, last_time, cur_time)
        return self.execute(sql)[0]
    
    def set_offline(self, uid, product='user', platform='all'):
        if platform=='all':
            sql = "DELETE FROM %s WHERE uid=%d and product='%s'" % \
                    (self._table_online, uid, product)
        else:
            sql = "DELETE FROM %s WHERE uid=%d and product='%s' and platform='%s'" % \
                    (self._table_online, uid, product, platform)
        return self.execute(sql)[0]
    
    def get_token(self, uid):
        sql = "SELECT `token`,`device`,`uid` FROM auth_device_token WHERE uid = %d order by up_time desc limit 1" %(uid)
        row = self.get_one(sql)
        return row
        
    def mod_friends(self, uid, fids):
        sql = "DELETE from %s where uid=%d " % (self._table_friends, int(uid))
        self.execute(sql)
        for id in fids:
            sql_insert = "INSERT INTO %s(`uid`,`fid`) VALUES(%d,%d)" % (self._table_friends, int(uid), int(id))
            self.execute(sql_insert)
        return True
        
    def search(self, key, limit=10):
        sql = "SELECT `id`,`username`,`email`, `icon`, `mobile_code`, `mobile`, `sex` " \
                " FROM %s " \
                " WHERE (username like '%%%%%s%%%%' or email='%s' or mobile='%s') and status=%d and group_id>1" \
                " limit %d" \
                %(self._table, key, key, key, const.User.STATUS_NORMAL, limit)
        row = self.get_rows(sql)
        return row
    
class FbuserModel(BaseModel):
    def __init__(self, uid = None):
        self._table = 'auth_fbuser'
        self._uid = uid
        
    def _add(self, fields):
        
        fbuser = {
            'fbid': {'type':'s', 'required':1},
            'tbid': {'type':'d', 'default':0},
            'fbusername': {'type':'s', 'required':1},
            'tbusername': {'type':'s', 'required':1},
            'sex': {'type':'d', 'required':1}, # 
            'email': {'type':'s', 'default':''},
            'access_token': {'type':'s', 'required':1},
            'link': {'type':'s', 'default':''},
            'add_time' : {'type':'d', 'default':Common.get_current_time()}
        }
        
        ret = self._args_handle('insert', fields, fbuser)   
        if not ret[0]:
            # todo:
            print ret[1]
            return ret
        return self._insert(self._table, fbuser)
    
    def add(self, kwarg):
        return self._add(kwarg)
    
    def detail(self, fbid):
        fields = "`fbid`,`tbid`,`fbusername`,`tbusername`,`sex`,`email`,`access_token`,`link`,`add_time`"
        where = "fbid='%s'" % str(fbid)
        sql = "select %s from %s where %s limit 1" % (fields, self._table, where)
        return self.get_one(sql)
    
    def mod(self, kwarg):
        return self._mod(kwarg)
    
    def _mod(self, args):
        fbuser = {
            'tbid': {'type':'d'},
            'fbusername': {'type':'s'},
            'tbusername': {'type':'s'},
            'sex': {'type':'d'}, # 
            'email': {'type':'s'},
            'access_token': {'type':'s'},
            'link': {'type':'s'},
        }   

        if not args.has_key('id'):
            return False

        ret = self._args_handle('update', args, fbuser)               
        if not ret[0]:
            return False
        
        where = "fbid='%s'" % args['fbid']
        if len(fbuser) > 0:
            ret = self._update(self._table, fbuser, where)
            if not ret[0]:
                return False
        
        return True


    # TODO 添加Format方法
    def filter(self, invitations):
        return invitations
