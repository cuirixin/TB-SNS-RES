#!/usr/bin/env python2.7
#-*- coding:utf8 -*-
#
# 2014-2-9 by Victor
# Copyright 2014 Tubban
from _module import const
from _module._lib.lang import Lang
from _module.sys_data.model import SysdataModel
from _module.topic.model import TopicLocalSpecailModel

class TopicLocalSpacialControl(object):
    def __init__(self, uid = None, userLang=None):
        self._uid = uid
        self._topicLocalSpecailModel = TopicLocalSpecailModel()
        self._field = Lang.get_db_field_name(userLang)
        self._sysDataModel = SysdataModel()
    
    def add(self, topic):
        return self._topicLocalSpecailModel.add(topic)
    
    def add_image(self, image):
        return self._topicLocalSpecailModel.add_image(image)
    
    def delete(self, id):
        topic = {'id': id, 'status': const.Topic.STATUS_DELETE}
        return self.mod(topic)
    
    def delete_image(self, uuid):
        image = {"status": -1}
        return self._topicLocalSpecailModel.mod_image(uuid, image)
        
    def mod(self, id, topic):
        return self._topicLocalSpecailModel.mod(id, topic)
    
    def get_detail_by_id(self, id):
        topic = self._topicLocalSpecailModel.get_by_id(id)
        if not topic:
            return None
        topic['images'] = self._topicLocalSpecailModel.get_images(id)
        topic['has_commented'] = 0
        
        if self._uid and self.has_comment(id, self._uid):
            topic['has_commented'] = 1
        return topic

    def get_by_id(self, id):
        return self._topicLocalSpecailModel.get_by_id(id)
    
    def add_increment(self, id, type):
        return self._topicLocalSpecailModel.add_increment(id, type)
    
    def del_increment(self, id, type):
        return self._topicLocalSpecailModel.del_increment(id, type)
    
    def add_comment(self, comment):
        ret = self._topicLocalSpecailModel.add_comment(comment)
        if ret[0]:
            self._topicLocalSpecailModel.add_increment(comment['topic_id'], 3)
        return ret
    
    def has_comment(self, id, uid):
        return self._topicLocalSpecailModel.has_commented(id, uid)

    def get_pager_list(self, pager, country_id=None, visible = None):
        data = self._topicLocalSpecailModel.get_pager_list(pager, country_id=country_id, visible=visible)
        for one in data['data']:
            one['images'] = self._topicLocalSpecailModel.get_images(one['id'])
        return data
    
    def get_comment_pager_list(self, pager, id):
        return self._topicLocalSpecailModel.get_comment_pager_list(pager, id)
    