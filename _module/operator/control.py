#!/usr/bin/env python2.7
#-*- coding:utf8 -*-
#
# 2014-2-9 by Victor
# Copyright 2014 Tubban
from _module import const
from _module._lib.common import Common
from _module.business.model import BusinessModel
from _module.operator.model import ProfilerModel, SalerModel
from _module.restaurant.control import RestaurantControl
from _module.restaurant.model import RestaurantModel
import MySQLdb

class ProfilerControl:
    def __init__(self, uid = None, userLang=None):
        self._uid = uid
        self._profilerModel = ProfilerModel(uid)
        self._restaurantModel = RestaurantModel(uid)
        self._businessModel = BusinessModel(uid)
        
        self._restaurantControl = RestaurantControl(uid)
                
    def add(self, comment):
        ret =  self._cModel.add(comment)
        return ret
    
    def get_locked_business(self, uid):
        return self._profilerModel.get_locked_business(uid)
    
    def get_log_by_buuid(self, buuid):
        return self._profilerModel.get_log_by_buuid(buuid)
    
    def profile_valid(self, uuid):
        business = self._businessModel.get_by_uuid(uuid)
        if business['category'] == const.Business.CATEGORY_RESTAURANT:
            restaurant = self._restaurantModel.get_by_id(business['id'])
            msg = [
                "中文名称为空",
                "中文简介为空",
                "餐厅菜系标签为空",
                "餐厅类型未指定"
            ] 
            if business['name_cn'].strip() == '':
                return [False, msg[0]]
            
            if business['description_cn'].strip() == '':
                return [False, msg[1]]
            
            if restaurant['cuisine_style'].strip() == '':
                return [False, msg[2]]
            
            if business['subcategory_id'] == 0:
                return [False, msg[3]]
            return [True, '']
    
    def finish_edit(self, uuid, uid):
        
        bid = self._businessModel.get_id_by_uuid(uuid)
        r = self._restaurantModel.get_by_id(bid)
        return self._profilerModel.finish_edit(uuid, uid, r['has_menu'])
    
    def get_profiler_statistic(self):
        rows = self._profilerModel.get_profiler_statistic()
        _rows = []
        for one in rows:
            if one['username']:
                _rows.append(one)
        return sorted(_rows, cmp=lambda x,y:cmp(x['total'],y['total']), reverse=True)
    
    def get_profiler_reports(self):
        rows = self._profilerModel.get_profiler_reports()
        return rows
    
    def report(self, uuid, user, message):
        business = self._businessModel.get_by_uuid(uuid)
        if not business:
            return False
        report = {
            "business_id" : business['id'],
            "uuid": uuid,
            "profiler" : user['id'],
            "profiler_name" : user['username'],
            "message" : message,
            "add_time" : Common.get_current_time()
        }
        ret = self._profilerModel.report_business(report)
        if ret[0]:
            self.unlock_business(uuid, user['id'])
        return True
    
    
    def verify(self, b_uuid, verify, verify_note):
        return self._profilerModel.mod(b_uuid, {"verify": verify, "verify_note":verify_note})
    
    def unlock_business(self, uuid, uid):
        return self._profilerModel.unlock_business(uid, uuid)
    
    def _is_chain(self, business):
        _business = self._profilerModel.filt_business(" category=3 and name='%s' and description_cn!='' and city_id=%d and status>0 " % (MySQLdb.escape_string(business['name']), business['city_id']))
        if not _business:
            return False
        _restaurant = self._restaurantModel.get_by_id(_business['id'])
        # 如果是连锁店，根据已有的翻译情况自动修改当前餐厅
        _b = {
            "business_id" : business['id'],
            "name_cn" : _business['name_cn'],
            "description": _business['description'],
            "description_cn": _business['description_cn'],
            "cuisine_style": _restaurant['cuisine_style'],
            "price_category": _restaurant['price_category'],
            "dining_option": _restaurant['dining_option'],
            "reservable": _restaurant['reservable'],
            "reserve_ahead": _restaurant['reserve_ahead'],
        }
        if self._restaurantControl.mod(_b):
            return True
        return False
    
    def _filt_one(self, uid, start_id, city_id):
        return self._profilerModel.filt_business(" city_id=%d and district_id!=0 and category=3 and description_cn='' and status>0 and id not in (select business_id from %s) and uuid not in (select b_uuid from %s)" % (city_id, "op_profile_report", "op_user_profile_lock"))
        """
        # 获取某城市在景点周边的中文简介为空的不在报错记录内的餐厅
        business = self._profilerModel.filt_business(" city_id=%d and district_id!=0 and category=3 and description_cn='' and status>0 and id not in (select business_id from %s) and uuid not in (select b_uuid from %s)" % (city_id, "op_profile_report", "op_user_profile_lock"))
        while business and self._profilerModel.is_locked_by_profiler(business['uuid']):
            start_id = business['id']
            # 
            w_sql = " city_id=%d and district_id!=0  and category=3 and description_cn='' and id > %d and status>0 and id not in (select business_id from %s)" % (city_id, start_id, "op_profile_report")
            business = self._profilerModel.filt_business(w_sql)
        return business
        """
    
    def extract_one(self, uid, city_id):
        start_id = 0
        business = self._filt_one(uid, start_id, city_id)
        
        # 循环直到不是连锁店或者店铺不存在的情况
        while business and self._is_chain(business):
            business = self._filt_one(uid, business['id'])
        
        if not business:
            return None
        
        #TODO 加读锁
        self._profilerModel.lock_business(uid, business['uuid'])
        return business
        
    def get_logs_by_profier(self, uid):
        return self._profilerModel.get_logs_by_profier(uid)
    
    def get_pager_logs_by_profiler(self, pager, uid):
        return self._profilerModel.get_pager_logs_by_profiler(pager, uid)

class SalerControl:
    def __init__(self, uid = None, userLang=None):
        self._uid = uid
        self._salerModel = SalerModel(uid)
        self._restaurantModel = RestaurantModel(uid)
        self._businessModel = BusinessModel(uid)

    def lock_business(self, business, uid):
        ret =  self._salerModel.add_log({"b_uuid":business['uuid'],"b_id":business['id'], "uid":uid})
        return ret[0]
    
    def unlock_business(self, business, uid):
        ret =  self._salerModel.del_log(business['uuid'], uid)
        return ret
    
    def get_saler_statistic(self):
        rows = self._salerModel.get_saler_statistic()
        _rows = []
        for one in rows:
            if one['username']:
                _rows.append(one)
        return sorted(_rows, cmp=lambda x,y:cmp(x['total'],y['total']), reverse=True)
    
    def report(self, uuid, user, message):
        business = self._businessModel.get_by_uuid(uuid)
        if not business:
            return False
        report = {
            "business_id" : business['id'],
            "uuid": uuid,
            "profiler" : user['id'],
            "profiler_name" : user['username'],
            "message" : message,
            "add_time" : Common.get_current_time()
        }
        ret = self._profilerModel.report_business(report)
        if ret[0]:
            self.unlock_business(uuid, user['id'])
        return True
    
    def has_sale_log(self, uuid):
        return self._salerModel.has_sale_log(uuid)
        
    def get_logs_by_saler(self, uid):
        return self._salerModel.get_logs_by_saler(uid)
    
    def get_pager_logs_by_saler(self, pager, uid):
        return self._salerModel.get_pager_logs_by_saler(pager, uid)
    
    def get_log_by_uuid(self, uuid):
        return self._salerModel.get_log_by_uuid(uuid)
        
    def mod_log(self, log):
        return self._salerModel.mod_log(log)