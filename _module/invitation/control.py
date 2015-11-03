#!/usr/bin/env python2.7
#-*- coding:utf8 -*-
#
# 2013-12-4 by Victor
# Copyright 2013 Tubban
from _module import const
from _module._lib.common import Common
from _module._lib.lang import Lang
from _module.friend.model import FriendModel
from _module.invitation.model import InvitationModel
from _module.message.service import MessageService
from _module.user.model import UserModel

class InvitationControl:
    def __init__(self, uid = None,userLang=None):
        self._uid = uid
        self._inviteModel = InvitationModel(self._uid)
        self._userModel = UserModel(self._uid)
        self._friendModel = FriendModel(self._uid)
        self._field = Lang.get_db_field_name(userLang)
    # 添加新邀请
    def add(self, invitation, targets):
        ret = self._inviteModel.add(invitation)
        if not ret[0]:
            return ret
        invite_id = ret[1]
        
        # 添加用户
        relation = {
            "uid" : invitation['creator'],
            "invitation_id" : invite_id,
            "is_creator" : 1,
            "status" : const.InvitationUser.STATUS_ACCEPT
        }
        self._inviteModel.add_member(invitation['creator'], invite_id, relation)

        for target in targets:
            relation = {
                "uid" : target['uid'],
                "invitation_id" : invite_id,
                "is_creator" : 0,
                "status" : const.InvitationUser.STATUS_UNHANDLED
            }
            self._inviteModel.add_member(target['uid'], invite_id, relation)
        
            # 添加消息
            message = {
                "sender" : invitation['creator'], 
                "sender_name" : self._userModel.get_by_id(invitation['creator'])['username'], 
                "uid" : int(target['uid']), 
                "type" : const.Message.TYPE_RESTAURANT_INVITATION,
                "content" : invitation['note'],
                "b_id" : invitation['b_id'],
                "b_uuid" : invitation['b_uuid'],
                "invitation_id" : invite_id
            }
            ret_m = MessageService().add_restaurant_invitation_request(message)
            if not ret_m[0]:
                continue
            mid = ret_m[1]
        
        return ret
    
    def mod(self, invitation):
        ret = self._inviteModel.mod(invitation)
        if not ret:
            return False
        return True
        """
        old = self._inviteModel.get_by_id(invitation['id'])
        print old
        # TODO send message
        """
        
    def cancel(self, id):
        invitation = {'id':id, 'status':const.Invitation.STATUS_CANCELED}
        self.mod(invitation)
        invitation = self.get_by_id(id)
        targets = self._inviteModel.get_members(invitation['id'])
        for one in targets:
            if one['id'] == invitation['creator']:
                continue
            MessageService().del_restaurant_invitation_request(one['id'], invitation['id'])
            # 添加消息
            message = {
                "sender" : invitation['creator'], 
                "sender_name" : self._userModel.get_by_id(invitation['creator'])['username'], 
                "uid" : one['id'], 
                "type" : const.Message.TYPE_RESTAURANT_INVITATION_NOTIFICATION,
                "content" : const.NotificationMessage.INVITATION_CANCELD,
                "b_id" : invitation['b_id'],
                "b_uuid" : invitation['b_uuid'],
                "invitation_id" : invitation['id']
            }
            MessageService().add(message)
        
        return True
        
    def delete(self, id):
        invitation = {'id':id, 'status':const.Invitation.STATUS_DELETE}
        self.mod(invitation)
        invitation = self.get_by_id(id)
        targets = self._inviteModel.get_members(invitation['id'])
        for one in targets:
            if one['id'] == invitation['creator']:
                continue
            MessageService().del_restaurant_invitation_request(one['id'], invitation['id'])
            # 添加消息
            message = {
                "sender" : invitation['creator'], 
                "sender_name" : self._userModel.get_by_id(invitation['creator'])['username'], 
                "uid" : one['id'], 
                "type" : const.Message.TYPE_RESTAURANT_INVITATION_NOTIFICATION,
                "content" : const.NotificationMessage.INVITATION_DELETED,
                "b_id" : invitation['b_id'],
                "b_uuid" : invitation['b_uuid'],
                "invitation_id" : invitation['id']
            }
            MessageService().add(message)
        
        return True
        
    def quit(self, uid, id):
        invitation = self.get_by_id(id)
        if not invitation:
            return False
        # 删除关联
        self._inviteModel.mod_relation(uid, invitation['id'], const.InvitationUser.STATUS_REJECT)
        # 添加消息
        message = {
            "sender" : uid, 
            "sender_name" : self._userModel.get_by_id(uid)['username'], 
            "uid" : invitation['creator'], 
            "type" : const.Message.TYPE_RESTAURANT_INVITATION_RESPONSE,
            "content" : const.NotificationMessage.INVITATION_QUIT,
            "b_id" : invitation['b_id'],
            "b_uuid" : invitation['b_uuid'],
            "invitation_id" : invitation['id']
        }
        MessageService().add(message)
        return True
    
    def _get_friend_result(self, uid, fid):
        result = [0, '']
        if uid:
            if uid == fid:
                result[0] = 1
            else:
                ret = self._friendModel.get_alias(uid, fid)
                if ret:
                    result[0] = 1
                    result[1] = ret['alias']
        return result
    # 详情
    """
    {
        "id": 6, 
        "b_uuid": "ciDf", 
        "r_name": "Katy's Lodge", 
        "creator": {
            "username": "test", 
            "alias": "", 
            "id": 38, 
            "is_friend": 1, 
            "icon": 0
        }, 
        "date_time": 18300000, 
        "type_sex": 2, 
        "type_eat": 4
        "type_pay": 1, 
        "type_num": 1, 
        "note": "", 
        "add_time": 1414631232, 
        "targets": [
            {
                "username": "portmann", 
                "stat": 0, 
                "uid": 9, 
                "is_friend": 1, 
                "alias": "tttt", 
                "icon": 0
            }
        ]
    }
    
    """
    def detail(self, id):
        invitation = self._inviteModel.detail(id)
        # TODO 可见验证
        if not invitation:
            return None
        return self._format_detail(self._uid, invitation)
        
    def get_by_id(self, id):
        return self._inviteModel.get_by_id(id)
        
    """
    filter:
           0 - All
           1 - Request
           2 - Upcoming
           3 - History
           4 - My create
    """
    def get_pager_list(self, uid, pager, filter=0):
        
        if filter == 1:
            ret = self._inviteModel.get_request_pager_list(uid, pager)
            list = ret['data']
            for one in list:
                one = self._format_detail(uid, one)
            ret['data'] = list
        elif filter == 4:
            ret = self._inviteModel.get_my_pager_list(uid, pager)
            list = ret['data']
            for one in list:
                one = self._format_detail(uid, one)
            ret['data'] = list
        elif filter == 5:
            ret = self._inviteModel.get_my_pager_list(uid, pager, const.Invitation.STATUS_CANCELED)
            list = ret['data']
            for one in list:
                one = self._format_detail(uid, one)
            ret['data'] = list
        else:
            ret = self._inviteModel.get_pager_list(uid, pager, filter)
            list = ret['data']
            for one in list:
                one = self._format_detail(uid, one)
            ret['data'] = list
        
        return ret
            
    def _format_detail(self, uid, invitation):
        
        _creator = self._userModel.get_by_id(invitation['creator'])
        friend_ret = self._get_friend_result(uid, invitation['creator'])
        invitation['creator'] = {
            "id":_creator['id'], 
            "username":_creator['username'], 
            "icon":_creator['icon'],
            "sex":_creator['sex'],
            "is_friend":friend_ret[0],
            "alias":friend_ret[1]
        }
        
        members = self._inviteModel.get_members(invitation['id'])
        for one in members:
            friend_ret = self._get_friend_result(uid, one['id'])
            one["is_friend"] =friend_ret[0]
            one["alias"] = friend_ret[1]
        invitation['targets'] = members
        return self._format(invitation)
        
    def _format(self, invitation):
        if not invitation:
            return None
        else:
            if invitation.has_key('date_time'):
                invitation['date_time'] = Common.seconds_to_str(invitation['date_time'], const.Date_Format.DATETIME2)
            return invitation
                