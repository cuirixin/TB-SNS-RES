#!/usr/bin/env python2.7
#-*- coding:utf8 -*-
#
# 2013-12-4 by Victor
# Copyright 2013 Tubban
from _module import const
from _module._base_c_ import BaseControl
from _module._lib.common import Common
from _module._lib.lang import Lang
from _module._lib.mgdb import MgDB
from _module.business.model import BusinessModel
from _module.comment.model import MealCommentModel
from _module.meal.model import MealModel
from _module.morder.model import MealOrderModel
from _module.restaurant.control import RestaurantControl
from _module.restaurant.model import RestaurantModel
from _module.sys_data.model import SysdataModel
import pymongo

class MealControl(BaseControl):
    def __init__(self, uid = None,userLang=None):
        self._uid = uid
        self._mealModel = MealModel(self._uid)
        self._mealCommentModel = MealCommentModel()
        self._rModel = RestaurantModel(self._uid)
        self._bModel = BusinessModel(self._uid)
        self._mealOrderModel = MealOrderModel()
        self._sysDataModel = SysdataModel()
        self._field = Lang.get_db_field_name(userLang)
        
        self._rControl = RestaurantControl(self._uid, userLang)
        
        self._client = MgDB.get_client()
        self._db = self._client.tubban

    def _get_filter_list(self, lat, lon, _limit=10, \
                             start_index=0, max_distance=2, city_id=-1, subcategory_id=0, \
                             district_id=0, district_type_id=0, s_type=0, s_direction=pymongo.ASCENDING, f_type = [], key = ''):
        # 过滤分页条件
        if start_index <=0 :
            start_index = 0

        if start_index >= 200:
            return []

        # 构造查询条件： category, city_id, district_id, subcategory_id
        conditions = {
            "status": const.Meal.STATUS_VALID,
            "city_id": city_id,
        }
        if district_id > 0:
            conditions['district_id'] = district_id
            if district_type_id > 0:
                conditions['district_type_id'] = district_type_id
        if subcategory_id > 0:
            conditions['subcategory_id'] = subcategory_id

        # 构造查询条件：s_type， f_type
        s_type_dict = [
            {"field": "default"}, # 0 默认排序
            {"field": "distance"}, # 1 离我最近
            {"field": "score"}, # 2 评价最高
            {"field": "order_num"}, # 3 人气最高
            {"field": "d_price"}, # 4 价格
        ]
        
        f_type_dict = [
            {"field": "default", "condition": None}, # 0 无
            {"field": "nt_use_weekend", "condition": {"nt_use_weekend": {"$gt": 0}}}, # 1 节假日可用
            {"field": "nt_preorder_type", "condition": {"nt_preorder_type": 0}}, # 2 无需预约
        ]
        
        # 构造排序和过滤条件
        sort_field = None
        if s_type > 1:
            sort_field = s_type_dict[s_type]['field']
            
        if len(f_type) > 0:
            for o in f_type:
                if int(o) > 0:
                    conditions = dict(conditions.items()+f_type_dict[int(o)]['condition'].items())
        
        meal_collection = self._db.restaurant_meals
        
        # 如果过滤条件为附近，或者排序方式为距离最近
        if district_id == -1 or s_type == 1:
            if max_distance > 0:
                conditions['coordinate'] = {
                    '$nearSphere':[lon, lat],
                    '$maxDistance' : max_distance/6371.0
                }
            else:
                conditions['coordinate'] = {
                    "$near": [lon, lat]
                }
                
        # 名称过滤
        if key and key.strip() <> '':
            conditions["$or"] = [{"name": {"$regex": key, "$options": "i"}}, {"address": {"$regex": key, "$options": "i"}}]
            #conditions['name'] = {"$regex": key}

        #print conditions
        # 查询
        if sort_field:
            cursor = meal_collection.find(conditions).sort(sort_field, s_direction).limit(_limit+start_index)
        else:
            cursor = meal_collection.find(conditions).limit(_limit+start_index)
        
        meal_list = []
        index = 0
        for meal in cursor:
            index = index + 1
            if index < start_index+1:
                continue
            meal['distance'] = Common.get_distance(lat, lon, meal['coordinate'][1], meal['coordinate'][0])
            meal_list.append(meal)
        return meal_list
            
    """
    Func: 获取餐厅筛选列表
    Used by: Customer/Manager/OP
    """
    def get_filter_list(self, pager, city_id=0, subcategory_id=0, district_id=0, district_type_id=0, distance=-1, lat=0, lon=0, \
                        s_type=0, s_direction=-1, f_type = [], key = ''):
        
        size = pager['ps']
        offset = size*(pager['p']-1)
        _list = []
        
        # 如果区域为“附近”或者排序为“距离我最近” 则需要lbs按距离查询
        _list = self._get_filter_list(lat = lat, 
                                     lon = lon, 
                                     _limit = size, 
                                     start_index = offset, 
                                     max_distance = distance,
                                     city_id = city_id,
                                     subcategory_id = subcategory_id,
                                     district_id = district_id,
                                     district_type_id = district_type_id,
                                     s_type = s_type,
                                     s_direction = s_direction,
                                     f_type = f_type,
                                     key = key)
        """
        _output = []
        meal_fields = ['id', 'uuid', 'name', 'name_cn', 'cover', 'score', 'price_avg', 'comment_num']
        for one in _list:
            business = self._bModel.get_by_fields(one['id'], business_fields)
            if business:
                business['distance'] = one['distance']
                _output.append(business)
        """
        
        _output = _list
        
        for one in _output:
            one['currency'] = self._sysDataModel.get_currency(one['currency_id'], self._field)
        
        return {"total": -1, "data": _output}
        
    def get_near_pager_list(self, pager, lat, lon, max_distance=None):
        size = pager['ps']
        offset = size*(pager['p']-1)
        _list = []
        
        if max_distance:
            _list = self.get_near_list_by_distance(lat, lon, size, offset, max_distance)
        else:
            _list = self.get_near_list(lat, lon, size, offset)
        
        """
        _output = []
        meal_fields = ['id', 'uuid', 'name', 'name_cn', 'cover', 'score', 'price_avg', 'comment_num']
        for one in _list:
            business = self._bModel.get_by_fields(one['id'], meal_fields)
            if business:
                business['distance'] = one['distance']
                _output.append(business)
        """
        return {"total": -1, "data": _list}
    
    
        """
    Func: 返回附近的套餐列表，按距离又远到近排序
    """
    def get_near_list(self, lat, lon, _limit=20, start_index=0):
        
        if start_index <=0 :
            start_index = 0
        
        if start_index >= 200:
            return []
        
        meal_collection = self._db.restaurant_meals
        
        meals = meal_collection.find({
            'status': const.Meal.STATUS_VALID,
            "coordinate": {
                "$near": [lon, lat]
            }
        }).limit(_limit+start_index)
        
        meal_list = []
        index = 0
        for meal in meals:
            index = index + 1
            if index < start_index+1:
                continue
            meal_list.append(meal)
        return meal_list
    
    def get_near_list_by_distance(self, lat, lon, _limit=20, start_index=0, max_distance=5):

        meal_collection = self._db.restaurant_meals
        
        # 最多200条
        if start_index <=0 :
            start_index = 0
        
        if start_index >= 200:
            return []
        
        meals = meal_collection.find({
            'status': const.Meal.STATUS_VALID,
            'coordinate':{
                '$nearSphere':[lon, lat],
                '$maxDistance' : max_distance/6371.0
             }
        }).limit(_limit+start_index)
        
        meal_list = []
        index = 0
        for meal in meals:
            index = index + 1
            if index < start_index+1:
                continue
            meal_list.append(meal)
        return meal_list
        
    def add_image(self, meal_id, image_uuid):
        relation = {
            "meal_id":meal_id,
            "uuid":image_uuid,
            "sortrank":1
        }
        return self._mealModel.add_image(relation)
        
    def del_image(self, meal_id, image_uuid):
        return self._mealModel.del_image(meal_id, image_uuid)
        
    def add(self, meal):
        ret =  self._mealModel.add(meal)
        if ret[0]:
            self._rControl.update_menu_num(meal['b_id'])
        return ret
    
    def delete(self, id):
        meal = {'id': id, 'status': const.Meal.STATUS_DELETE}
        return self.mod(meal)
        
    def mod(self, meal):
        _meal = self._mealModel.get_by_id(meal['id'])
        if not _meal:
            return False
        flag = self._mealModel.mod(meal)
        if flag:
            """ 留给Mongo统一处理
            if meal.has_key('status'):
                meal_collection = self._db.restaurant_meals
                _tmp = {"status": meal['status']}
                meal_collection.update({"id": meal['id']}, {"$set":_tmp})
            """
            self._rControl.update_menu_num(_meal['b_id'])
        return flag
    
    def get_by_id(self, id):
        return self._mealModel.get_by_id(id)
    
    def get_detail_for_op(self, id):
        """
        fields = ['id', 'b_id', 'b_uuid', 'name', 'name_cn', 'type', 'd_price', 'o_price', \
                  'cover', 'description', 'description_cn', 'status', 'order_num', \
                  'like_num', 'comment_num', 'city_id', 'categories', 'digest_cn']
        meal = self._mealModel.get_by_fields(id, fields)
        """
        meal = self._mealModel.get_by_id(id)
        if meal:
            _images = self._mealModel.get_images(meal['id'])
            meal['images'] = []
            for one in _images:
                meal['images'].append(one['uuid'])
            meal['categories'] = self._sysDataModel.get_cuisine_style(Common.filter_comma_ids(meal['categories']), self._field)
        else:
            return None
        return meal
    
    def get_detail_for_customer(self, id, uid=None):
        fields = ['id', 'b_id', 'b_uuid', 'name_cn', 'score', 'type', 'd_price', 'o_price', \
                  'cover', 'description_cn', 'status', 'order_num', \
                  'like_num', 'comment_num', 'city_id', 'categories', 'digest_cn', \
                  'nt_retreat', 'nt_use_weekend', 'nt_use_time', 'nt_preorder_type', \
                  'nt_preorder_time', 'nt_content_cn', 'currency_id']
        meal = self._mealModel.get_by_fields(id, fields)
        if meal:
            meal['currency'] = self._sysDataModel.get_currency(meal['currency_id'], self._field)
            meal['business'] = self._bModel.get_brief_by_id(meal['b_id'])
            _images = self._mealModel.get_images(meal['id'])
            meal['images'] = []
            for one in _images:
                meal['images'].append(one['uuid'])
            meal['categories'] = self._sysDataModel.get_cuisine_style(Common.filter_comma_ids(meal['categories']), self._field)
        else:
            return None
        meal['has_like'] = 0
        if uid is not None and self._mealModel.has_like(meal['id'], uid):
            meal['has_like'] = 1
        return meal
    
    def get_detail(self, id, uid=None):
        meal = self.get_by_id(id)
        if meal:
            meal['images'] = self._mealModel.get_images(meal['id'])
            meal['currency'] = self._sysDataModel.get_currency(meal['currency_id'], self._field)
            meal['categories'] = self._sysDataModel.get_cuisine_style(Common.filter_comma_ids(meal['categories']), self._field)
        else:
            return None
        meal['has_like'] = 0
        if uid is not None and self._mealModel.has_like(meal['id'], uid):
            meal['has_like'] = 1
        return meal
    
    def get_hot_meals(self):
        meals = self._mealModel.get_hot_meals()
        return meals
    
    def get_all_by_restaurant_to_manage(self, b_uuid):
        list = self._mealModel.get_all_by_restaurant_to_manage(b_uuid)
        for one in list:
            one['images'] = []
            _images = self._mealModel.get_images(one['id'])
            for o in _images:
                one['images'].append(o['uuid'])
            ids = Common.filter_comma_ids(one['categories'])
            one['categories'] = self._sysDataModel.get_cuisine_style(ids, self._field)
        return list
    
    def get_all_by_restaurant(self, b_uuid):
        list = self._mealModel.get_all_by_restaurant(b_uuid)
        for one in list:
            one['images'] = []
            _images = self._mealModel.get_images(one['id'])
            for o in _images:
                one['images'].append(o['uuid'])
            ids = Common.filter_comma_ids(one['categories'])
            one['categories'] = self._sysDataModel.get_cuisine_style(ids, self._field)
        return list
                
    def get_list_by_restaurant(self, uuid, uid=None):
        list = self._mealModel.get_all_by_restaurant(uuid)
        _list = []
        for one in list:
            _one = self._filter_fields(one, ["id", "type", "b_uuid", "cover", "name", "name_cn", "digest_cn", "d_price", "o_price", "order_num", "like_num", "order_num", "comment_num", "currency_id"])
            _one['currency'] = self._sysDataModel.get_currency(_one['currency_id'], self._field)
            _one['has_like'] = 0
            if uid is not None and self._mealModel.has_like(_one['id'], uid):
                _one['has_like'] = 1
            _list.append(_one)
        return _list
    
    def get_like_pager_list(self, uid, pager):
        fields = ['id', 'cover', 'status', 'name', 'name_cn', 'digest_cn', 'comment_num', \
                  'o_price', 'd_price', 'nt_preorder_type', 'nt_use_weekend', \
                  'order_num', 'like_num', 'score', 'type', 'currency_id', 'description_cn']
        
        data =  self._mealModel.get_like_pager_list(uid, pager, fields=fields)
        for one in data['data']:
            one['currency'] = self._sysDataModel.get_currency(one['currency_id'], self._field)
        return data
    """
    Func: 获取所有的套餐，按order_num排序
    """
    def get_all(self):
        list = self._mealModel.get_all(orderby='order_num')
        _list = []
        for one in list:
            _one = self._filter_fields(one, ["id", "type", "b_uuid", "cover", "name", "description", "d_price", "o_price", "order_num", "like_num", "order_num", "comment_num"])
            _one['has_like'] = 0
            if self._uid is not None and self._mealModel.has_like(_one['id'], self._uid):
                _one['has_like'] = 1
            _list.append(_one)
        return _list
    
    def like(self, uid, meal_id):
        return self._mealModel.add_like(meal_id, uid)
    
    def del_like(self, uid, meal_id):
        return self._mealModel.del_like(meal_id, uid)
        
    def add_comment(self, comment):
        ret = self._mealCommentModel.add(comment)
        if not ret[0]:
            return False
        
        meal_order_id = comment['meal_order_id']
        meal_id = comment['meal_id']
        self._mealModel.update_comment_num(meal_id)
        self._mealOrderModel.mod({"id": meal_order_id, "status_comment": const.MealOrder.STATUS_COMMENT_SUBMITED})
        return True
        
        
    def get_comment_pager_list(self, meal_id, pager, lang_code=None):
        return self._mealCommentModel.get_pager_list(meal_id, pager, lang_code)
    
    
    def add_order_num(self, meal_id, meal_num):
        return self._mealModel.add_order_num(meal_id, meal_num)
    
    
    ############For web
    
    def search(self, type=0, cuisine=[], area=0, sort=0):
        
        if sort == 0:
            sort = ' m.like_num desc'
        elif sort == 1:
            sort = ' m.d_price asc'
        elif sort == 2:
            sort = ' m.order_num desc'
        list = self._mealModel.search(type, cuisine, area, sort)
        for one in list:
            one['restaurant'] = self._bModel.get_brief_by_id(one['b_id'])
            city = self._sysDataModel.get_city_by_id(one['city_id'], self._field)
            if city:
                one['restaurant_city_name'] = city['name']
            else:
                one['restaurant_city_name'] = ''
        return list
        
    def get_meal_cities(self):
        
        ids = self._mealModel.get_city_ids()
        return self._sysDataModel.get_city_by_ids(ids, self._field)
        
        