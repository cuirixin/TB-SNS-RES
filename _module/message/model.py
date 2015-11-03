#!/usr/bin/env python2.7
#-*- coding:utf8 -*-
#
# 2014-3-8 by Victor
# Copyright 2014 Tubban
from _module import const
from _module._base_m_ import BaseModel
from _module._lib.common import Common

class MessageModel(BaseModel):
    
    def __init__(self, uid = None):
        self._uid = uid
        self._message_table = 'sn_message'
        self._user_table = 'auth_user'
    
    def add(self, fields):
        return self._add(fields)

    def _add(self, fields):
        message = {
            'uid': {'type':'d', 'required':1},
            'sender': {'type':'d', 'required':1, 'default':0},
            'sender_name': {'type':'s', 'default':''},
            'b_id': {'type':'d', 'default':0},
            'b_uuid': {'type':'s', 'default':''},
            'type': {'type':'d', 'required':1},
            'status': {'type':'d', 'default':const.Message.STATUS_UNHANDLED},
            'read': {'type':'d', 'default':0},
            'invitation_id': {'type':'d', 'default':0},
            'pushed': {'type':'s', 'default':0},
            'content': {'type':'s', 'default':''},
            'extra': {'type':'s', 'default':'{}'},
            'add_time': {'type':'d', 'default':Common.get_current_time()},
        }
        
        ret = self._args_handle('insert', fields, message)               
        if not ret[0]:
            return ret
        table = self._get_mo_split_table(fields['uid'], self._message_table, const.DB.MESSAGE_SPLIT)
        return self._insert(table, message)
    
    def change_status(self, uid, id, status):
        table = self._get_mo_split_table(self._uid, self._message_table, const.DB.MESSAGE_SPLIT)
        sql = "UPDATE %s set status=%d WHERE id=%s " % (table, status, id)
        ret = self.execute(sql)
        if not ret[0]:
            return False
        return True
    
    """
    def delete(self, id):
        if self._uid is None:
            return False
        table = self._get_mo_split_table(self._uid, self._message_table, const.DB.MESSAGE_SPLIT)
        sql = "DELETE FROM %s WHERE id=%s " % (table, id)
        ret = self.execute(sql)
        if not ret[0]:
            return False
        return True
    """

    def get_unread_nums(self, uid):
        table = self._get_mo_split_table(uid, self._message_table, const.DB.MESSAGE_SPLIT)
        sql = "SELECT `type`, count(id) as cnt FROM %s WHERE `read`=0 group by `type`" % (table)
        return self.get_rows(sql)
        
    def get_pager_list_by_types(self, pager, uid, types, read=-1):
        table = self._get_mo_split_table(uid, self._message_table, const.DB.MESSAGE_SPLIT)
    
        size = pager['ps']
        offset = size*(pager['p']-1)
        where_sql = ' WHERE a.status>%d AND a.uid=%d' % (const.Message.STATUS_DELETE, uid)
        
        if types[0] == '0':
            pass
        elif len(types) == 1:
            where_sql = where_sql + ' AND a.`type`=%d ' % int(types[0])
        else:
            where_sql = where_sql + ' AND a.`type` in (%s) ' % ','.join(types)
            
        if read <> -1:
            where_sql = where_sql + ' AND a.`read`=%d ' % int(read)
            
        count_sql = "SELECT count(*) as total FROM %s a " % table + where_sql
        count =  self.get_one(count_sql)['total']
        if count<>0:
            se_sql = "SELECT a.*,b.icon as sender_icon, b.sex as sender_sex " \
                        " FROM %s a" \
                        " LEFT JOIN %s b ON b.id=a.sender" \
                        " %s " \
                        " order by a.add_time desc "  \
                        " limit %s,%s "\
            % (table, self._user_table, where_sql, offset, size)
            rows = self.get_rows(se_sql)
            
            # 返回后，执行update
            for one in rows:
                update_sql = "UPDATE %s SET `read`=1 where id=%d " \
                            % (table, one['id'])
                self.execute(update_sql)
            return dict(total=count, data=rows)
        else:
            return dict(total=0, data=[])
        
    def get_by_id(self, uid, id):
        table = self._get_mo_split_table(uid, self._message_table, const.DB.MESSAGE_SPLIT)
        sql = "select * from %s where id=%d" % (table, id)
        return self.get_one(sql)

    """
    Func: 删除sender发送而来的某一类型的消息
    """
    def delete_by_user_and_type(self, uid, sender, type):
        table = self._get_mo_split_table(uid, self._message_table, const.DB.MESSAGE_SPLIT)
        sql = "update %s set status=%d where uid=%d and sender=%d and `type`=%d" % (table, const.Message.STATUS_DELETE, uid, sender, type)
        return self.execute(sql)[0]

    """
    Func: 删除某一邀请消息
    """
    def delete_by_user_and_type_and_invitation(self, uid, type, invitation_id):
        table = self._get_mo_split_table(uid, self._message_table, const.DB.MESSAGE_SPLIT)
        sql = "update %s set status=%d where `uid`=%d and `type`=%d and `invitation_id`=%d" % (table, const.Message.STATUS_DELETE, uid, type, invitation_id)
        return self.execute(sql)[0]
    

class MessageQueueModel(BaseModel):
    
    def __init__(self, uid = None):
        self._uid = uid
        self._message_queue_talbe = 'message_queue'
        # self._message_table = 'message'
    
    def add_queue(self, fields):
        queue = {
            'uid': {'type':'d', 'required':1},
            'language': {'type':'s', 'required':1},
            'target': {'type':'s', 'required':1},
            'target_type': {'type':'d', 'required':1},
            'info': {'type':'s', 'required':1},
            'status': {'type':'d', 'default':const.MessageQueue.STATUS_UNSEND},
            'add_time': {'type':'d', 'default':Common.get_current_time()},
        }
        
        ret = self._args_handle('insert', fields, queue)               
        if not ret[0]:
            # todo:
            return ret
        return self._insert(self._message_queue_talbe, queue)
    
    def get_unsend_queue_list(self, target_type=const.MessageQueue.TARGET_TYPE_EMAIL):
        sql = ("select * from %s WHERE target_type=%d AND status=%d") % \
                (self._message_queue_talbe, target_type, const.MessageQueue.STATUS_UNSEND)
        return self.get_rows(sql)
        
    def update_queue(self, args):
        if not args.has_key('id'):
            return False
        allow_fields = {
            'status': {'type':'d', 'set':[0,1,2]},
            'uid': {'type':'d'},
            'send_time': {'type':'d'},
        }

        ret = self._args_handle('update', args, allow_fields)               
        if not ret[0]:
            return ret
        
        where = "id=%d" % args['id']
        if len(allow_fields) > 0:
            ret = self._update(self._message_queue_talbe, allow_fields, where)
            if not ret[0]:
                return False
        # _mod success
        return True
    
    def update_queue_status_by_uid(self, uid, status):
        sql = "UPDATE %s SET status=%d WHERE uid=%d" % (self._message_queue_talbe, status, uid)
        ret = self.update(sql)
        if not ret[0]:
            return False
        return True
