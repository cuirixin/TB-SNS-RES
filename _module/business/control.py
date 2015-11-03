#!/usr/bin/env python2.7
#-*- coding:utf8 -*-
#
# 2013-12-4 by Victor
# Copyright 2013 Tubban
from base64 import b16encode, b16decode
from _module import const
from _module._lib.common import Common
from _module._lib.lang import Lang
from _module.business.model import BusinessModel
from _module.claim.model import ClaimModel
from _module.discover.model import DiscoverModel
from _module.dish.model import DishModel
from _module.friend.model import FriendModel
from _module.image.model import ImageModel
from _module.push.control import PushControl
from _module.restaurant.model import RestaurantModel
from _module.sys_data.model import SysdataModel
from _module.user.control import UserControl
from _module.user.model import UserModel

class BusinessControl:
    def __init__(self, uid = None,userLang=None):
        self._uid = uid
        self._bModel = BusinessModel(self._uid)
        self._cModel = ClaimModel(self._uid)
        self._rModel = RestaurantModel(self._uid)
        self._dModel = DishModel(self._uid)
        self._iModel = ImageModel(self._uid)
        self._fModel = FriendModel(self._uid)
        self._uModel = UserModel()
        self._iModel = ImageModel(self._uid)
        self._dcModel = DiscoverModel(self._uid)
        self._sysDataModel = SysdataModel()
        self._field = Lang.get_db_field_name(userLang)
        
    """
    Func: 获取城市区域数据，二维
    """
    def get_districts_by_city(self, city_id):
        sys_districts = self._sysDataModel.get_all_business_district_type(self._field)
        districts = []
        districts.append({"type": {"id": -2, "name": "城市热门 "}, "list": self._bModel.get_hot_districts(city_id=city_id, limit=10)})
        for one in sys_districts:
            #list = self._bModel.get_districts(city_id, one['id'])
            list = self._bModel.get_districts_ok(city_id, one['id'])
            if len(list) > 0:
                districts.append({"type": one, "list": list})
        return districts
            
    """
    Func: 内部方法，按距离排序，解决MongoDB计算时距离的误差导致显示时没有严格按距离单调排序
    """  
    def _sort_by_distance(self, lat, lon, list):
        for l in list:
            l['distance'] = Common.get_distance(lat, lon, l['lat'], l['lon'])
        if len(list)>0:
            list = sorted(list, key=lambda l : l['distance'])
        return list
        
    """
    Func: 以经纬度点位中心，前limit数目的的business列表 (不再使用，请使用POI模块的相应方法)
    """
    def get_near_list_by_dot(self, lat, lon, type=const.Business.CATEGORY_RESTAURANT, limit=50):
        if lat is None or lon is None:
            return []
        list = self._bModel.get_near_list_by_dot(lat, lon, type, limit)
        if len(list) == 0:
            list = self._bModel.get_most_populars(type, limit)
        return self._sort_by_distance(lat, lon, list)
    
    """
    Func: 根据条件查询，city、cusine (建议不再使用)
    """
    def search_by_condition(self, condition, category=const.Business.CATEGORY_RESTAURANT):
        list = self._bModel.get_list_by_condition(condition, category=const.Business.CATEGORY_RESTAURANT)
        if condition['lat'] is not None and condition['lon'] is not None:
            return self._sort_by_distance(condition['lat'], condition['lon'], list)
        return list
    
    """
    Func: 矩形区域内，business列表  (建议不再使用)
    """
    def get_near_list_by_rectangle(self, ne_lat, ne_lon, sw_lat, sw_lon, type=None, lat=None, lon=None):
        list = self._bModel.get_near_list_by_rectangle(
            float(ne_lat), float(ne_lon), float(sw_lat), float(sw_lon), type)
        if lat is not None and lon is not None:
            return self._sort_by_distance(lat, lon, list)
        return list
    
    def get_by_id(self, id):
        return self._bModel.get_by_id(id)
    
    def get_brief_by_id(self, id):
        return self._bModel.get_brief_by_id(id)
    
    def get_by_uuid(self,uuid):
        business = self._bModel.get_by_uuid(uuid)
        return business
    
    def get_bid_by_uuid(self,uuid):
        bid = self._bModel.get_id_by_uuid(uuid)
        return bid
    
    def get_uuid_by_bid(self,bid):
        uuid = self._bModel.get_uuid_by_bid(bid)
        return uuid
    
    def like(self, bid, category, uid):
        return self._bModel.add_like(bid, category, uid)
    
    def del_like(self, uid, bid):
        return self._bModel.del_like(uid, bid)
    
    def link_relations(self, list, uid=None):
        for one in list:
            one['has_like'] = 0
            if uid and one.has_key('id') and self._bModel.has_like(one['id'], uid):
                one['has_like'] = 1
        return list
    
    def wantgo(self, bid, category, uid):
        return self._bModel.add_wantgo(bid, category, uid)
    
    def wantsee(self, bid):
        return self._bModel.add_wantsee(bid)
    
    def get_brief_business_image(self, bid):
        return self._bModel.get_brief_business_image(bid)
    
    def get_business_image(self,bid):
        images = self._bModel.get_business_image(bid)
        return images
    
    def get_business_ugc_image(self,bid):
        images = self._bModel.get_business_ugc_image(bid)
        return images
    
    def add_business_ugc_image(self,image):
        ret = self._bModel.add_business_ugc_image(image)
        if ret[1]:
            self._iModel.del_tmp(image[0])
        return ret
    
    def get_business_ugc_image_by_uuid(self, uuid):
        return self._bModel.get_business_ugc_image_by_uuid(uuid)
        
    def delete_business_ugc_image(self, uuid):
        return self._bModel.delete_business_ugc_image(uuid)
    
    def ugc_image_like(self, uuid, uid=None):
        return self._bModel.ugc_image_like(uuid, uid)
    
    def get_ugc_image_list_by_user(self, uid):
        return self._bModel.get_ugc_image_list_by_user(uid)
    
    def mod(self, business):
        return self._bModel.mod(business)
    
    def get_pager_list_of_city(self, pager, city):
        return self._bModel.get_pager_list_of_city(pager, city)
    
    def get_has_menu_pager_list(self, pager, city_id=None):
        return  self._bModel.get_pager_list_of_city(pager, city_id)
    
    
    def get_like_user_pager_list(self, pager, business_id):
        ret = self._bModel.get_like_user_pager_list(pager, business_id)
        list = ret['data']
        #print list
        for u in list:
            if self._uid and u['id'] and self._fModel.is_friend(self._uid, u['id']):
                u['is_friend'] = 1
            else:
                u['is_friend'] = 0
        
        _ret = {}
        _ret['total'] = ret['total']
        _ret['data'] = list
        return _ret
    
    def get_liked_user_pager_list(self, pager, uid):
        ret = self._bModel.get_liked_pager_list_by_user(pager, uid)
        for one in ret['data']:
            one['currency'] = self._sysDataModel.get_currency(one["currency_id"], self._field)
            one['style_tags'] = []
            if one['category'] == const.Business.CATEGORY_RESTAURANT:
                restaurant = self._rModel.get_by_fields(one['id'], ["cuisine_style"])
                if restaurant:
                    one['style_tags'] = self._sysDataModel.get_cuisine_style(restaurant['cuisine_style'], self._field)
                
        return ret
    
    def get_all_business_by_user(self, owner):
        return self._bModel.get_all_business(owner)
    
    def get_signed_contract_pager_list(self, pager):
        data = self._bModel.get_signed_contract_pager_list(pager)
        for one in data['data']:
            one['country'] = self._sysDataModel.get_country(one['country_id'], self._field)
            if one['city_id'] <> 0:
                one['city'] = self._sysDataModel.get_city(one['city_id'], self._field)
            else:
                one['city'] = {"id": 0, "name": "Unkonw"}
        return data

    ###############################################

    ###
    # business 数据级别 （ＵＧＣ）
    ###
    
    def get_business_transportation(self,tids):
        transport = self._bModel.get_transportation(tids)
        return transport
    
    def get_brief_detail_by_uuid(self, uuid):
        business = self.get_by_uuid(uuid)
        business['currency'] = self._sysDataModel.get_currency(business['currency_id'], self._field)
        business['country'] = self._sysDataModel.get_country_name(business['country_id'])
        business['servicelanguage'] = self._sysDataModel.get_servicelanguage(business['servicelanguage'])
        business['paymenttool'] = self._sysDataModel.get_paymenttool(business['paymenttool'])
        business['city_name'] = self._sysDataModel.get_city_name(business['city_id'])
        
        return business
    
    def get_detail_by_uuid_for_custormer(self, uuid):
        business_fields = ['id', 'uuid', 'category', 'name', 'name_cn', 'cover', 'score', 'lat', 'lon', 'city_id', 'country_id',\
                           'currency_id', 'address', 'phone', 'description', 'description_cn', \
                           'cover', 'price_avg', 'servicelanguage', 'paymenttool', 'menu_num', 'meal_num', 'comment_num', 'subcategory_id']
        business = self._bModel.get_by_fields_uuid(uuid, business_fields)
        if not business:
            return None
        # TODO 关闭暂时不需要的数据
        #business['currency'] = self._sysDataModel.get_currency(business['currency_id'], self._field)
        #business['country'] = self._sysDataModel.get_country(business['country_id'], self._field)
        #business['city'] = {}
        #if business['city_id'] <> 0:
        #    business['city'] = self._sysDataModel.get_city(business['city_id'], self._field)
        
        #business['servicelanguage'] = self._sysDataModel.get_servicelanguage(business['servicelanguage'])
        #business['paymenttool'] = self._sysDataModel.get_paymenttool(business['paymenttool'])
        business['image'] = self.get_brief_business_image(business['id'])
        #business['subcategory'] = self._sysDataModel.get_rsubcategory(business['subcategory_id'])
        
        return business
    
    """
    business 实体数据信息。
    
    """
    def get_detail_by_uuid(self,uuid):
        business = self.get_by_uuid(uuid)
        if not business:
            return None
        business['currency'] = self._sysDataModel.get_currency(business['currency_id'], self._field)
        business['country'] = self._sysDataModel.get_country_name(business['country_id'], self._field)
        #business['closeday'] = self.get_closeday_names(business['closeday'], self._field)
        #business['transportation']=[]
        #business['opentime'] = self.get_business_opentime(business['opentime'])
        business['servicelanguage'] = self._sysDataModel.get_servicelanguage(business['servicelanguage'], self._field)
        business['paymenttool'] = self._sysDataModel.get_paymenttool(business['paymenttool'], self._field)
        business['image'] = self.get_business_image(business['id'])
        business['image_ugc'] = [] #self.get_business_ugc_image(business['id'])
        
        return business

    def get_all_business(self,uid):
        return self._bModel.get_all_business(uid)

    """
    # 收藏
    """
    def collect(self, uid, business_id, category):
        data = {'uid':uid, 'business_id':business_id, 
                'category': category,
                'add_time':Common.get_current_time()}
        return self._bModel.add_collect(data)
    
    def del_collect(self, uid, business_id):
        return self._bModel.del_collect(uid, business_id)
    
    def get_collect_list(self, uid):
        return self._bModel.get_collect_list(uid)
    
    # 获取假期时间
    def get_closedays(self, business_id):
        days = self._bModel.get_closedays(business_id)
        for day in days:
            day['from_time'] = Common.seconds_to_str(day['from_time'], const.Date_Format.DATE)
            day['to_time'] = Common.seconds_to_str(day['to_time'], const.Date_Format.DATE)
        return days
    
    # 获取营业时间
    def get_opendays(self, business_id):
        days = self._bModel.get_opendays(business_id)
        for day in days:
            for time in day['times']:
                time['from_time'] = Common.sec_to_cur_daytime_str(time['from_time'])
                time['to_time'] = Common.sec_to_cur_daytime_str(time['to_time'])
        return days
    
    # 获取营业时间
    def get_opendays_api(self, business_id):
        days = self._bModel.get_opendays(business_id)
        return days
    
    def get_business_owner(self,uuid):
        return self._bModel.get_business_owner(uuid)
    
    def search(self, key, category=const.Business.CATEGORY_RESTAURANT, skeys=['name','name_cn']):
        list = self._bModel.search(key, category, skeys)
        return list
    
    def delete_image(self, business_id, images, cover_relate=False):
        for one in images:
            self._bModel.delete_business_image_by_uuid(one)
        if cover_relate:
            business = {'business_id':business_id, 'cover':''}
            self._bModel.mod(business)
        return True
    
    def delete_image_by_type(self, uuid, is_ugc):
        if is_ugc == 1:
            discover = self._dcModel.get_by_uuid(uuid)
            if discover:
                self._dcModel.change_status(discover['id'], const.Discover.STATUS_DELETE)
            return self._iModel.delete_business_ugc_image(uuid)
        else:
            return self._iModel.delete_business_image(uuid)
        
    # 修改假期时间
    def mod_closedays(self, business_id, days):
        self._bModel.clear_closedays(business_id)
        return self._bModel.add_closedays(days)
    
    # 修改营业时间
    def mod_opendays(self, business_id, days):
        self._bModel.clear_opendays(business_id)
        return self._bModel.add_opendays(days)
            
    # 通过认领
    def claim_agree(self, id):
        claim = self._cModel.get_by_id(id)
        
        business = self.get_brief_by_id(claim['business_id'])
        # 通过审核
        uid = claim['uid']
        fields = ["id", "username", "sex", "email", "nike", "creator"]
        user = self._uModel.get_brief_user_by_id(uid, fields)
        if not user:
            if claim['email'].strip() == '':
                return False
            email_user = self._uModel.get_by_email(claim['email'], fields)
            if email_user:
                user = email_user
            if not user:
                # 创建用户并绑定
                user = {}
                user['username'] = self._uModel.gen_username()
                user['email'] = claim['email']
                #user['mobile'] = claim['mobile'] 此处mobile不保存，如果需要保存，应该排重
                #user['mobile_code'] = claim['mobile_code']
                user['nike'] = b16encode(Common.generate_short_uuid(6))
                user['password'] = Common._md5(user['nike'])
                user['group_id'] = const.User.GROUP_ADMIN
                ret = UserControl().add(user)
                if not ret[0]:
                    return False
                uid = ret[1]
                user['id'] = uid
                user['creator'] = uid
                
                # print 

        _business = {'business_id':claim['business_id'], 'owner': user['creator'], 'status':const.Business.STATUS_VALID}
        ret = self._bModel.mod(_business)
        if not ret:
            return False
        
        # 触发发送消息状态
        # MessageQueueModel().update_queue_status_by_uid(uid, const.MessageQueue.STATUS_UNSEND)
        print "Send Email "
        email_data = {
            "email": user['email'],
            "password": b16decode(user['nike']),
            "business_name": business['name'],
            "business_address": business['address']
        }
        msg = {
          "type": const.PUSH.TYPE_EMAIL,
          "code": const.PUSH.CODE_CLAIM_SUCCESS,
          "receiver": 0,
          "content": email_data,
          "extra": "{}"
        }
        PushControl().push_one(msg)
        
        # 屏蔽其他认领记录并更新当前记录状态
        self._cModel.change_status_by_bid(claim['business_id'], const.Claim.STATUS_REJECT)
        self._cModel.mod(id, {"status": const.Claim.STATUS_AGREE, "uid": user['id']})
        return True
    
    def _del_user(self, uid):
        user = self._uModel.get_by_id(uid)
        if user:
            if user['source']==const.User.SOURCE_CLAIM and user['status']==const.User.STATUS_UNVERIFY:
                print "Delete User %d" % int(uid)
                return self._uModel.delete_by_id(uid)
        return True
    
    # 拒绝认领
    def claim_reject(self, id):
        ret = self._cModel.mod(id, {"status": const.Claim.STATUS_REJECT})
        if not ret:
            return False
        return True 
                
    def get_pager_list(self, pager, status=None, key=None, has_menu = None, has_meal = None, city_id=None):
        wsql = ' 1=1 '
        if has_menu is not None:
            if has_menu == 0:
                wsql += 'AND menu_num=0 ' 
            if has_menu == 1:
                wsql += 'AND menu_num>0 ' 
        if has_meal is not None:
            if has_meal == 0:
                wsql += 'AND meal_num=0 ' 
            if has_meal == 1:
                wsql += 'AND meal_num>0 ' 
        if city_id is not None and city_id <> -1:
            wsql += 'AND city_id=%d ' % city_id
        
        return self._bModel.get_pager_list(pager, status, key, wsql)
    
    
    def get_unlocate_by_index(self, index):
        return self._bModel.get_unlocate_by_index(index)
    
    # ------------------------- Op ----------------------
    
    def get_uploadmenu_list(self):
        return self._bModel.get_uploadmenu_list()
    
    
    def ugc_agree(self, business_id):
        business = {"business_id":business_id, "status":const.Business.STATUS_UNCLAIMED}
        return self._bModel.mod(business)
    
    def ugc_reject(self, business_id):
        business = {"business_id":business_id, "status":const.Business.STATUS_DELETE}
        return self._bModel.mod(business)
    
    def get_album_pager_list(self, pager, type, key=None):
        
        if type == 1:
            pager = self._bModel.get_no_cover_but_has_image_pager_list(pager)
        else:
            pager = self._bModel.get_pager_list(pager, None, key, None)
        _list = pager['data']
        for one in _list:
            one['images'] = self._get_business_images(one['id'], one['uuid'])
        pager['data'] = _list
        return pager
    
    def get_business_ugc_image_pager_list(self, pager, status):
        return self._bModel.get_business_ugc_image_pager_list(pager, status)
    
    def _get_business_images(self, bid, buuid):
        images = self.get_business_image(bid)
        for o in images:
            o['is_ugc'] = 0
        _images = self.get_business_ugc_image(bid)
        for o in _images:
            o['is_ugc'] = 1
            images.append(o)
        return images
    
    def set_ugc_images_ok(self, uuids):
        if uuids == '':
            return True
        return self._bModel.change_ugc_images_verified(uuids, 1)
    