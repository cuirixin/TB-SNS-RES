#!/usr/bin/env python2.7
#-*- coding:utf8 -*-
#
# 2014-3-8 by Victor
# Copyright 2014 Tubban
from _module import const
from _module._base_m_ import BaseModel
from _module._lib.common import Common

class TopicLocalSpecailModel(BaseModel):
    
    def __init__(self, uid = None):
        self._uid = uid
        self._topic_local_special = 'topic_local_special'
        self._topic_image_tabel = 'topic_local_special_image'
        self._topic_comment_tabel = 'topic_local_special_comment'

    def get_brief_by_id(self, id):
        # sql构建
        fields = ['id', 'country_id', 'name', 'name_cn', 'slogan', 'score', 'status', 'cover', 'tag']
        select_str = self._gen_fields_str(fields)
        sql = "SELECT %s " \
                " FROM %s " \
                " WHERE `id`=%d "\
                " LIMIT 1" % (select_str, self._topic_local_special, id)
        return self.get_one(sql)
    
    def get_images(self, id):
        # sql构建
        fields = ['uuid', 'title']
        select_str = self._gen_fields_str(fields)
        sql = "SELECT %s " \
                " FROM %s " \
                " WHERE `topic_id`=%d and status > -1 "\
                % (select_str, self._topic_image_tabel, id)
        return self.get_rows_by_slave(sql)
    
    def get_by_id(self, id):
        # sql构建
        fields = ['id', 'country_id', 'district', 'name', 'name_cn', 'slogan', 'score', 'status', 'cover', 'description', 'add_time', 'tag_id', 'tag']
        select_str = self._gen_fields_str(fields)
        sql = "SELECT %s " \
                " FROM %s " \
                " WHERE `id`=%d "\
                " LIMIT 1" % (select_str, self._topic_local_special, id)
        return self.get_one(sql)
        
    def _add(self, fields):
        
        topic = {
            'country_id': {'type':'d', 'required':1},
            'city_id': {'type':'d', 'default':0},
            'name': {'type':'s', 'required':1},
            'name_cn': {'type':'s', 'required':1},
            'slogan': {'type':'s', 'default':1},
            'score': {'type':'f', 'required':1},
            'tag': {'type':'s', 'default':''},
            'tag_id': {'type':'d', 'default':0},
            'tag_id_1': {'type':'d', 'default':0},
            'status': {'type':'d', 'default':const.Topic.STATUS_INVISIBLE},
            'cover': {'type':'s', 'default':''},
            'district': {'type':'s', 'default':''},
            'description' : {'type':'s', 'default':''},
            'add_time': {'type': 'd', 'default': Common.get_current_time()},
            'mod_time': {'type': 'd', 'default': Common.get_current_time()},
        }
        
        ret = self._args_handle('insert', fields, topic)   
        if not ret[0]:
            return ret
        return self._insert(self._topic_local_special, topic)
    
    def add(self, kwarg):
        return self._add(kwarg)
    
    def add_image(self, fields):
        image = {
            'topic_id': {'type':'d', 'required':1},
            'uuid': {'type':'s', 'required':1},
            'title': {'type':'s', 'default':''},
            'status': {'type': 'd', 'default': 1},
        }
        
        ret = self._args_handle('insert', fields, image)   
        if not ret[0]:
            return ret
        return self._insert(self._topic_image_tabel, image)
    
    def has_commented(self, id, uid):
        sql = "SELECT count(1) as total FROM %s WHERE uid=%d AND topic_id=%d " % (self._topic_comment_tabel, uid, id)
        if self.get_one_by_slave(sql)['total'] > 0:
            return True
        return False
    
    def add_comment(self, fields):
        comment = {
            'topic_id': {'type':'d', 'required':1},
            'content': {'type':'s', 'required':1},
            'uid': {'type':'d', 'default':0},
            'username': {'type': 's', 'default': "Nobody"},
            'add_time': {'type':'d', 'default':Common.get_current_time()},
        }
        
        ret = self._args_handle('insert', fields, comment)   
        if not ret[0]:
            return ret
        return self._insert(self._topic_comment_tabel, comment)
    
    def mod_image(self, uuid, args):
        image = {
            'status': {'type':'d'},
            'title' : {'type':'s'},
        }
        if not uuid:
            return False

        ret = self._args_handle('update', args, image)               
        if not ret[0]:
            return False
        where = "uuid='%s'" % uuid
        ret = self._update(self._topic_image_tabel, image, where)
        if not ret[0]:
            return False
        return True
        
    def mod(self, id, kwarg):
        return self._mod(id, kwarg)
    
    def _mod(self, id, args):
        topic = {
            'country_id': {'type':'d', 'required':1},
            'city_id': {'type':'d', 'default':0},
            'name': {'type':'s', 'required':1},
            'name_cn': {'type':'s', 'required':1},
            'slogan': {'type':'s', 'default':1},
            'score': {'type':'f', 'required':1},
            'tag': {'type':'s', 'default':''},
            'tag_id': {'type':'d', 'default':0},
            'tag_id_1': {'type':'d', 'default':0},
            'status': {'type':'d', 'default':const.Topic.STATUS_INVISIBLE},
            'cover': {'type':'s', 'default':''},
            'district': {'type':'s', 'default':''},
            'description' : {'type':'s', 'default':''},
        }   
        if not id:
            return False

        ret = self._args_handle('update', args, topic)               
        if not ret[0]:
            return False
        where = "id=%d" % (id)
        topic['mod_time'] = {'type': 'd', 'value': Common.get_current_time()}
        ret = self._update(self._topic_local_special, topic, where)
        if not ret[0]:
            return False
        return True
    
    def add_increment(self, id, type):
        if type not in [1, 2, 3]:
            return False
        if type == 1:
            sql = "UPDATE %s SET `want_eat_num`=`want_eat_num`+1 WHERE id=%d LIMIT 1" % (self._topic_local_special, id)
        elif type == 2:
            sql = "UPDATE %s SET `has_eat_num`=`has_eat_num`+1 WHERE id=%d LIMIT 1" % (self._topic_local_special, id)
        elif type == 3:
            sql = "UPDATE %s SET `comment_num`=`comment_num`+1 WHERE id=%d LIMIT 1" % (self._topic_local_special, id)
        return self.execute(sql)[0]
    
    def del_increment(self, id, type):
        if type not in [4, 5]:
            return False
        if type == 4:
            sql = "UPDATE %s SET `want_eat_num`=`want_eat_num`-1 WHERE id=%d LIMIT 1" % (self._topic_local_special, id)
        elif type == 5:
            sql = "UPDATE %s SET `has_eat_num`=`has_eat_num`-1 WHERE id=%d LIMIT 1" % (self._topic_local_special, id)
        return self.execute(sql)[0]
    
    def delete(self, id):
        sql = "UPDATE %s SET status=%d WHERE id=%d limit 1" % (self._topic_local_special, const.Topic.STATUS_DELETE, id)
        return self.execute(sql)[0]
    
    def get_pager_list(self, pager, country_id=None, fields=None, visible=None):
        size = pager['ps']
        offset = size*(pager['p']-1)
        
        if fields is None:
            fields = ['id', 'country_id', 'cover', 'tag', 'tag_id', 'name', 'name_cn', 'score', 'slogan', 'status', 'district', 'has_eat_num', 'want_eat_num']
        
        fields_str = self._gen_fields_str(fields)
        
        where_sql = ' WHERE status>%d  ' % const.Topic.STATUS_DELETE
        
        if visible is True:
            where_sql = where_sql + " AND status=%d " % const.Topic.STATUS_VALID
        
        if country_id <> None:
            where_sql = where_sql + ' and country_id=%d ' % int(country_id)
        
        count_sql = "SELECT count(1) as total FROM %s " % self._topic_local_special + where_sql
        count =  self.get_one(count_sql)['total']
        if count<>0:
            # c.uid as user_id, c.username as user_name
            se_sql = "SELECT %s " \
                        " FROM %s " \
                        " %s " \
                        " order by add_time desc " \
                        " limit %s,%s"  \
            % (fields_str,self._topic_local_special, where_sql, offset, size)
            rows = self.get_rows(se_sql)
            return dict(total=count, data=rows)
        else:
            return dict(total=0, data=[])
        
    def get_comment_pager_list(self, pager, id):
        size = pager['ps']
        offset = size*(pager['p']-1)
        
        fields = ['id', 'content', 'username', 'uid', 'add_time']
        
        fields_str = self._gen_fields_str(fields)
        
        where_sql = ' WHERE topic_id=%d and status>-1 ' % id
        
        count_sql = "SELECT count(1) as total FROM %s " % self._topic_comment_tabel + where_sql
        count =  self.get_one(count_sql)['total']
        if count<>0:
            # c.uid as user_id, c.username as user_name
            se_sql = "SELECT %s " \
                        " FROM %s " \
                        " %s " \
                        " order by add_time desc " \
                        " limit %s,%s"  \
            % (fields_str,self._topic_comment_tabel, where_sql, offset, size)
            rows = self.get_rows(se_sql)
            return dict(total=count, data=rows)
        else:
            return dict(total=0, data=[])
    
    """
    
    def del_image(self, meal_id, image_uuid):
        sql = "UPDATE %s SET status=%d WHERE meal_id=%d and uuid='%s'" % (self._meal_image_table, const.Meal.STATUS_DELETE, meal_id, image_uuid)
        return self.execute(sql)[0]
    
    
    def get_images(self, meal_id):
        sql = "SELECT uuid, meal_id FROM %s WHERE meal_id=%d and status>%d order by sortrank asc" % (self._meal_image_table, meal_id, const.Meal.STATUS_DELETE)
        return self.get_rows(sql)
    
    def get_by_fields(self, meal_id, fields):
        select_str = self._gen_fields_str(fields)
        sql = "SELECT %s, DATE_FORMAT(nt_validity_from, '%%%%Y-%%%%m-%%%%d') nt_validity_from, DATE_FORMAT(nt_validity_to, '%%%%Y-%%%%m-%%%%d') nt_validity_to FROM %s WHERE `id`=%d" % (select_str, self._meal_table, meal_id)
        return self.get_one(sql)
    
    def has_like(self, meal_id, uid):
        like_user_table = self._get_mo_split_table(uid, "r_meal_like_user", const.DB.R_MEAL_LIKE_USER_SPLIT)
        if meal_id is None or uid is None:
            return False
        sql = "SELECT count(*) as total FROM %s WHERE meal_id=%d AND uid=%d" % (like_user_table, int(meal_id), int(uid))
        if self.get_one(sql)['total'] == 0:
            return False
        return True
    
    def add_like(self, meal_id, uid):
        if self.has_like(meal_id, uid):
            return True
        if uid:
            like_table = self._get_mo_split_table(meal_id, "r_meal_like", const.DB.R_MEAL_LIKE_SPLIT)
            like_user_table = self._get_mo_split_table(uid, "r_meal_like_user", const.DB.R_MEAL_LIKE_USER_SPLIT)
            sql_relation = "INSERT INTO %s(`uid`,`meal_id`,`add_time`) VALUES(%d,%d,%d)" % \
                            (like_user_table, uid, meal_id, Common.get_current_time())
            ret  = self.execute(sql_relation)[0]
            if not ret:
                return False
            sql_relation = "INSERT INTO %s(`uid`,`meal_id`,`add_time`) VALUES(%d,%d,%d)" % \
                            (like_table, uid, meal_id, Common.get_current_time())
            ret = self.execute(sql_relation)[0]
            if not ret:
                return False
        sql = "UPDATE  %s SET like_num=like_num+1 WHERE id=%d" % (self._meal_table, int(meal_id))
        ret = self.execute(sql)[0]
        if not ret:
            return False
        return True
    
    def del_like(self, meal_id, uid):
        if uid:
            like_table = self._get_mo_split_table(meal_id, "r_meal_like", const.DB.R_MEAL_LIKE_SPLIT)
            like_user_table = self._get_mo_split_table(uid, "r_meal_like_user", const.DB.R_MEAL_LIKE_USER_SPLIT)
            sql_relation = "DELETE FROM %s WHERE `uid`=%d and `meal_id`=%d" % \
                            (like_table, uid, meal_id)
            ret  = self.execute(sql_relation)[0]
            if not ret:
                return False
            sql_relation = "DELETE FROM %s WHERE `uid`=%d and `meal_id`=%d" % \
                            (like_user_table, uid, meal_id)
            ret = self.execute(sql_relation)[0]
            if not ret:
                return False
        sql = "UPDATE  %s SET like_num=like_num-1 WHERE id=%d" % (self._meal_table, int(meal_id))
        ret = self.execute(sql)[0]
        if not ret:
            return False
        return True
        
    def search(self, type=0, cuisine=[], area=0, sort=' m.like_num desc'):
        where_sql = " WHERE m.status=%d "% const.Meal.STATUS_VALID
        if int(type)<>0:
            where_sql = where_sql + "AND m.type=%d " % int(type)
            
        cuisine_where = " 1!=1 "
        for one in cuisine:
            cuisine_where = cuisine_where + " OR m.`categories` like '%%%%%s%%%%' " % (','+str(one)+',')
        if len(cuisine) > 0:
            where_sql = where_sql + " AND ("+cuisine_where+")"
            
        if area<>0:
            where_sql = where_sql + " AND m.city_id=%d" % area
            
        sql = "SELECT * FROM %s m" \
                " %s " \
                " order by %s" % (self._meal_table, where_sql, sort)
                
        return self.get_rows(sql)
        
    """