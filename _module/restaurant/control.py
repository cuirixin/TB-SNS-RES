#!/usr/bin/env python2.7
#-*- coding:utf8 -*-
#
# 2013-12-4 by Victor
# Copyright 2013 Tubban
from _module import const
from _module._lib.common import Common
from _module._lib.lang import Lang
from _module._lib.log import Log
from _module.business.control import BusinessControl
from _module.business.model import BusinessModel
from _module.carte.model import CarteModel
from _module.const import Log_Msg
from _module.dish.model import DishModel
from _module.dishgroup.model import DishgroupModel
from _module.image.model import ImageModel
from _module.meal.model import MealModel
from _module.menu_package.model import MenuPackageModel
from _module.name.control import NameControl
from _module.poi.control import POIControl
from _module.price.control import PriceControl
from _module.restaurant.model import RestaurantModel
from _module.sys_data.model import SysdataModel
from _module.user.model import UserModel
import json

class RestaurantControl:
    def __init__(self, uid = None, userLang=None):
        self._uid = uid
        self._uModel = UserModel(self._uid)
        self._rModel = RestaurantModel(self._uid)
        self._bModel = BusinessModel(self._uid)
        self._cModel = CarteModel(self._uid)
        self._imageModel = ImageModel(self._uid)
        self._carteModel = CarteModel(self._uid)
        self._dgModel = DishgroupModel(self._uid)
        self._dishModel = DishModel(self._uid)
        self._mModel = MealModel(self._uid)
        self._priceControl = PriceControl()
        self._sysdataModel = SysdataModel()
        self._poiControl = POIControl()
        self._menuPackageModel = MenuPackageModel()
        self._field = Lang.get_db_field_name(userLang)
        
        
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
        _list = self._poiControl.get_filter_list(lat = lat, 
                                                 lon = lon, 
                                                 _limit = size, 
                                                 category = const.Business.CATEGORY_RESTAURANT, 
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
        
        _output = []
        business_fields = ['id', 'category', 'uuid', 'name', 'name_cn', 'cover', 'price_avg', 'comment_num', 'subcategory_id', 'currency_id', 'lat', 'lon', 'meal_num', 'menu_num']
        for one in _list:
            business = self._bModel.get_by_fields(one['id'], business_fields)
            #business['price_avg'] = one['price_avg']
            if business:
                business['score'] = one['score']
                business['distance'] = one['distance']
                #business['subcategory'] = self._sysdataModel.get_rsubcategory(business['subcategory_id'])
                business['currency'] = self._sysdataModel.get_currency(business["currency_id"], self._field)
                # 标签
                business['style_tags'] = []
                if business['category'] == const.Business.CATEGORY_RESTAURANT:
                    restaurant = self._rModel.get_by_fields(business['id'], ["cuisine_style"])
                    if not restaurant:
                        print business['id']
                    else:
                        business['style_tags'] = self._sysdataModel.get_cuisine_style(restaurant['cuisine_style'], self._field)
                _output.append(business)
        return {"total": -1, "data": _output}

    
    """
    Func: 获取附近餐厅列表
    Used by: Customer
    """
    def get_near_pager_list(self, pager, lat, lon, max_distance=None):
        size = pager['ps']
        offset = size*(pager['p']-1)
        _list = []
        if max_distance:
            _list = self._poiControl.get_near_list_by_distance(lat, lon, size, const.Business.CATEGORY_RESTAURANT, offset, max_distance)
        else:
            _list = self._poiControl.get_near_list(lat, lon, size, const.Business.CATEGORY_RESTAURANT, offset)
        
        _output = []
        business_fields = ['id', 'uuid', 'name', 'name_cn', 'cover', 'score', 'price_avg', 'comment_num']
        for one in _list:
            business = self._bModel.get_by_fields(one['id'], business_fields)
            if business:
                business['distance'] = one['distance']
                _output.append(business)
            
        return {"total": -1, "data": _output}
        
    """
    Func: 获取餐厅信息
    Used by: Customer/Manager/OP
    """
    def get_by_id(self,bid):
        return self._rModel.get_by_id(bid)
    
    """
    Func: 获取餐厅详情
    Used by: Customer Only
    """
    def get_detail_by_id_for_customer(self, rid):
        restaurant_fields = ['id', 'dining_option', 'cuisine_style', 'reservable', 'has_menu']
        restaurant = self._rModel.get_by_fields(rid, restaurant_fields)
        if not restaurant:
            return None
        restaurant['dining_option'] = self._sysdataModel.get_dining_option(restaurant['dining_option'], self._field)# self.get_dining_option_names(restaurant['dining_option'])
        restaurant['cuisine_style'] = self._sysdataModel.get_cuisine_style(restaurant['cuisine_style'], self._field)# self.get_cuisine_style_names(restaurant['cuisine_style'])
        return restaurant
        
    ############
        
    def get_menu(self, rid, version=None):
        if version is None:
            version = 0
        try:
            buffer = self._menuPackageModel.get_by_rid(rid)
            buffer_version = buffer['version']
            package = json.loads(buffer['package'])
        except Exception as e:
            print e
            package = None
            
        if package is None:
            package = self._get_menu(rid)
            self._menuPackageModel.add({'rid': rid, 'version':version, 'package':json.dumps(package)})
        else:
            if buffer_version < version:
                package = self._get_menu(rid)
                self._menuPackageModel.mod({'rid': rid, 'version':version, 'package':json.dumps(package)})
        return package
    
    def _name_key(self, id, type):
        return str(id)+'_'+str(type)
    
    def _get_menu(self, rid):
        cartes = self._carteModel.get_brief_list_by_restid(rid)
        for one in cartes:
            one['dishgroups'] = self._get_dishgroups(one['id'])
            one['dishgroups_num'] = len(one['dishgroups'])
        return cartes
    
    def _get_dishgroups(self, carte_id):
        dishgroups = self._dgModel.get_brief_list_by_carte(carte_id)
        for one in dishgroups:
            dishes = self._dishModel.get_brief_list(carte_id, one['id'])
            for d in dishes:
                
                """
                d['mouthfeel'] = d['mouthfeel'].split(',')
                if len(d['mouthfeel'])==0 or d['mouthfeel'][0]=='':
                    d['mouthfeel'] = []
                d['ingredient'] = d['ingredient'].split(',')
                if len(d['ingredient'])==0 or d['ingredient'][0]=='':
                    d['ingredient'] = []
                d['cooktechnique'] = d['cooktechnique'].split(',')
                if len(d['cooktechnique'])==0 or d['cooktechnique'][0]=='':
                    d['cooktechnique'] = []
                """
                d['price'] = {"price": d['price'], "num": d['price_num'], "portionunit_id": d['price_unit']}
                del d['price_num']
                del d['price_unit']
                #d['prices'] = self._priceControl.get_brief_prices_by_target(const.Price.TYPE_DISH, d['id'])
                
                nameControl = NameControl()
                d['names'] = nameControl.get_one(d['name'], 'all') 

                # 封面
                if d['cover'] == '' and d['names'].has_key('cover'):
                    d['cover'] = d['names']['cover']

            one['dishes'] = dishes
            one['dish_num'] = len(one['dishes'])
        return dishgroups
    
    """Public Data"""
    
    def get_all_cuisineStyle(self):
        ret =  self._rModel.get_all_cuisineStyle(self._field)
        ret1=ret[:]
        for one in ret:
            if one['continent_id']==3 and len(one['name'].split("-"))>1:
                ret1.remove(one)
        return ret1
    

    """Public Data END """
    
    def get_dining_option_names(self,ids):
        names=[]
        ret = self._sysdataModel.get_dining_option(ids, self._field)
        if ret:
            for one in ret:
                if one.name:
                    names.append(one.name)
        return names
    
    def get_cuisine_style_names(self,ids):
        names=[]
        ret = self._sysdataModel.get_cuisine_style(ids, self._field)
        if ret:
            for one in ret:
                if one.name:
                    names.append(one.name)
        return names
    
    def get_reserve_position(self, ids):
        return self._rModel.get_reserve_position(ids, self._field)
    
    def update_menu_num(self, bid):
        num_1 = self._cModel.get_cnt_by_restid(bid)
        uuid = self._bModel.get_uuid_by_bid(bid)
        num_2 = self._mModel.get_cnt_by_restaurant(uuid)
        self._bModel.mod({'business_id':bid, 'menu_num':num_1, 'meal_num':num_2})
        self._bModel.update_search_poi(bid, {'id':bid, 'menu_num':num_1, 'meal_num':num_2})
        return
    
    def get_all_meal_category(self, business_id):
        restaurant = self._rModel.get_by_id(business_id)
        return self._sysdataModel.get_cuisine_style(restaurant['cuisine_style'], self._field)
    
    # restaurant 实体信息
    
    def get_detail_by_id(self,rid):
        restaurant = self.get_by_id(rid)
        if not restaurant:
            return None
        restaurant['dining_option'] = self.get_dining_option_names(restaurant['dining_option'])
        restaurant['cuisine_style'] = self.get_cuisine_style_names(restaurant['cuisine_style'])
        return restaurant
    
    def gen_opendays_detail(self,opendays=[]):
        opendays = sorted(opendays, key=lambda openday : openday['weekday'])
        regular_day=[]
        opentime = []
        for one in opendays:
            if one["is_regular"]==1:
                regular_time=one['times']
                regular_day.append(one['weekday'])
            else:
                if len(regular_day)>0:
                    sweekday = self._bModel.get_weekday_by_id(regular_day[0],self._field)
                    eweekday = self._bModel.get_weekday_by_id(regular_day[-1],self._field)
                    if len(regular_day)==1:
                        wkd = sweekday
                    else:
                        wkd = sweekday + " ~ "+eweekday
                    opentime.append((wkd,regular_time))
                    regular_day=[]
                if one['is_free']!=1:
                    nonregular_time=one['times']
                    if len(nonregular_time)>0:
                        wkd = self._bModel.get_weekday_by_id(one['weekday'],self._field)
                        opentime.append((wkd,nonregular_time))
        # 注意边界条件
        if len(regular_day)>0:
            sweekday = self._bModel.get_weekday_by_id(regular_day[0],self._field)
            eweekday = self._bModel.get_weekday_by_id(regular_day[-1],self._field)
            if len(regular_day)==1:
                wkd = sweekday
            else:
                wkd = sweekday + " ~ "+eweekday
            opentime.append((wkd,regular_time))
        return opentime
        
    def get_detail_by_uuid(self,uuid):
        detail = {}
        bc = BusinessControl(None,self._field)
        business = bc.get_detail_by_uuid(uuid)
        if not business:
            return None
        restaurant = self.get_detail_by_id(business['id'])
        detail['business'] = business
        detail['restaurant'] = restaurant
        opendays = bc.get_opendays(business['id'])
        detail['business']['opendays']=self.gen_opendays_detail(opendays)
        detail['business']['holiday']=bc.get_closedays(business['id'])
        return detail
    
    def get_near_list(self, lat, lon):
        if lat is None or lon is None:
            return []
        list = self._bModel.get_near_list_by_dot(float(lat), float(lon), const.Business.CATEGORY_RESTAURANT)
        for l in list:
            l['distance'] = Common.get_distance(lat, lon, l['lat'], l['lon'])
        if len(list)>0:
            list = sorted(list, key=lambda l : l['distance'])
        return list
        
    def get_collect_list(self, uid):
        return self._bModel.get_collect_list(uid)
    
    """
    Func: 获取Client创建的所有Restaurant
    """
    def get_list_by_user(self, creator):
        return self._bModel.get_list_by_creator(creator, const.Business.CATEGORY_RESTAURANT)
    
    def get_list_of_reg_users(self):
        return self._bModel.get_list_of_reg_users(const.Business.CATEGORY_RESTAURANT)
    
    # 选择性修改
    def mod(self, db):
        if not self._bModel.mod(db):
            return False
        return self._rModel.mod(db)

    def add(self,db):
        transportations = db['transportation']
        if transportations:
            ts_id=[]
            for one in transportations:
                ret = self._bModel.add_transportation(one)
                if ret[0]:
                    ts_id.append(str(ret[1]))
                else:
                    Log.error("交通添加失败") 
            db['business']['transportation'] = ','.join(ts_id)
        else:
            db['business']['transportation'] = ''
        
        images = db['image']
                      
        ret = [False, None]
        b_ret = self._bModel.add(db['business'])
        if b_ret[0]:
            db['rest']['id'] = b_ret[1]
            s_ret = self._rModel.add(db['rest'])
            if s_ret[0]:
                bid=b_ret[1]
                ret=[True, b_ret[1], b_ret[2]]
                for one in images:
                    image=list(one)
                    image.append(bid)
                    tmp = self._bModel.add_business_image(image)
                    if tmp[0]:
                        self._imageModel.del_tmp(image[0])
            else:
                b_ret = self._bModel.delete(b_ret[1])
                if not b_ret[0]:
                    Log.error(Log_Msg.BUSINESS_DEL_FAILED) 
        return ret
    
    def edit(self,db):
        Log.debug(Log_Msg.SHOP_EDIT_BEGIN)
        
        bid = db['business']['id']
        
        oldTids = self._bModel.get_business_transporttation_by_bid(bid)
        transportations = db['transportation']
        if transportations:
            ts_id=[]
            for one in transportations:
                ret = self._bModel.add_transportation(one)
                if ret[0]:
                    ts_id.append(str(ret[1]))
                else:
                    Log.error("交通添加失败") 
        db['business']['transportation'] = ','.join(ts_id)
        self._bModel.delete_transportation(oldTids)
        '''
        oldOids = self._bModel.get_business_opentime_by_bid(bid)
        opentimes = db['opentime']
        open_id=[]
        for one in opentimes:
            ret = self._bModel.add_opentime(one)
            if ret[0]:
                open_id.append(str(ret[1]))
            else:
                Log.error("营业时间添加失败") 
        db['business']['opentime'] = ','.join(open_id)
        self._bModel.delete_opentime(oldOids)
        '''
        oldImages = self._bModel.get_business_image(bid)
        for oImg in oldImages:
            self._imageModel.add_tmp(oImg['uuid'])
        self._bModel.delete_business_image(bid)
        images = db['image']
        for one in images:
            image=list(one)
            image.append(bid)
            tmp = self._bModel.add_business_image(image)
            if tmp[0]: 
                self._imageModel.del_tmp(image[0])
        
        ret = False
        b_ret = self._bModel.edit(db['business'],bid)
        if b_ret[0]:
            Log.debug(Log_Msg.BUSINESS_EDIT_SUC)
            db['rest']['business_id'] = bid
            s_ret = self._rModel.mod(db['rest'])
            if s_ret:
                Log.debug(Log_Msg.SHOP_EDIT_SUC)
                ret = True
            else:
                Log.error(Log_Msg.SHOP_EDIT_FAILED)
                ret = False
        else:
            Log.error(Log_Msg.BUSINESS_EDIT_FAILED)
        
        return ret
    
