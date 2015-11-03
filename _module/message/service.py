#!/usr/bin/env python2.7
#-*- coding:utf8 -*-
#
# 2014-3-25 by Victor
# Copyright 2013 Tubban
from _module import const
from _module._base_c_ import BaseControl
from _module.friend.model import FriendModel
from _module.invitation.model import InvitationModel
from _module.message.model import MessageModel
from _module.user.model import UserModel

class MessageService(BaseControl):
    def __init__(self, uid = None, userLang=None):
        self._uid = uid
        self._messageM = MessageModel(uid)
        self._friendM = FriendModel(uid)
        self._invitationM = InvitationModel(uid)
        self._userM = UserModel(uid)

    """
    message = {
            "sender":_from, 
            "sender_name":u_from['username'], 
            "uid":u_to, 
            "type":const.Message.TYPE_APPLY_FOR_FRIEND,
            "content" : message
        }
    """
    def add_apply_friend_request(self, message):
        # TODO 如果需要的话初始化一些额外的字段
        return self._messageM.add(message)
    
    """
    message = {
                "sender":invitation['creator'], 
                "sender_name": self._userModel.get_by_id(invitation['creator'])['username'], 
                "uid":target['id'], 
                "type":const.Message.TYPE_APPLY_FOR_FRIEND,
                "content" : invitation['note']
            }
    """
    def add_restaurant_invitation_request(self, message):
        # TODO 如果需要的话初始化一些额外的字段
        return self._messageM.add(message)
    
    """
    Func: 删除餐厅邀请
    """
    def del_restaurant_invitation_request(self, uid, invitation_id):
        return self._messageM.delete_by_user_and_type_and_invitation(uid, const.Message.TYPE_RESTAURANT_INVITATION, invitation_id)
    
    """
    Func: 获取某用户各类型的未读的消息数目
    """
    def get_unread_nums(self, uid):
        rows = self._messageM.get_unread_nums(uid)
        types = {
            const.Message.TYPE_APPLY_FOR_FRIEND : 0,
            const.Message.TYPE_APPLY_FOR_FRIEND_RESPONSE : 0,
            const.Message.TYPE_RESTAURANT_INVITATION : 0,
            const.Message.TYPE_RESTAURANT_INVITATION_RESPONSE:0
        }
        for one in rows:
            types[one['type']] = one['cnt']
        return types
        
    """
    Func: 根据用户和消息类型，返回分页列表
    """
    def get_pager_list_by_types(self, pager, uid, types, read=-1):
        ret = self._messageM.get_pager_list_by_types(pager, uid, types, read)
        _list = []
        for one in ret['data']:
            _one = self._filter_fields(one, ["id", "type", "status", "b_uuid", "pushed", "read", "sender", "sender_name", "sender_icon","sender_sex", "content", "add_time", "extra","invitation_id"])
            _list.append(_one)
        ret['data'] = _list
        return ret
        
    def delete(self, uid, id):
        return self._messageM.change_status(uid, id, const.Message.STATUS_DELETE)
    
    def add(self, message):
        return self._messageM.add(message)
    
    """
    Func: 处理消息
    """
    def handle(self, uid, id, handle_type):
        # 删除信息
        if handle_type == const.Message.HANDLE_TYPE_DELETE:
            return self.delete(uid, id)
        
        message = self._messageM.get_by_id(uid, id)
        if message is None or message['status']<>const.Message.STATUS_UNHANDLED:
            return True
        
        # 好友相关
        if message['type'] == const.Message.TYPE_APPLY_FOR_FRIEND:
            return self._handle_friend_apply(uid, message, handle_type)
        # 邀请
        if message['type'] == const.Message.TYPE_RESTAURANT_INVITATION:
            return self._handle_restaurant_invitation(uid, message, handle_type)
        
        return False

    def _handle_friend_apply(self, uid, message, handle_type):
        # 同意加好友
        if handle_type == const.Message.HANDLE_TYPE_ACCEPT:
            
            self._friendM.add(uid, message['sender'])
            self._messageM.change_status(uid, message['id'], const.Message.STATUS_ACCEPT)
            self._friendM.mod_apply(message['sender'], uid, const.ApplyFriend.STATUS_ACCEPT)
            message = {
                'uid': message['sender'],
                'sender': uid,
                'sender_name': self._userM.get_by_id(uid)['username'],
                'status':const.Message.STATUS_ACCEPT,
                'b_id': 0,
                'type': const.Message.TYPE_APPLY_FOR_FRIEND_RESPONSE,
                'content': 'Accept your request',
                'extra': '{}'
            }
            self._messageM.add(message)
            return True
        
        if handle_type == const.Message.HANDLE_TYPE_REJECT:
            self._messageM.change_status(uid, message['id'], const.Message.HANDLE_TYPE_REJECT)
            self._friendM.mod_apply(message['sender'], uid, const.ApplyFriend.STATUS_REJECT)
            message = {
                'uid': message['sender'],
                'sender': uid,
                'sender_name': self._userM.get_by_id(uid)['username'],
                'b_id': 0,
                'type': const.Message.TYPE_APPLY_FOR_FRIEND_RESPONSE,
                'status':const.Message.STATUS_REJECT,
                'content': 'Reject your request',
                'extra': '{}'
            }
            self._messageM.add(message)
            return True
        
        if handle_type == const.Message.HANDLE_TYPE_IGNORE:
            self._messageM.change_status(uid, message['id'], const.Message.HANDLE_TYPE_IGNORE)
            self._friendM.mod_apply(message['sender'], uid, const.ApplyFriend.STATUS_IGNORE)
            return True
        
        if handle_type == const.Message.HANDLE_TYPE_DELETE:
            self._messageM.change_status(uid, message['id'], const.Message.HANDLE_TYPE_DELETE)
            return True
        
    def _handle_restaurant_invitation(self, uid, message, handle_type):
        
        invitation = self._invitationM.get_by_id(message['invitation_id'])
        if not invitation:
            return False
        
        if handle_type == const.Message.HANDLE_TYPE_ACCEPT:
            # 修改消状态为接受
            self._messageM.change_status(uid, message['id'], const.Message.STATUS_ACCEPT)
            self._invitationM.mod_relation(uid, invitation['id'], const.InvitationUser.STATUS_ACCEPT)
            
            message = {
                'uid': message['sender'],
                'sender': uid,
                'sender_name': self._userM.get_by_id(uid)['username'],
                'status':const.Message.STATUS_ACCEPT,
                'b_id': invitation['b_id'],
                'b_uuid': invitation['b_uuid'],
                'invitation_id':invitation['id'],
                'type': const.Message.TYPE_RESTAURANT_INVITATION_NOTIFICATION,
                'content': const.NotificationMessage.INVITATION_ACCEPTED,
                'extra': '{}'
            }
            self._messageM.add(message)
            return True
        
        if handle_type == const.Message.HANDLE_TYPE_REJECT:
            # 修改消状态为接受
            self._messageM.change_status(uid, message['id'], const.Message.STATUS_REJECT)
            self._invitationM.mod_relation(uid, invitation['id'], const.InvitationUser.STATUS_REJECT)
            
            message = {
                'uid': message['sender'],
                'sender': uid,
                'sender_name': self._userM.get_by_id(uid)['username'],
                'invitation_id':invitation['id'],
                'status':const.Message.STATUS_REJECT,
                'b_id': invitation['b_id'],
                'b_uuid': invitation['b_uuid'],
                'type': const.Message.TYPE_RESTAURANT_INVITATION_NOTIFICATION,
                'content': 'Accept your invitation request',
                'extra': '{}'
            }
            self._messageM.add(message)
            return True
        
        if handle_type == const.Message.HANDLE_TYPE_IGNORE:
            # 修改消状态为接受
            self._messageM.change_status(uid, message['id'], const.Message.STATUS_IGNORE)
            self._invitationM.mod_relation(uid, invitation['id'], const.InvitationUser.STATUS_IGNORE)
            
            return True
        
        if handle_type == const.Message.HANDLE_TYPE_DELETE:
            self._messageM.change_status(uid, message['id'], const.Message.STATUS_DELETE)
            return True
            
        