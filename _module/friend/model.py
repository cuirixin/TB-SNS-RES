#!/usr/bin/env python2.7
#-*- coding:utf8 -*-
#
# 2013-12-4 by Victor
# Copyright 2013 Tubban
from _module import const
from _module._base_m_ import BaseModel
from _module._lib.common import Common

class FriendModel(BaseModel):
    def __init__(self, uid = None):
        self._table_user = 'auth_user'
        self._uid = uid
        
    def _get_table_friend(self, uid):
        return self._get_mo_split_table(uid, "sn_friend", const.DB.FRIEND_SPLIT)
    
    def _get_table_apply_friend(self, uid):
        return self._get_mo_split_table(uid, "sn_friend_apply", const.DB.FRIEND_SPLIT)
    
    def get_list_by_user(self, uid):
        sql = "SELECT u.username, u.sex, u.id, u.mobile, u.mobile_code, u.icon, u.email, f.alias " \
                " FROM %s f " \
                " LEFT JOIN %s u on u.id=f.fid " \
                " WHERE f.uid=%d " % \
                (self._get_table_friend(uid), self._table_user, int(uid))
        return self.get_rows(sql)
    
    def is_friend(self, uid, fid):
        sql = "SELECT count(*) as total FROM %s " \
                " WHERE uid=%d and fid=%d " % \
                (self._get_table_friend(uid), int(uid), int(fid))
        cnt = self.get_one(sql)['total']
        if cnt:
            return True
        return False
    
    def add_apply(self, uid, fid, mid):
        sql = "REPLACE INTO %s(`uid`,`fid`,`status`,`add_time`,`mid`) VALUES(%d,%d,%d,%d,%d)" \
                % (self._get_table_apply_friend(int(uid)), int(uid), int(fid), const.ApplyFriend.STATUS_UNHANDLED, Common.get_current_time(), mid)
        self.execute(sql)
        return True
    
    def mod_apply(self, uid, fid, status):
        sql = "UPDATE %s set `status`=%d where `uid`=%d and `fid`=%d" \
                % (self._get_table_apply_friend(int(uid)), status, int(uid), int(fid))
        self.execute(sql)
        return True
    
    def get_apply_list(self, uid):
        table = self._get_table_apply_friend(uid)
        sql = "SELECT u.username, u.sex, u.id, u.mobile, u.mobile_code, u.icon, u.email, f.status as apply_status, f.mid " \
                " FROM %s f " \
                " LEFT JOIN %s u on u.id=f.fid " \
                " WHERE f.uid=%d order by f.add_time desc" % \
                (table, self._table_user, int(uid))
        return self.get_rows(sql)
    
    def add(self, uid, fid):
        sql1 = "REPLACE INTO %s(`uid`,`fid`) VALUES(%d,%d)" \
                % (self._get_table_friend(int(uid)), int(uid), int(fid))
        sql2 = "REPLACE INTO %s(`uid`,`fid`) VALUES(%d,%d)" \
                % (self._get_table_friend(int(fid)), int(fid), int(uid))
        self.execute(sql1)
        self.execute(sql2)
        return True
    
    
    def mod(self, kwarg):
        return self._mod(kwarg)
    
    def _mod(self, args):
        friend = {
            'alias': {'type':'s'}
        }   
        if not args.has_key('uid') or not args.has_key('fid'):
            return False

        ret = self._args_handle('update', args, friend)               
        if not ret[0]:
            return False
        
        where = "fid=%d and uid=%d" % (args['fid'], args['uid'])
        if len(friend) > 0:
            ret = self._update(self._get_table_friend(args['uid']), friend, where)
            if not ret[0]:
                return False
        
        return True
    
    def get_alias(self, uid, fid):
        sql = "SELECT `alias` from %s WHERE uid=%d and fid=%d " % \
                (self._get_table_friend(uid), int(uid), int(fid))
        return self.get_one(sql)
    
    def detail(self, uid, fid):
        sql = "SELECT u.username, u.sex, u.id, u.mobile, u.mobile_code, u.icon, u.email, f.alias " \
                " FROM %s f " \
                " LEFT JOIN %s u on u.id=f.fid " \
                " WHERE f.uid=%d and f.fid=%d " % \
                (self._get_table_friend(uid), self._table_user, int(uid), int(fid))
        return self.get_one(sql)
    
    def cancel_friend(self, uid, fid):
        sql1 = "DELETE FROM %s " \
                " WHERE uid=%d and fid=%d " % \
                (self._get_table_friend(uid), int(uid), int(fid))
        print self.execute(sql1)[0]
        sql2 = "DELETE FROM %s " \
                " WHERE uid=%d and fid=%d " % \
                (self._get_table_friend(fid), int(fid), int(uid))
        print self.execute(sql2)[0]
        return True

    ############################
    
    

