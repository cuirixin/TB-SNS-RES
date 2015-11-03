#!/usr/bin/env python2.7
#-*- coding:utf8 -*-
#
# 2014-3-8 by Victor
# Copyright 2014 Tubban
from _module import const
from _module._base_m_ import BaseModel
from _module._lib.common import Common

class MealModel(BaseModel):
    
    
    def __init__(self, uid = None):
        self._uid = uid
        self._meal_table = 'r_meal'
        self._meal_image_table = 'r_meal_image'
        self._meal_comment_table = 'r_meal_comment'
        self._business_table = 'business'

    def get_brief_by_id(self, meal_id):
        # sql构建
        fields = ['id', 'b_id', 'b_uuid', 'name', 'name_cn', 'digest_cn', 'type', 'd_price', 'o_price', 'cover', 'currency_id', 'description']
        select_str = self._gen_fields_str(fields)
        sql = "SELECT %s, DATE_FORMAT(nt_validity_from, '%%%%Y-%%%%m-%%%%d') nt_validity_from, DATE_FORMAT(nt_validity_to, '%%%%Y-%%%%m-%%%%d') nt_validity_to" \
                " FROM %s " \
                " WHERE `id`=%d "\
                " LIMIT 1" % (select_str, self._meal_table, meal_id)
        return self.get_one(sql)
        
    # ---------------For Op--------------------
    def _add(self, fields):
        
        meal = {
            'b_id': {'type':'d', 'required':1},
            'b_uuid': {'type':'s', 'required':1},
            'name': {'type':'s', 'required':1},
            'name_cn': {'type':'s', 'required':1},
            'type': {'type':'d', 'default':1},
            'city_id': {'type':'d', 'required':1},
            'country_id': {'type':'d', 'required':1},
            'currency_id': {'type':'d', 'required':1},
            
            'categories':{'type':'s', 'default':''},
            'cuisine':{'type':'d', 'default':0},
            'd_price': {'type':'f', 'default':0},
            'o_price': {'type':'f', 'default':0},
            'status': {'type':'d', 'default':const.Meal.STATUS_SOLDOUT},
            'cover': {'type':'s', 'default':''},
            'description' : {'type':'s', 'default':''},
            'description_cn' : {'type':'s', 'required':1},
            'digest_cn' : {'type':'s', 'default':''},
            'sortrank' : {'type':'d', 'default':1},
            'add_time': {'type': 'd', 'default': Common.get_current_time()},
            
            'nt_preorder_type': {'type':'d', 'default':0},
            'nt_preorder_time': {'type':'d', 'default':86400},
            'nt_content' : {'type':'s', 'default':''},
            'nt_content_cn' : {'type':'s', 'required':1},
            'nt_retreat': {'type':'d', 'default':0},
            'nt_use_time' : {'type':'s', 'required':1},
            'nt_use_weekend' : {'type':'d', 'required':1},
            'nt_validity_from' : {'type':'s', 'required':1},
            'nt_validity_to' : {'type':'s', 'required':1},
        }
        
        ret = self._args_handle('insert', fields, meal)   
        if not ret[0]:
            # todo:
            return ret
        return self._insert(self._meal_table, meal)
    
    def add(self, kwarg):
        return self._add(kwarg)
    
    def mod(self, kwarg):
        return self._mod(kwarg)
    
    def _mod(self, args):
        meal = {
            'name': {'type':'s'},
            'type': {'type':'d'},
            'status': {'type':'d'},
            'cover': {'type':'s',},
            'order_num' : {'type':'d'},   # For User
            'comment_num' : {'type':'d'},
        }   
        if not args.has_key('id'):
            return False

        ret = self._args_handle('update', args, meal)               
        if not ret[0]:
            return False
        where = "id=%d" % (args['id'])
        meal['mod_time'] = {'type': 'd', 'value': Common.get_current_time()}
        meal['version'] = {'type': 'd', 'value': Common.get_current_time()}
        ret = self._update(self._meal_table, meal, where)
        if not ret[0]:
            return False
        return True
    
    def delete(self, id):
        sql = "UPDATE %s SET status=%d WHERE id=%d" % (self._meal_table, const.Meal.STATUS_DELETE, id)
        return self.execute(sql)[0]
    
    def update_comment_num(self, id):
        table = self._get_mo_split_table(id, self._meal_comment_table, const.DB.R_MEAL_COMMENT_SPLIT)
        sql = "select count(1) as total from %s where meal_id=%d" % (table, id)
        total = self.get_one(sql)['total']
        return self.mod({"id": id, "comment_num": total})
        
    def add_image(self, fields):
        image = {
            'uuid': {'type':'s', 'required':1},
            'meal_id': {'type':'d', 'required':1},
            'status': {'type':'d', 'default':1},
            'sortrank': {'type':'d', 'default':1},
        }
        
        ret = self._args_handle('insert', fields, image)   
        if not ret[0]:
            return ret
        return self._insert(self._meal_image_table, image)
    
    def del_image(self, meal_id, image_uuid):
        sql = "UPDATE %s SET status=%d WHERE meal_id=%d and uuid='%s'" % (self._meal_image_table, const.Meal.STATUS_DELETE, meal_id, image_uuid)
        return self.execute(sql)[0]
    
    """
    Func: 返回所有未删除的套餐
    """
    def get_all_by_restaurant_to_manage(self, b_uuid):
        sql = "SELECT * FROM %s WHERE b_uuid='%s' and status>%d order by sortrank asc" % (self._meal_table, b_uuid, const.Meal.STATUS_DELETE)
        return self.get_rows(sql)
    
    #----------------For User------------------------
    
    """
    Func: 返回所有在售的套餐
    """
    def get_all_by_restaurant(self, b_uuid):
        sql = "SELECT * FROM %s WHERE b_uuid='%s' and status=%d order by sortrank asc" % (self._meal_table, b_uuid, const.Meal.STATUS_VALID)
        return self.get_rows(sql)
    
    def get_like_pager_list(self, uid, pager, fields=None):
        like_user_table = self._get_mo_split_table(uid, "r_meal_like_user", const.DB.R_MEAL_LIKE_USER_SPLIT)
        size = pager['ps']
        offset = size*(pager['p']-1)
        
        if fields is None:
            fields = ['id', 'b_id', 'name', 'name_cn', 'type', 'd_price', 'o_price', 'currency_id', 'order_num', 'like_num', 'description', 'description_cn', 'digest_cn']
        
        fields_str = self._gen_fields_str(fields, "m")
        
        where_sql = ' WHERE r.uid=%d  ' % uid
        count_sql = "SELECT count(1) as total FROM %s r " % like_user_table + where_sql
        count =  self.get_one(count_sql)['total']
        if count<>0:
            # c.uid as user_id, c.username as user_name
            se_sql = "SELECT %s " \
                        " FROM %s r " \
                        " left join %s m on m.id=r.meal_id " \
                        " %s " \
                        " limit %s,%s"  \
            % (fields_str, like_user_table, self._meal_table, where_sql, offset, size)
            rows = self.get_rows_by_slave(se_sql)
            return dict(total=count, data=rows)
        else:
            return dict(total=0, data=[])
            
    
    def get_cnt_by_restaurant(self, b_uuid):
        sql = "SELECT count(1) as total FROM %s WHERE b_uuid='%s' and status=%d" % (self._meal_table, b_uuid, const.Meal.STATUS_VALID)
        return self.get_one(sql)['total']
    
    def get_all(self, orderby='sortrank'):
        sql = "SELECT * FROM %s WHERE status=%d order by %s asc" % (self._meal_table, const.Meal.STATUS_VALID, orderby)
        return self.get_rows(sql)
    
    def get_images(self, meal_id):
        sql = "SELECT uuid, meal_id FROM %s WHERE meal_id=%d and status>%d order by sortrank asc" % (self._meal_image_table, meal_id, const.Meal.STATUS_DELETE)
        return self.get_rows_by_slave(sql)
    
    def get_by_fields(self, meal_id, fields):
        select_str = self._gen_fields_str(fields)
        sql = "SELECT %s, DATE_FORMAT(nt_validity_from, '%%%%Y-%%%%m-%%%%d') nt_validity_from, DATE_FORMAT(nt_validity_to, '%%%%Y-%%%%m-%%%%d') nt_validity_to FROM %s WHERE `id`=%d" % (select_str, self._meal_table, meal_id)
        return self.get_one(sql)
    
    def get_by_id(self, meal_id):
        sql = "SELECT a.*, DATE_FORMAT(a.nt_validity_from, '%%%%Y-%%%%m-%%%%d') nt_validity_from, DATE_FORMAT(a.nt_validity_to, '%%%%Y-%%%%m-%%%%d') nt_validity_to  FROM %s a WHERE a.id=%d" % (self._meal_table, meal_id)
        return self.get_one(sql)
    
    def add_order_num(self, id, num):
        sql = "UPDATE %s SET order_num=order_num+%d, version=%d WHERE id=%d limit 1" % (self._meal_table, int(num), Common.get_current_time(), int(id))
        return self.execute(sql)
    
    def get_hot_meals(self):
        sql = "SELECT id, order_num, name FROM %s WHERE status=%d order by order_num desc limit 10" % (self._meal_table, const.Meal.STATUS_VALID)
        return self.get_rows(sql)
    
    def has_like(self, meal_id, uid):
        like_user_table = self._get_mo_split_table(uid, "r_meal_like_user", const.DB.R_MEAL_LIKE_USER_SPLIT)
        if meal_id is None or uid is None:
            return False
        sql = "SELECT count(1) as total FROM %s WHERE meal_id=%d AND uid=%d" % (like_user_table, int(meal_id), int(uid))
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
        

    def get_city_ids(self):
        sql = "select status, group_concat(city_id) as ids from %s where status=%d group by status;" % (self._meal_table, const.Meal.STATUS_VALID)
        ret = self.get_rows(sql)
        if len(ret)==0:
            return ''
        else:
            return ret[0]['ids']
        