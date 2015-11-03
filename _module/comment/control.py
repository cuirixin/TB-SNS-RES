#!/usr/bin/env python2.7
#-*- coding:utf8 -*-
################################################################################
#
# Copyright (c) 2015 Tubban.com, Inc. All Rights Reserved
#
################################################################################

from _module._lib.lang import Lang
from _module.business.model import BusinessModel
from _module.comment.model import BCommentModel

class BCommentControl:
    def __init__(self, uid = None, userLang=None):
        
        self._uid = uid
        self._cModel = BCommentModel(self._uid)
        self._userLang = userLang
        self._field = Lang.get_db_field_name(userLang)
        self._bModel = BusinessModel(self._uid)

    def add(self, comment):
        ret =  self._cModel.add(comment)
        if ret[0]:
            self._cModel.update_comment_num(comment['business_id'])
        return ret

    def get_pager_list(self, business_id, pager, lang_code=None):
        return self._cModel.get_pager_list(business_id, pager, lang_code)

    def delete(self, business_id, id):
        if self._cModel.delete(business_id, id):
            self._cModel.update_comment_num(business_id)
        return True

    def has_commented_by_user(self, bid, uid):
        if not uid or uid == 0:
            return False
        comment = self._cModel.get_latest_one_by_user(bid, uid)
        if comment:
            return True
        return False


