#!/usr/bin/env python2.7
#-*- coding:utf8 -*-
#
# 2014-1-19 by Victor
# Copyright 2014 Tubban
from _module import const
from _module._base_m_ import BaseModel
from _module._lib.common import Common

class DishModel(BaseModel):
    def __init__(self, uid = None):
        self._uid = uid
        self._dish_table = 'r_dish'
        self._dish_like_user_table = 'dish_like_user'
        
    def get_brief_list(self, carte_id, dishgroup_id, visible=None):
        sql = "SELECT id, number, name, ingredient, cooktechnique, mouthfeel, `cover` , " \
                " `recommend`,`sortrank`,`price`,`price_num`,`price_unit`,`like_num` FROM %s " \
                " WHERE " % self._dish_table
        sql += " carte_id=%s " % carte_id
        sql += " and dishgroup_id=%s " % dishgroup_id
        sql += " and status=%d " % const.Dish.STATUS_VALID
        if visible is not None:
            sql += " and visible=%d " % int(visible)
        sql += " order by recommend desc"
        return self.get_rows(sql)    
    
    
    def get_by_fields(self, id, fields=None):
        if not fields:
            fields = ['id', 'name', 'cover', 'price', 'price_num', 'price_unit']
        select_str = self._gen_fields_str(fields)
        sql = "SELECT %s FROM %s WHERE id=%s limit 1" %(select_str, self._dish_table, id)
        return self.get_one(sql)
    
    def get_brief_all_list_by_restaurant(self, rid):
        fields = ['id', 'name', 'cover', 'price', 'price_num', 'price_unit', 'recommend', 'dishgroup_id', 'carte_id']
        select_str = self._gen_fields_str(fields)
        sql = "SELECT %s " \
                " FROM %s " \
                " WHERE `restaurant_id`=%d and status>%d order by add_time desc "\
                % (select_str, self._dish_table, rid, const.Dish.STATUS_DELETE)
                
        return self.get_rows(sql)
    
    def get_by_id(self,id):
        sql = "SELECT id, number, recommend, name, ingredient, cooktechnique, mouthfeel, visible, " \
                " carte_id, dishgroup_id, cover ,`price`,`price_num`,`price_unit` FROM %s WHERE id=%s " %(self._dish_table, id)
        return self.get_one(sql)
    
    def get_detail(self, id):
        sql = "SELECT id, number, name, recommend, ingredient, cooktechnique, mouthfeel, " \
                " visible, tag, carte_id, dishgroup_id, restaurant_id, `cover`,`sortrank`,`price`,`price_num`,`price_unit`,`like_num` " \
                " from %s where id=%s" % (self._dish_table, id)
        return self.get_one(sql)
    
    
    def add_like(self, uid, dish_id):
        sql = "UPDATE %s SET like_num=like_num+1 WHERE id=%d" % (self._dish_table, dish_id)
        flag = self.execute(sql)[0]
        if not flag:
            return flag
        
        if uid <> 0:
            like_user_table = self._get_mo_split_table(uid, self._dish_like_user_table, const.DB.DISH_LIKE_USER_SPLIT)
            sql_relation = "REPLACE INTO %s(`uid`,`dish_id`,`add_time`) VALUES(%d,%d,%d)" % \
                            (like_user_table, uid, dish_id, Common.get_current_time())
            return self.execute(sql_relation)[0]
        return True
    
    def remove_like(self, uid, dish_id):
        sql = "UPDATE %s SET like_num=like_num-1 WHERE id=%d" % (self._dish_table, dish_id)
        flag = self.execute(sql)[0]
        if not flag:
            return flag
        
        if uid <> 0:
            like_user_table = self._get_mo_split_table(uid, self._dish_like_user_table, const.DB.DISH_LIKE_USER_SPLIT)
            sql_relation = "DELETE FROM %s WHERE uid=%d and dish_id=%d" % \
                            (like_user_table, uid, dish_id)
            return self.execute(sql_relation)[0]
        return True
    
    def has_like(self, uid, dish_id):
        like_user_table = self._get_mo_split_table(uid, self._dish_like_user_table, const.DB.DISH_LIKE_USER_SPLIT)
        sql = "SELECT count(1) as total FROM %s WHERE dish_id=%d AND uid=%d" % (like_user_table, int(dish_id), int(uid))
        if self.get_one(sql)['total'] == 0:
            return False
        return True
    
    ############################# TODO
    
    """
    Func:获取菜品列表，例如：某菜单下所有菜品、某菜单下某菜品类别的所有菜品
    """
    def get_list(self, carte_id=None, dishgroup_id=None, visible=None):
        sql = "SELECT id, number, name, ingredient, cooktechnique, mouthfeel, visible, carte_id, " \
                " dishgroup_id, `cover` ,`recommend`,`sortrank`, `price`,`price_num`,`price_unit`,`like_num` FROM %s " \
                " WHERE status>%d " % (self._dish_table, const.Dish.STATUS_DELETE)
        if carte_id<>None:
            sql += " and carte_id=%s " % carte_id
        if dishgroup_id<>None:
            sql += " and dishgroup_id=%s " % dishgroup_id
        if visible<>None:
            sql += " and visible=%d " % int(visible)
        
        sql += " order by  sortrank asc, recommend desc"
        return self.get_rows(sql)
    
    def get_brief_recommend_by_restaurant(self, restid, limit=10, fields=None):
        if fields is None:
            fields = ['id', 'name', 'price', 'price_num', 'price_unit']
        select_str = self._gen_fields_str(fields)
        
        sql = "SELECT %s FROM %s WHERE restaurant_id=%d and recommend=1 and visible=1 limit %d" % \
                (select_str, self._dish_table, restid, limit)
        return self.get_rows_by_slave(sql)

    def get_recommend_by_restaurant(self, restid, limit=10):
        sql = "SELECT id, name, ingredient, cooktechnique, mouthfeel, " \
                " carte_id, dishgroup_id, `cover` ,`price`,`price_num`,`price_unit` " \
                " from %s where restaurant_id=%d and recommend=1 and visible=1 " \
                " ORDER by `sortrank` asc LIMIT %d" % (self._dish_table, restid, limit)
        return self.get_rows_by_slave(sql)
    
    def get_noRecommendNoCoverDish(self,restid, limit=10):
        sql = "SELECT id, number, name, `cover`,ingredient, cooktechnique, mouthfeel,`sortrank`,`price`,`price_num`,`price_unit` " \
                " from %s where restaurant_id=%d and recommend=0 and visible=1 and cover=''" \
                " ORDER by `sortrank` asc LIMIT %d" % (self._dish_table, restid, limit)
        return self.get_rows(sql)

    def get_noRecommendButHasCoverDish(self,restid, limit=10):
        sql = "SELECT id, number, name, `cover`,ingredient, cooktechnique, mouthfeel,`sortrank`,`price`,`price_num`,`price_unit` " \
                " from %s where restaurant_id=%d and recommend=0 and visible=1 and cover!=''" \
                " ORDER by `sortrank` asc LIMIT %d" % (self._dish_table, restid, limit)
        return self.get_rows(sql)
    
    
    def add(self, fields):
        return self._add(fields)

    def _add(self, fields):
        dish = {
            'name': {'type':'s', 'required':1},
            'number': {'type':'s', 'default':''},
            'visible': {'type':'d', 'default':0},
            'ingredient': {'type':'s', 'default':''},
            'cooktechnique': {'type':'s', 'default':''},
            'mouthfeel': {'type':'s', 'default':''},
            'dishgroup_id': {'type':'s', 'default':0},
            'restaurant_id': {'type':'d', 'default':0},
            'carte_id': {'type':'d', 'default':0},
            'cover': {'type':'s', 'default':''},
            'recommend': {'type':'d', 'default':0},
            'praise': {'type':'d', 'default':0},
            'price': {'type':'f', 'default':0},
            'price_num': {'type':'d', 'default':1},
            'price_unit': {'type':'f', 'default':101},
            'add_time': {'type':'d', 'default':Common.get_current_time()},
        }
        
        ret = self._args_handle('insert', fields, dish)               
        if not ret[0]:
            return ret
        return self._insert(self._dish_table, dish)
    
    def mod(self, args):
        return self._mod(args)
    
    def _mod(self, args):
        dish = {
            'name': {'type':'s'},
            'number': {'type':'s'},
            'visible': {'type':'d'},
            'ingredient': {'type':'s'},
            'cooktechnique': {'type':'s'},
            'mouthfeel': {'type':'s'},
            'dishgroup_id': {'type':'d'},
            'restaurant_id': {'type':'d'},
            'carte_id': {'type':'d'},
            'cover': {'type':'s'},
            'recommend': {'type':'d'},
            'praise': {'type':'d'},
            'price': {'type':'f'},
            'price_num': {'type':'d'},
            'price_unit': {'type':'f'},
        }   
        if not args.has_key('id'):
            return False

        ret = self._args_handle('update', args, dish)               
        if not ret[0]:
            return False
        
        if len(dish) == 0:
            return True
        
        where = "id=%d" % (int(args['id']))
        ret = self._update(self._dish_table, dish, where)
        if not ret[0]:
            return False
        return True
    
    def get_by_number(self, carteid, number):
        sql = "SELECT * FROM %s WHERE carte_id=%s and number='%s' " \
                % (self._dish_table, carteid, number)
        return self.get_one(sql)
        
    def get_carte_id(self,dishid):
        sql = " SELECT carte_id FROM %s WHERE id=%s;"  % (self._dish_table, dishid)
        ret = self.get_one(sql)
        if ret:
            return ret['carte_id']
        else:
            return None
    
    def delete(self, id):
        sql = "UPDATE %s SET status=%d WHERE id=%d" % (self._dish_table, const.Dish.STATUS_DELETE, int(id))
        return self.execute(sql)[0]
    
    def add_praise(self,dishid):
        sql = "UPDATE %s SET `praise` = `praise`+1 where id=%s;"  % (self._dish_table, dishid)
        return self.update(sql)
    
    def set_recommend(self,dishid,recommended):
        sql = "UPDATE %s SET `recommend` = %s where id=%s;"  % (self._dish_table, recommended, dishid)
        return self.update(sql)
    
    def set_order(self,orderIds):
        for i, Id in enumerate(orderIds):
            sql = "UPDATE %s SET `sortrank`=%s WHERE `id`=%s" % (self._dish_table,i+1,Id)
            self.update(sql)
        return True

    def get_list_by_source_carte_id(self, sf_id):
        sql = "SELECT id FROM %s " \
                " WHERE sf_id=%d " % (self._dish_table, sf_id)
        return self.get_rows(sql)
    
    def get_by_dishname(self, restaurant_id, name, carte_id):
        sql = "SELECT * FROM %s WHERE restaurant_id=%d and carte_id=%s and name='%s' limit 1 " \
                % (self._dish_table, int(restaurant_id), int(carte_id), self.escape_string(name))
        return self.get_one(sql)

    