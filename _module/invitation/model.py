#!/usr/bin/env python2.7
#-*- coding:utf8 -*-
#
# 2013-12-4 by Victor
# Copyright 2013 Tubban
from _module import const
from _module._base_m_ import BaseModel
from _module._lib.common import Common

class InvitationModel(BaseModel):
    def __init__(self, uid = None):
        self._table = 'sn_r_invitation'
        self._invitation_user_table = "sn_r_invitation_user"
        self._invitation_user_user_table = "sn_r_invitation_user_user"
        self._message_table = 'sn_message'
        self._user_table = 'auth_user'
        self._uid = uid
        
    def _add(self, fields):
        
        invitation = {
            'b_id': {'type':'d', 'required':1},
            'b_uuid': {'type':'s', 'required':1},
            'r_name': {'type':'s', 'required':1},
            'creator': {'type':'d', 'required':1},
            'date_time': {'type':'d', 'required':1}, # 时间戳  
            'type_eat': {'type':'d', 'required':1},
            'type_num': {'type':'d', 'required':1},
            'type_sex': {'type':'d', 'required':1},
            'type_pay': {'type':'d', 'required':1},
            'type_visible': {'type':'d', 'default':const.Invitation.TYPE_VISIBLE_ANYONE},
            'status': {'type':'d', 'default':const.Invitation.STATUS_VALID},
            'note': {'type':'s', 'default':''},
            'p_num' : {'type':'d', 'default':0},
            'p_c_num' : {'type':'d', 'default':0},
            'add_time' : {'type':'d', 'default':Common.get_current_time()}
        }
        
        ret = self._args_handle('insert', fields, invitation)   
        if not ret[0]:
            # todo:
            print ret[1]
            return ret
        return self._insert(self._table, invitation)
    
    def add(self, kwarg):
        return self._add(kwarg)
    
    def get_by_id(self, id):
        sql = "SELECT * FROM %s WHERE id=%d" % (self._table, int(id))
        return self.get_one(sql)
    
    def _add_target(self, invitation_id, fields):
        table = self._get_mo_split_table(invitation_id, self._invitation_user_table, const.DB.INVITATION_USER_SPLIT)
        target = {
            'invitation_id': {'type':'d', 'required':1},
            'uid': {'type':'d', 'required':1},
            'is_creator': {'type':'d', 'required':1},
            'status' : {'type':'d', 'required':1}
        }
        
        ret = self._args_handle('insert', fields, target)   
        if not ret[0]:
            return ret
        return self._insert(table, target)
    
    def add_member(self, uid, invitation_id, fields):
        # 添加邀请Target数据，按邀请分表
        ret = self._add_target(invitation_id, fields)
        if not ret[0]:
            return ret
        # 添加用户邀请关联数据，按用户
        table = self._get_mo_split_table(uid, self._invitation_user_user_table, const.DB.INVITATION_USER_USER_SPLIT)
        relation = {
            'uid': {'type':'d', 'required':1},
            'invitation_id': {'type':'d', 'required':1},
            'is_creator': {'type':'d', 'required':1},
            'status' : {'type':'d', 'required':1}
        }
        
        ret = self._args_handle('insert', fields, relation)   
        if not ret[0]:
            return ret
        return self._insert(table, relation)
    
    def get_members(self, invitation_id):
        table = self._get_mo_split_table(invitation_id, self._invitation_user_table, const.DB.INVITATION_USER_SPLIT)
        sql = "SELECT a.uid as id, a.status, a.is_creator, b.sex, b.icon, b.username " \
                " FROM %s a "\
                " LEFT JOIN %s b ON a.uid=b.id "\
                " WHERE a.invitation_id=%d" % (table, self._user_table, invitation_id)
        return self.get_rows(sql)
    
    def _update_target_num(self, invitation_id):
        table = self._get_mo_split_table(invitation_id, self._invitation_user_table, const.DB.INVITATION_USER_SPLIT)
        sql = "SELECT count(*) as total from %s WHERE invitation_id=%d " % (table, invitation_id)
        p_num = self.get_one(sql)['total']
        sql = "SELECT count(*) as total from %s WHERE invitation_id=%d AND status=%d " % (table, invitation_id, const.InvitationUser.STATUS_ACCEPT)
        p_c_num = self.get_one(sql)['total']
        #print {"id":invitation_id, "p_num":p_num, "p_c_num":p_c_num}
        return self.mod({"id":invitation_id, "p_num":p_num, "p_c_num":p_c_num})
    
    def mod_relation(self, uid, invitation_id, status):
        table_1 = self._get_mo_split_table(invitation_id, self._invitation_user_table, const.DB.INVITATION_USER_SPLIT)
        table_2 = self._get_mo_split_table(uid, self._invitation_user_user_table, const.DB.INVITATION_USER_USER_SPLIT)
        sql_1 = "UPDATE %s SET status=%d WHERE uid=%d and invitation_id=%d " % (table_1, status, uid, invitation_id)
        sql_2 = "UPDATE %s SET status=%d WHERE uid=%d and invitation_id=%d " % (table_2, status, uid, invitation_id)
        print self.execute(sql_1)
        print self.execute(sql_2)
        self._update_target_num(invitation_id)
        return True
        
    def del_relation(self, uid, invitation_id):
        table = self._get_mo_split_table(uid, self._invitation_user_table, const.DB.INVITATION_USER_SPLIT)
        sql = "DELETE FROM %s WHERE uid=%d and invitation_id=%d" % (table, uid, invitation_id)
        return self.execute(sql)[0]
    
    def detail(self, id):
        fields = "`id`,`b_uuid`,`r_name`,`creator`,`status`,`date_time`,`type_eat`,`type_num`,`type_sex`,`type_pay`,`note`,`add_time`,`p_num`,`p_c_num`"
        where = "id=%d" % int(id)
        sql = "select %s from %s where %s" % (fields, self._table, where)
        return self.get_one(sql)
    
    """
    Func: 获取关联的邀请列表
    """
    def get_pager_list(self, uid, pager, filter):
        i_u_table = self._get_mo_split_table(uid, self._invitation_user_user_table, const.DB.INVITATION_USER_USER_SPLIT)
    
        size = pager['ps']
        offset = size*(pager['p']-1)
        where_sql = ' WHERE b.status=%d AND a.uid=%d ' % (const.Invitation.STATUS_VALID, uid)
        order_sql = " b.date_time desc"
        # 全部
        if filter == 0:
            pass
        # upcoming
        elif filter == 2:
            where_sql = where_sql + ' AND b.`date_time`>%d AND a.status=%d' % (Common.get_current_time(), const.InvitationUser.STATUS_ACCEPT)
            order_sql = " b.date_time asc"
        elif filter == 3:
            where_sql = where_sql + ' AND b.`date_time`<%d AND a.status=%d ' % (Common.get_current_time(), const.InvitationUser.STATUS_ACCEPT)

        count_sql = "SELECT count(*) as total " \
                        " FROM %s a " \
                        " LEFT JOIN %s b on b.id=a.invitation_id " \
                        " %s " % (i_u_table, self._table, where_sql)
        count =  self.get_one(count_sql)['total']
        if count<>0:
            se_sql = "SELECT b.`id`,b.`b_uuid`,b.`r_name`,b.`creator`,b.`date_time`,b.`type_eat`,b.`type_num`,b.`type_sex`,b.`type_pay`,b.`note`,b.`add_time` " \
                        " FROM %s a" \
                        " LEFT JOIN %s b on b.id=a.invitation_id " \
                        " %s " \
                        " order by %s "  \
                        " limit %s,%s "\
            % (i_u_table, self._table, where_sql, order_sql, offset, size)
            rows = self.get_rows(se_sql)
            
            return dict(total=count, data=rows)
        else:
            return dict(total=0, data=[])
        
        
    def get_request_pager_list(self, uid, pager):
        
        m_table = self._get_mo_split_table(uid, self._message_table, const.DB.MESSAGE_SPLIT)
        size = pager['ps']
        offset = size*(pager['p']-1)
        where_sql = ' WHERE a.uid=%d and a.status=%d AND a.type=%d ' % (uid, const.Message.STATUS_UNHANDLED, const.Message.TYPE_RESTAURANT_INVITATION)
        order_sql = " b.date_time asc"
            
        count_sql = "SELECT count(*) as total " \
                        " FROM %s a " \
                        " %s " % (m_table, where_sql)
        count =  self.get_one(count_sql)['total']
        if count<>0:
            se_sql = "SELECT b.`id`,b.`b_uuid`,b.`r_name`,b.`creator`,b.`date_time`,b.`type_eat`,b.`type_num`,b.`type_sex`,b.`type_pay`,b.`note`,b.`add_time`,a.`id` as message_id " \
                        " FROM %s a" \
                        " LEFT JOIN %s b on b.id=a.invitation_id " \
                        " %s " \
                        " order by %s "  \
                        " limit %s,%s "\
            % (m_table, self._table, where_sql, order_sql, offset, size)
            rows = self.get_rows(se_sql)
            
            return dict(total=count, data=rows)
        else:
            return dict(total=0, data=[])
        
    """
    Func: 获取用户创建的
    """
    def get_my_pager_list(self, uid, pager, status=None):
        size = pager['ps']
        offset = size*(pager['p']-1)
        if status is None:
            where_sql = "WHERE b.creator=%d and b.status>%d " % (uid, const.Invitation.STATUS_DELETE)
        else:
            where_sql = "WHERE b.creator=%d and b.status=%d " % (uid, status)
        count_sql = "SELECT count(*) as total " \
                        " FROM %s b " \
                        " %s " % (self._table, where_sql)
        count =  self.get_one(count_sql)['total']
        if count<>0:
            se_sql = "SELECT b.`id`,b.`b_uuid`,b.`r_name`,b.`creator`,b.`date_time`,b.`type_eat`,b.`type_num`,b.`type_sex`,b.`type_pay`,b.`note`,b.`add_time` " \
                        " FROM %s b" \
                        " %s " \
                        " order by b.date_time desc " \
                        " limit %s,%s " \
            % (self._table, where_sql, offset, size)
            rows = self.get_rows(se_sql)
            return dict(total=count, data=rows)
        else:
            return dict(total=0, data=[])

    def mod(self, kwarg):
        return self._mod(kwarg)
    
    def _mod(self, args):
        invitation = {
            'b_id': {'type':'d'},
            'r_name': {'type':'s'},
            'b_uuid': {'type':'s'},
            'date_time': {'type':'d'}, # 时间戳  
            'type_eat': {'type':'d'},
            'type_num': {'type':'d'},
            'type_sex': {'type':'d'},
            'type_pay': {'type':'d'},
            'type_visible': {'type':'d'},
            'status': {'type':'d'},
            'note': {'type':'s'},
            'p_num' : {'type':'d'},
            'p_c_num' : {'type':'d'},
        }   

        if not args.has_key('id'):
            return False

        ret = self._args_handle('update', args, invitation)               
        if not ret[0]:
            return False
        
        where = "id=%d" % args['id']
        if len(invitation) > 0:
            ret = self._update(self._table, invitation, where)
            if not ret[0]:
                return False
        
        return True


    # TODO 添加Format方法
    def filter(self, invitations):
        return invitations
