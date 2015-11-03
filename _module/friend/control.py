#!/usr/bin/env python2.7
#-*- coding:utf8 -*-
#
# 2013-12-4 by Victor
# Copyright 2013 Tubban
from _module import const
from _module._base_c_ import BaseControl
from _module.friend.model import FriendModel
from _module.message.model import MessageModel
from _module.message.service import MessageService
from _module.user.model import UserModel

class FriendControl(BaseControl):
    def __init__(self, uid = None,userLang=None):
        self._uid = uid
        self._uModel = UserModel(self._uid)
        self._fModel = FriendModel(self._uid)
        self._mModel = MessageModel(self._uid)
    
    # 申请加好友
    def apply(self, _from, _tos, msg):
        # TODO or DELETE
        u_from = self._uModel.get_by_id(_from)
        for _to in _tos:
            if self._fModel.is_friend(_from, _to):
                continue
            # 删除原请求消息
            self._mModel.delete_by_user_and_type(int(_to), int(_from), const.Message.TYPE_APPLY_FOR_FRIEND)
            message = {
                "sender":int(_from), 
                "sender_name":u_from['username'], 
                "uid":int(_to), 
                "type":const.Message.TYPE_APPLY_FOR_FRIEND,
                "content" : msg
            }
            # 发送新消息
            ret = MessageService().add_apply_friend_request(message)
            if not ret[0]:
                return False
            mid = ret[1]
            # 添加申请记录表
            self._fModel.add_apply(_from, _to, mid)
        return True

    def get_list(self, uid):
        friends = self._fModel.get_list_by_user(uid)
        return friends
    
    def get_apply_list(self, uid):
        ret = self._fModel.get_apply_list(uid)
        """
        _list = []
        for one in ret['data']:
            _list.append(_one)
        ret['data'] = _list
        """
        return ret
    
    def mod(self, friend):
        return self._fModel.mod(friend)

    def is_friend(self, uid, fid):
        return self._fModel.is_friend(uid, fid)
    
    def detail(self, uid, fid):
        friend = self._fModel.detail(uid, fid)
        #friend = self._filter_fields(user, ['id', ''])
        return friend
    
    def cancel_friend(self, uid, fid):
        return self._fModel.cancel_friend(uid, fid)
        