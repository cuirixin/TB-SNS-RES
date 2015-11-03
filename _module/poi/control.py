#!/usr/bin/env python2.7
#-*- coding:utf8 -*-
#
# 2014-2-9 by Victor
# Copyright 2014 Tubban
from bson.son import SON
from _module import const
from _module._lib.common import Common
from _module._lib.lang import Lang
from _module._lib.mgdb import MgDB
from _module.sys_data.model import SysdataModel
from pymongo import GEO2D
import json
import pprint
import pymongo

"""
POIControl: POI
"""
class POIControl:
    def __init__(self, uid = None,userLang=None):
        self._uid = uid
        self._client = MgDB.get_client()
        self._db = self._client.tubban
        self._sysDataModel = SysdataModel()
        self._field = Lang.get_db_field_name(userLang)
        
    
    """
    Func: 获取附近城市, 100公里内
    """
    def get_near_city(self, lat, lon, _limit=5, max_distance=100):
        city_collection = self._db.cities
        
        cities = city_collection.find({
            'coordinate':{
                '$nearSphere':[lon, lat],
                '$maxDistance' : max_distance/6371.0
             }
        }).limit(_limit)
        
        city_list = []
        for city in cities:
            _city = self._sysDataModel.get_city_by_id(city['id'], self._field)
            city_list.append({"id": _city['id'], "name": _city['name']})
        
        return city_list
    
    """
    Func: 获取附近城市, 100公里内
    """
    def get_near_accurate_city(self, lat, lon, max_distance=100):
        sample_collection = self._db.city_samples
        
        samples = sample_collection.find({
            'coordinate':{
                '$nearSphere':[lon, lat],
                '$maxDistance' : max_distance/6371.0
             }
        }).limit(1)
        
        sample = None
        for one in samples:
            sample = one
            break
            
        city = self._sysDataModel.get_city_by_id(sample['city_id'], self._field)
        if not city:
            return None
        else:
            return city
    
    """
    Func: 返回附近的Business列表，按距离又远到近排序，不支持分批次
    """
    def get_near_list(self, lat, lon, _limit=20, category=const.Business.CATEGORY_RESTAURANT, start_index=0):
        
        if start_index <=0 :
            start_index = 0
        
        if start_index >= 200:
            return []
        
        pois_collection = self._db.business_pois
        
        pois = pois_collection.find({
            "category":category, 
            "status": {'$in': (1,5,6,10)}, # 10 是特殊状态，有但未开放
            "coordinate": {
                "$near": [lon, lat]
            }
        }).limit(_limit+start_index)
        
        business_list = []
        index = 0
        for poi in pois:
            index = index + 1
            if index < start_index+1:
                continue
            poi['distance'] = Common.get_distance(lat, lon, poi['coordinate'][1], poi['coordinate'][0])
            business_list.append(poi)
            #print poi['distance']
        
        return business_list

    """
    Func: 按距离范围查询，可用于分批次查询
    """
    def get_near_list_by_distance(self, lat, lon, _limit=50, category=const.Business.CATEGORY_RESTAURANT, start_index=0, max_distance=2):
        
        pois_collection = self._db.business_pois
        #pois_collection.
        #({'coordinate':{$near: [121.4905, 31.2646], $maxDistance:2}})
        #pois = pois_collection.find({"category":category, "coordinate": {"$near": [float(lon), float(lat)], "$maxDistance": round(max_distance/111.12, 8)}}).limit(_limit)
        #print pprint.pprint(self._db.command(SON([('geoNear', 'business_pois'), ('near', [lon, lat]), ('limit', _limit)])))
        
        #pois = pois_collection.find({"category":category, "status": {'$in': (1,5,6)}, "coordinate": SON([("$near", [lon, lat]), ("$maxDistance", max_distance/110.9)])}).limit(_limit)
        
        # 最多200条
        if start_index <=0 :
            start_index = 0
        
        if start_index >= 200:
            return []
        
        pois = pois_collection.find({
            "category":category,
            "status": {'$in': (1,5,6)}, 
            'coordinate':{
                '$nearSphere':[lon, lat],
                '$maxDistance' : max_distance/6371.0
             }
        }).limit(_limit+start_index)
        
        business_list = []
        index = 0
        for poi in pois:
            index = index + 1
            if index < start_index+1:
                continue
            poi['distance'] = Common.get_distance(lat, lon, poi['coordinate'][1], poi['coordinate'][0])
            business_list.append(poi)
            #print poi['distance']
        
        return business_list
    
    
    def get_filter_list(self, lat, lon, _limit=10, category = const.Business.CATEGORY_RESTAURANT, \
                             start_index=0, max_distance=2, city_id=-1, subcategory_id=0, \
                             district_id=0, district_type_id=0, s_type=0, s_direction=pymongo.ASCENDING, f_type = [], key = ''):
        # 过滤分页条件
        if start_index <=0 :
            start_index = 0
        
        if start_index >= 200:
            return []
        
        # 构造查询条件： category, city_id, district_id, subcategory_id
        conditions = {
            "category": category,
            "city_id": city_id,
            "status": {'$in': (1,5,6)},
        }
        if district_id > 0:
            conditions['district_id'] = district_id
            del conditions['city_id'] # 解决区域可能不在次城市的问题。后续整理完城市后，需要将区域内餐厅归到城市中去
            if district_type_id > 0:
                conditions['district_type_id'] = district_type_id
        if subcategory_id > 0:
            conditions['subcategory_id'] = subcategory_id
        
        # 构造查询条件：s_type， f_type
        s_type_dict = [
            {"field": "score_it"}, # 0 默认排序，智能排序
            {"field": "distance"}, # 1 离我最近
            {"field": "score"}, # 2 评价最高
            {"field": "like_num"}, # 3 人气最高
            {"field": "price_avg"}, # 4 价格
        ]
        
        f_type_dict = [
            {"field": "default", "condition": None}, # 0 无
            {"field": "menu_num", "condition": {"menu_num": {"$gt": 0}}}, # 1 有菜单
            {"field": "meal_num", "condition": {"meal_num": {"$gt": 0}}}, # 2 有团购 
            {"field": "reservable", "condition": {"reservable": 1}}, # 3 人气最高
            {"field": "support_cn", "condition": {"support_cn": 1}}, # 4 有中文服务
        ]
        
        # 构造排序和过滤条件
        sort_field = None
        
        if s_type <> 1:
            sort_field = s_type_dict[s_type]['field']
            
        #如果为默认排序，则强制排序为逆序
        if s_type == 0:
            s_direction = pymongo.DESCENDING
            
        if len(f_type) > 0:
            for o in f_type:
                if int(o) > 0:
                    conditions = dict(conditions.items()+f_type_dict[int(o)]['condition'].items())
        
        pois_collection = self._db.business_pois
        
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
            conditions["$or"] = [{"name": {"$regex": key, "$options": "i"}}, {"name_cn": {"$regex": key}}, {"address": {"$regex": key, "$options": "i"}}]
            # 名称的特殊查询
            if category == const.Business.CATEGORY_RESTAURANT:
                cuisine = self._sysDataModel.find_one_cuisine_style(key)
                if cuisine:
                    cuisine_style = ',%s,' % cuisine['id']
                    conditions["$or"].append({"cuisine_style": {"$regex": cuisine_style}})
                    # conditions["$or"] = [{"cuisine_style": {"$regex": cuisine_style}}]

        print conditions
        # 查询
        if sort_field:
            #print sort_field, s_direction
            cursor = pois_collection.find(conditions).sort(sort_field, s_direction).limit(_limit+start_index)
        else:
            cursor = pois_collection.find(conditions).limit(_limit+start_index)
            
        business_list = []
        index = 0
        
        for poi in cursor:
            index = index + 1
            if index < start_index+1:
                continue
            #print lat, lon, poi['coordinate'][1], poi['coordinate'][0]
            poi['distance'] = Common.get_distance(lat, lon, poi['coordinate'][1], poi['coordinate'][0])
            business_list.append(poi)
            
        # 如果是按距离排序，则强制排序一次。防止mongdo计算与外部计算不一致问题
        if s_type == 1:
            return sorted(business_list, key=lambda l : l['distance'])
        else:
            return business_list #sorted(business_list, key=lambda l : l['distance'])

    def get_list_by_range(self, lat, lon, lon_left_bottom, lat_left_bottom, lon_right_top, lat_right_top, limit=100, category=const.Business.CATEGORY_RESTAURANT):
        pois_collection = self._db.business_pois
        pois = pois_collection.find({
            "category":category,
            "coordinate": {
                "$within": {
                    "$box": [[lon_left_bottom, lat_left_bottom], [lon_right_top, lat_right_top]]
                }
            }
        }).limit(limit)
        
        business_list = []
        for poi in pois:
            poi['distance'] = Common.get_distance(lat, lon, poi['coordinate'][1], poi['coordinate'][0])
            business_list.append(poi)
        return business_list
        
        """
        $places = $this->getPlaceRepository()->createQueryBuilder()
        ->field('coordinate')->near($longitude, $latitude)
        ->maxDistance($max/111)
        ->getQuery()->toarray();

        
        
        pois_collection.find({
                                'coordinate':{
                                    $nearSphere:{ 
                                        $geometry :{ 
                                            type : "Point" ,
                                            coordinates : [lon, lat] 
                                        } ,
                                        $maxDistance : <distance in meters>
                                     }
                                 } 
                              })
        """
        
    def get_samples_by_city(self, city_id):
        
        return self._sysDataModel.get_city_samples(city_id)
        
    def add_city_sample(self, sample):
        return self._sysDataModel.add_city_sample(sample)
    
    def del_city_sample(self, id):
        return self._sysDataModel.del_city_sample(id)
        
    