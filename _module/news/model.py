#!/usr/bin/env python2.7
#-*- coding:utf8 -*-
#
# 2013-12-4 by Victor
# Copyright 2013 Tubban
from _module import const
from _module._base_m_ import BaseModel
from _module._lib.common import Common

class BnewsModel(BaseModel):
    
    def __init__(self, uid = None):
        self._bnews_table = 'b_news'
        self._bnews_like_table = 'b_news_like'
        self._bnews_image_table = 'b_news_image'
        self._bnews_reply_table = 'b_news_reply'
        self._business_table = 'business'
        self._user_table = 'auth_user'
        self._uid = uid

    def get_by_id(self, id):
        sql = "SELECT * FROM %s WHERE id = %d" % (self._bnews_table, int(id))
        return self.get_one(sql)
    
    def _add(self, fields):
        news = {
            'b_id': {'type':'d', 'required':1},
            'b_uuid': {'type':'s', 'required':1},
            'title': {'type':'s', 'required':1},
            'content': {'type':'s', 'default':''},
            'add_time' : {'type':'d', 'default':Common.get_current_time()},
        }
        
        ret = self._args_handle('insert', fields, news)   
        if not ret[0]:
            # todo:
            return ret
        return self._insert(self._bnews_table, news)
    
    def add(self, kwarg):
        return self._add(kwarg)
    
    def change_status(self, id, status):
        sql = "UPDATE %s SET status=%d WHERE id=%d;" % (self._bnews_table, status, int(id))
        ret =  self.execute(sql)[1]
        return ret
    
    def add_like(self, id, uid):
        table = self._get_mo_split_table(id, self._bnews_like_table, const.DB.B_NEWS_LIKE_SPLIT)
        
        fields = {
            "news_id":id,
            "uid":uid
        }
        relation = {
            'news_id': {'type':'d', 'required':1},
            'uid': {'type':'d', 'required':1},
            'add_time' : {'type':'d', 'default':Common.get_current_time()},
        }
        
        ret = self._args_handle('insert', fields, relation)   
        if not ret[0]:
            return False
        if not self._insert(table, relation):
            return False
        
        sql = "UPDATE %s SET like_num=like_num+1 WHERE id=%d" % (self._bnews_table, id)
        return self.execute(sql)[0]
    
    def has_like(self, id, uid):
        table = self._get_mo_split_table(id, self._bnews_like_table, const.DB.B_NEWS_LIKE_SPLIT)
        sql = "SELECT count(1) as total FROM %s WHERE news_id=%d and uid=%d" % (table, id, uid)
        if self.get_one(sql)['total'] == 0:
            return False
        return True
        
    def get_pager_list(self, pager, b_id):
        size = pager['ps']
        offset = size*(pager['p']-1)
        where_sql = " WHERE d.status>%d and d.b_id=%d" % (const.Discover.STATUS_DELETE, b_id)
        count_sql = "SELECT count(*) as total FROM %s d %s" % (self._bnews_table, where_sql)
        count =  self.get_one(count_sql)['total']
        if count<>0:
            se_sql = "SELECT d.*,b.name as business_name, b.name_cn as business_name_cn FROM %s d " \
                        " LEFT JOIN %s b on b.id=d.b_id " \
                        " %s " \
                        " order by d.add_time desc " \
                        " limit %s,%s"  \
            % (self._bnews_table, self._business_table, where_sql, offset, size)
            rows = self.get_rows(se_sql)
            return dict(total=count, data=rows)
        else:
            return dict(total=0, data=[])


    def get_reply_pager_list(self, pager, news_id):
        table = self._get_mo_split_table(news_id, self._bnews_reply_table, const.DB.B_NEWS_REPLY_SPLIT)
        size = pager['ps']
        offset = size*(pager['p']-1)
        where_sql = " WHERE d.news_id=%d and d.status>%d" % (news_id, const.BnewsReply.STATUS_DELETE)
        count_sql = "SELECT count(*) as total FROM %s d %s" % (table, where_sql)
        count =  self.get_one(count_sql)['total']
        if count<>0:
            se_sql = "SELECT d.*,u.username as u_username, u.sex as u_sex, u.email as u_email FROM %s d " \
                        " LEFT JOIN %s u on u.id=d.uid " \
                        " %s " \
                        " limit %s,%s"  \
            % (table, self._user_table, where_sql, offset, size)
            rows = self.get_rows(se_sql)
            return dict(total=count, data=rows)
        else:
            return dict(total=0, data=[])
        
    def add_image(self, fields):
        image = {
            'news_id': {'type':'d', 'required':1},
            'uuid': {'type':'s', 'required':1},
        }
        
        ret = self._args_handle('insert', fields, image)   
        if not ret[0]:
            return ret
        return self._insert(self._bnews_image_table, image)

    def get_news_images(self, news_id):
        sql = "SELECT * FROM %s WHERE news_id=%d " % (self._bnews_image_table, news_id)
        return self.get_rows(sql)

    def add_reply(self, fields):
        table = self._get_mo_split_table(fields['news_id'], self._bnews_reply_table, const.DB.B_NEWS_REPLY_SPLIT)
        reply = {
            'uid': {'type':'d', 'required':1},
            'news_id': {'type':'s', 'required':1},
            'content': {'type':'s', 'default':''},
            'status' : {'type':'d', 'default':const.BnewsReply.STATUS_VALID},
            'add_time' : {'type':'d', 'default':Common.get_current_time()},
        }
        
        ret = self._args_handle('insert', fields, reply)   
        if not ret[0]:
            # todo:
            return ret
        return self._insert(table, reply)
    
    def get_reply_by_id(self, news_id, reply_id):
        table = self._get_mo_split_table(news_id, self._bnews_reply_table, const.DB.B_NEWS_REPLY_SPLIT)
        sql = "SELECT * FROM %s WHERE id=%d " % (table, reply_id)
        return self.get_one(sql)
        
    def delete_reply(self, news_id, reply_id):
        table = self._get_mo_split_table(news_id, self._bnews_reply_table, const.DB.B_NEWS_REPLY_SPLIT)
        sql = "UPDATE %s SET status=%d WHERE id=%d " % (table, const.BnewsReply.STATUS_DELETE, reply_id)
        return self.execute(sql)[0]
        
    