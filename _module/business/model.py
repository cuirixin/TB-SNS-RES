#!/usr/bin/env python2.7
#-*- coding:utf8 -*-
#
# 2013-12-4 by Victor
# Copyright 2013 Tubban
from _module import const
from _module._lib.mgdb import MgDB
from _module._base_m_ import BaseModel
from _module._lib.common import Common
from _module.uuid.model import UUIDModel

class BusinessModel(BaseModel):
    
    def __init__(self, uid = None):
        self._business_table = 'business'
        self._transportation_table = "b_transportation"
        self._opentime_table = "b_opentime"
        self._image_table = "b_image"
        self._image_ugc_table = "b_image_ugc"
        self._price_table = "price"
        self._collect_table = 'b_collect'
        self._search_poi_table = 'business_search'
        self._wango_table = 'b_wantgo'
        self._carte_source = 'r_carte_source'
        self._business_district = 'business_district'
        
        self._openday_table = 'b_openday'
        self._openday_time_table = 'b_openday_time'
        self._closeday_table = 'b_closeday'
        self._discover_table = 'discover'
        self._weekday_table = 'sys_weekday'
        self._user_table = 'auth_user'
        self._uid = uid
        
    def get_all_districts_by_city(self, city_id):
        sql = "SELECT type_id, name, name_cn, lon, lat, r_num, `hot` FROM %s WHERE city_id=%d order by type_id asc" % \
                (self._business_district, city_id)
        return self.get_rows(sql)
    
    
    def get_districts(self, city_id, district_type_id):
        sql = "SELECT id, type_id, name, name_cn, lon, lat, r_num, `hot` FROM %s WHERE city_id=%d and type_id=%d" % \
                (self._business_district, city_id, district_type_id)
        return self.get_rows(sql)
    
    def get_districts_ok(self, city_id, district_type_id):
        sql = "SELECT id, type_id, name, name_cn, lon, lat, r_num, `hot` FROM %s WHERE city_id=%d and type_id=%d and `r_num`>0 " % \
                (self._business_district, city_id, district_type_id)
        return self.get_rows(sql)
    
    
    def get_hot_districts(self, city_id, limit=10):
        sql = "SELECT id, type_id, name, name_cn, lon, lat, r_num, `hot` FROM %s WHERE city_id=%d order by hot desc limit %d" % \
                (self._business_district, city_id, limit)
        return self.get_rows(sql)
    
    def get_by_fields(self, id, business_fields):
        select_str = self._gen_fields_str(business_fields)
        sql = "SELECT %s FROM %s WHERE `id`=%d" % (select_str, self._business_table,id)
        return self.get_one(sql)
    
    def get_by_fields_uuid(self, uuid, business_fields):
        select_str = self._gen_fields_str(business_fields)
        sql = "SELECT %s FROM %s WHERE `uuid`='%s'" % (select_str, self._business_table, uuid)
        return self.get_one(sql)
        
    """ business """
    def get_by_id(self, id):
        sql = "SELECT * FROM %s WHERE `id`=%d" % (self._business_table,id)
        return self.get_one(sql)
    
    def get_brief_by_id(self, id):
        sql = "SELECT id, uuid, mobile, name, name_cn, status, phone, score, lat, " \
            " lon, description, address, zip, category,cover, owner, country_id, city_id, currency_id, " \
            " like_num, wantgo_num, collect_num, menu_num, meal_num FROM %s WHERE `id`=%d" % (self._business_table,id)
        return self.get_one(sql)
    
    def get_bid_by_uuid(self,uuid):
        if uuid.strip() == '':
            return 0
        sql = "SELECT id FROM %s WHERE `uuid`='%s' limit 1;" \
                % (self._business_table,uuid)
        return self.get_one(sql).id
    
    def get_by_uuid(self, uuid):
        if uuid.strip() == '':
            return None
        sql = "SELECT * FROM %s WHERE  `uuid`='%s' limit 1" \
                % (self._business_table,uuid)
        return self.get_one(sql)
        
    NEAR_DISTANCE = (500, 1000, 2000, 3000, 5000, 10000, 20000)
    def get_near_list_by_dot(self, lat, lon, category=const.Business.CATEGORY_RESTAURANT, limit=50):
        if limit>200:
            return []
        rows = set()
        m = len(self.NEAR_DISTANCE)
        n = 0
        if self._uid is None:
            self._uid = 0
        while len(rows) <= limit:
            flag = False
            sql = "CALL search_near_business(%s,%s,%s,%s,%s)" % (str(lat),
                        str(lon), str(self.NEAR_DISTANCE[n]), str(self._uid), str(category))
            r = self.get_rows(sql)
            for o in r:
                rows.add(str(o['id']))
                if len(rows)>=limit:
                    flag = True
                    break
            if flag:
                break
            n = n + 1
            if n >= m:
                break
        
        if len(rows)==0:
            return []
        
        ids = ','.join(list(rows))
        
        sql="SELECT id, uuid, mobile, name, name_cn, status, phone, score, lat, " \
            " lon, description, address, category,cover, owner, country_id, city_id, currency_id, " \
            " like_num, wantgo_num, collect_num, menu_num, meal_num " \
            " FROM %s " \
            " WHERE `status`>%s AND `id` in (%s) " \
            % (self._business_table, const.Business.STATUS_DELETE, ids)
            
        if category is not None:
            sql += " AND `category`=%s " % category
        _list = self.get_rows(sql)
        for l in _list:
            if l['category']==const.Business.CATEGORY_HOTEL:
                l['category_name'] = 'hotel'
            elif l['category']==const.Business.CATEGORY_RESTAURANT:
                l['category_name'] = 'restaurant'
            elif l['category']==const.Business.CATEGORY_SHOP:
                l['category_name'] = 'shop' 
        return _list
    
    def get_list_by_condition(self, condition, category=const.Business.CATEGORY_RESTAURANT):
        
        where_sql = " b.id=r.id AND b.`status`>%d AND b.`category`=%s AND b.`menu_num`>0" % (const.Business.STATUS_DELETE, category)
        if condition.has_key('city') and condition['city'] <> 0:
            where_sql += "  AND b.city_id=%d " % condition['city']
            
        if condition.has_key('last_id') and condition['last_id'] <> 0:
            where_sql += " AND b.id>%d " % condition['last_id']
            
        if condition.has_key('cuisine') and condition['cuisine'] <> '':
            condition['cuisine'] = Common.filter_comma_ids(condition['cuisine']).split(",")
            where_sql += " AND ( 1!=1 "
            for o in condition['cuisine']:
                where_sql += " OR r.cuisine_style like '%%%%%s%%%%' " % (','+o+',')
            where_sql += " ) "
        if category == const.Business.CATEGORY_RESTAURANT:
            sql="SELECT b.id, b.uuid, b.mobile, b.name, b.name_cn, b.status, b.phone, b.score, b.lat, " \
                " b.lon, b.description, b.address, b.category, b.cover, b.owner, b.country_id, b.currency_id, " \
                " b.like_num, b.wantgo_num, b.collect_num, b.menu_num, b.meal_num, b.city_id " \
                " FROM %s b, %s r" \
                " WHERE %s" \
                % (self._business_table, "restaurant", where_sql)
            sql +=  " limit %d" % condition['limit']
            _list = self.get_rows(sql)
        return _list
    
    def get_most_populars(self, category=const.Business.CATEGORY_RESTAURANT, limit=50):
        sql="SELECT id, uuid, mobile, name, name_cn, status, phone, score, lat, " \
            " lon, description, address, category,cover, owner, country_id, currency_id, " \
            " like_num, wantgo_num, collect_num, menu_num, meal_num, city_id " \
            " FROM %s " \
            " WHERE `status`!=%s  AND `menu_num`>0" \
            % (self._business_table, const.Business.STATUS_DELETE)
                        
        if category is not None:
            sql += " AND `category`=%s " % category
        sql +=  " ORDER BY like_num desc limit %d" % limit
        _list = self.get_rows(sql)
        return _list
    
    def get_near_list_by_rectangle(self, ne_lat, ne_lon, sw_lat, sw_lon,category=None):
        sql="SELECT id, uuid, mobile, status,name, name_cn, phone, score, lat, " \
            " lon, description, address, category,cover, owner, country_id, currency_id, " \
            " like_num, wantgo_num, collect_num, menu_num, meal_num" \
            " FROM %s " \
            " WHERE `status`!=%s  AND (lat>='%s' and lat<='%s' and lon>='%s' and lon<='%s')" \
            % (self._business_table, const.Business.STATUS_DELETE, str(sw_lat), str(ne_lat), str(sw_lon), str(ne_lon))
        if category is not None:
            sql += " AND `category`=%s " % category
        sql += " limit 200"
        list = self.get_rows(sql)
        for l in list:
            if l['category']==const.Business.CATEGORY_HOTEL:
                l['category_name'] = 'hotel'
            elif l['category']==const.Business.CATEGORY_RESTAURANT:
                l['category_name'] = 'restaurant'
            elif l['category']==const.Business.CATEGORY_SHOP:
                l['category_name'] = 'shop' 
        return list
    
    def has_like(self, bid, uid):
        like_table = self._get_mo_split_table(bid, "b_like", const.DB.B_LIKE_SPLIT)
        like_user_table = self._get_mo_split_table(uid, "b_like_user", const.DB.B_LIKE_USER_SPLIT)
        if bid is None or uid is None:
            return False
        sql1 = "SELECT count(1) as total FROM %s WHERE business_id=%d AND uid=%d" % (like_table, int(bid), int(uid))
        sql2 = "SELECT count(1) as total FROM %s WHERE business_id=%d AND uid=%d" % (like_user_table, int(bid), int(uid))
        if self.get_one(sql1)['total'] == 0 or self.get_one(sql2)['total'] == 0:
            return False
        if self.get_one_by_slave(sql1)['total'] == 0:
            return False
        return True
    
    def has_wantgo(self, bid, uid):
        if bid is None or uid is None:
            return False
        sql = "SELECT count(*) as total FROM %s WHERE business_id=%d AND uid=%d" % (self._wango_table, int(bid), int(uid))
        if self.get_one(sql)['total'] == 0:
            return False
        return True
    
    
    def add_like(self, bid, category, uid=None):
        if self.has_like(bid, uid):
            return True
        if uid:
            like_user_table = self._get_mo_split_table(uid, "b_like_user", const.DB.B_LIKE_USER_SPLIT)
            sql_relation = "REPLACE INTO %s(`uid`,`business_id`,`category`,`add_time`) VALUES(%d,%d,%d,%d)" % \
                            (like_user_table, uid, bid, category, Common.get_current_time())
            print sql_relation
            ret  = self.execute(sql_relation)[0]
            if not ret:
                return False
            like_table = self._get_mo_split_table(bid, "b_like", const.DB.B_LIKE_SPLIT)
            sql_relation = "REPLACE INTO %s(`uid`,`business_id`,`category`,`add_time`) VALUES(%d,%d,%d,%d)" % \
                            (like_table, uid, bid, category, Common.get_current_time())
            print sql_relation
            ret = self.execute(sql_relation)[0]
            if not ret:
                return False
            
        sql = "UPDATE  %s SET like_num=like_num+1, last_update=%d WHERE id=%d" % (self._business_table, Common.get_current_time(), int(bid))
        return self.execute(sql)[0]
    
    def del_like(self, uid, bid):
        like_user_table = self._get_mo_split_table(uid, "b_like_user", const.DB.B_LIKE_USER_SPLIT)
        sql_relation = "DELETE FROM  %s WHERE `uid`=%d and `business_id`=%d LIMIT 1" % \
                            (like_user_table, uid, bid)
        self.execute(sql_relation)
        like_table = self._get_mo_split_table(bid, "b_like", const.DB.B_LIKE_SPLIT)
        sql_relation = "DELETE FROM  %s WHERE `uid`=%d and `business_id`=%d LIMIT 1" % \
                            (like_table, uid, bid)
        self.execute(sql_relation)
        sql = "UPDATE %s SET like_num=like_num-1, last_update=%d WHERE id=%d" % (self._business_table, Common.get_current_time(), int(bid))
        self.execute(sql)
        return True
    
    def add_wantgo(self, bid, category, uid=None):
        sql_c = "SELECT uid FROM %s WHERE business_id=%d AND uid=%d" % (self._wango_table, bid, uid)
        if self.get_one(sql_c):
            return True
        sql = "UPDATE  %s SET wantgo_num=wantgo_num+1 WHERE id=%d" % (self._business_table, int(bid))
        ret = self.execute(sql)[0]
        if not ret:
            return False
        if uid:
            sql_relation = "INSERT INTO %s(`uid`,`business_id`,`category`,`add_time`) VALUES(%d,%d,%d,%d)" % \
                        (self._wango_table, uid, bid, category, Common.get_current_time())
            return self.execute(sql_relation)[0]
        return True
    
    def add_wantsee(self, bid):
        sql = "UPDATE  %s SET wantsee_num=wantsee_num+1 WHERE id=%d" % (self._business_table, int(bid))
        ret = self.execute(sql)[0]
        if not ret:
            return False
        return True
    
    
    
    def get_pager_list_of_city(self, pager, city_id=None, wheresql = None):
        size = pager['ps']
        offset = size*(pager['p']-1)
        
        where_sql = " WHERE status>%d  AND `description_cn`!='' " % const.Business.STATUS_DELETE
        
        if city_id is not None and city_id<>0:
            where_sql = where_sql+" AND city_id= %d" % city_id
                
        if wheresql <> None:
            where_sql = where_sql+ " AND " + wheresql
            
        count_sql = "SELECT count(1) as total FROM %s b " % self._business_table + where_sql
        count =  self.get_one(count_sql)['total']
        if count<>0:
            fields = ['id', 'uuid', 'name', 'name_cn', 'address', 'city_id', 'phone', 'cover', 'score_it', 'currency_id', 'description_cn', 'lat', 'lon', 'price_avg', 'score', 'servicelanguage']
            fields_str = self._gen_fields_str(fields, 'b')
            se_sql = "SELECT %s FROM %s b " \
                        " %s " \
                        " order by b.score_it desc" \
                        " limit %s,%s"  \
            % (fields_str, self._business_table, where_sql, offset, size)
            rows = self.get_rows(se_sql)
            return dict(total=count, data=rows)
        else:
            return dict(total=0, data=[])
        
    
    """图片"""
    
    def get_brief_business_image(self, bid):
        sql = "SELECT id, uuid FROM %s WHERE business_id=%s and status>%d" % (self._image_table,bid, const.Image.STATUS_DELETE)
        return self.get_rows_by_slave(sql)
        
    def get_business_image(self,bid):
        sql = "SELECT * FROM %s WHERE business_id=%s and status>%d" % (self._image_table,bid, const.Image.STATUS_DELETE)
        return self.get_rows_by_slave(sql)

    def add_business_image(self,image):
        sql = "INSERT INTO %s(`uuid`,`title`,`description`,`business_id`) " \
                " values('%s','%s','%s',%s) " \
                % (self._image_table,image[0],'','',image[3],)
        return self.execute(sql)
    
    
    def add_image(self, fields):
        image = {
            'uuid': {'type':'s', 'required':1},
            'business_id': {'type':'d', 'required':1},
            'title': {'type':'s', 'default':''},
            'description': {'type':'s', 'default':''},
            'source_type': {'type':'d', 'default':const.Common.SOURCE_TYPE_CUSTOM},
        }
        
        ret = self._args_handle('insert', fields, image)               
        if not ret[0]:
            # todo:
            return ret
        return self._insert(self._image_table, image)
    
    def get_business_ugc_image(self,bid):
        sql = "SELECT * FROM %s WHERE business_id=%s and status>%d" % (self._image_ugc_table, bid, const.Image.STATUS_DELETE)
        return self.get_rows(sql)
    
    def add_business_ugc_image(self,image):
        sql = "INSERT INTO %s(`uuid`,`title`,`description`,`business_id`,`uid`,`username`,add_time) " \
                " values('%s','%s','%s',%s,%s,'%s',%s) " \
                % (self._image_ugc_table,image[0],self.escape_string(image[1]),self.escape_string(image[2]),image[3],image[4],self.escape_string(image[5]), Common.get_current_time())
        return self.execute(sql)
    
    def get_business_ugc_image_by_uuid(self, uuid):
        sql = "SELECT * FROM %s WHERE uuid='%s' limit 1" % (self._image_ugc_table, uuid)
        return self.get_one(sql)
    
    def delete_business_ugc_image(self, uuid):
        sql = "UPDATE %s SET status=%d WHERE uuid='%s'" % (self._image_ugc_table, const.Image.STATUS_DELETE, uuid)
        ret =  self.execute(sql)[1]
        # 删除对应的discover
        sql = "UPDATE %s SET status=%d WHERE image_uuid='%s'" % (self._discover_table, const.Discover.STATUS_DELETE, uuid)
        self.execute(sql)
        return ret
    
    def ugc_image_like(self, uuid, uid = None):
        sql = "UPDATE %s SET like_num=like_num+1 WHERE uuid='%s'" % (self._image_ugc_table, uuid)
        ret =  self.execute(sql)[1]
        return ret
    
    def get_ugc_image_list_by_user(self, uid):
        sql = "SELECT i.*, b.name as business_name, b.uuid as business_uuid  FROM %s i " \
                " LEFT JOIN %s b on b.id=i.business_id " \
                " WHERE i.uid = %d and i.status>%d " \
                " order by i.add_time asc" % (self._image_ugc_table, self._business_table, uid, const.Image.STATUS_DELETE)
        return self.get_rows(sql)
    
    
    def get_collect_list(self, uid):
        return []
    
    
    def is_collected(self, uid, business_id):
        return False
    
    def del_collect(self, uid, business_id):
        return True

    def add_collect(self, data):
        return True
    
    
    def add(self, fields):
        
        business = {
            'name': {'type':'s', 'required':1},
            'description': {'type':'s', 'default':''},
            'description_cn' : {'type':'s', 'default':''},
            'category' : {'type':'d', 'default':const.Business.CATEGORY_RESTAURANT},
            'address' : {'type':'s', 'default':''},
            'zip' : {'type':'s', 'default':''},
            'city' : {'type':'s', 'default':''},
            'city_id' : {'type':'s', 'default':0},
            'country_id' : {'type':'d', 'default':0},
            'currency_id' : {'type':'d', 'default':1}, # 默认欧元
            'phone' : {'type':'s', 'default':''},
            'phone2' : {'type':'s', 'default':''},
            'email' : {'type':'s', 'default':''},
            'fax' : {'type':'s', 'default':''},
            'website' : {'type':'s', 'default':''},
            'state' : {'type':'s', 'default':''},
            'servicelanguage' : {'type':'s', 'default':''},
            'transportation' : {'type':'s', 'default':''},
            'closeday' : {'type':'s', 'default':''},
            'paymenttool' : {'type':'s', 'default':''},
            'last_update' : {'type':'d', 'default':Common.get_current_time()},
            'reg_language' : {'type':'s', 'default':''},
            'cover' : {'type':'s', 'default':''},
            'mobile' : {'type':'s', 'default':''},
            'source_type' : {'type':'d', 'default':0},
            'source_id' : {'type':'d', 'default':0},
            'status' : {'type':'d', 'default':const.Business.STATUS_NOT_VERIFIED},
            'owner' : {'type':'d', 'default':0},
            'lat' : {'type':'f', 'default':1.0},
            'lon' : {'type':'f', 'default':1.0},
            'extra' : {'type':'s', 'default':''},
            'hour' : {'type':'s', 'default':''},
        }
        
        ret = self._args_handle('insert', fields, business)   
        
        if not ret[0]:
            # todo:
            return ret
        ret = self._insert(self._business_table, business)
    
        if not ret[0]:
            return ret
        uuid = UUIDModel().get_uuid_by_id(ret[1])
        self.edit({'uuid':uuid}, ret[1])
        
        business = fields
        return [True, ret[1], uuid]
    
    def edit(self, business, bid):
        sql = "UPDATE %s SET " % self._business_table
        
        for key in business:
            sql += "%s=%%(%s)s," % (key,key)
        sql = sql[0:len(sql)-1] 
        sql += " WHERE id=%s" % bid
        
        ret = self.update(sql, **business)
        return ret
    
    # 位置搜索
    def add_search_poi(self, poi):
        client = MgDB.get_client()
        db = client.tubban
        pois_collection = db.business_pois
        pois_collection.insert(poi)
        return True
    
    
    """
    Func : 获取喜欢某个business的用户列表
    """
    def get_like_user_pager_list(self, pager, business_id):
        like_table = self._get_mo_split_table(business_id, "b_like", const.DB.B_LIKE_SPLIT)
    
        size = pager['ps']
        offset = size*(pager['p']-1)
        
        where_sql = ' WHERE a.business_id=%d ' % business_id
        count_sql = "SELECT count(*) as total FROM %s a " % like_table + where_sql
        count =  self.get_one(count_sql)['total']
        if count<>0:
            se_sql = "SELECT b.username, b.sex, b.id, b.mobile, b.mobile_code, b.icon, b.email" \
                        " FROM %s a " \
                        " LEFT JOIN %s b ON a.uid=b.id" \
                        " %s " \
                        " limit %s,%s"  \
            % (like_table, self._user_table, where_sql, offset, size)
            rows = self.get_rows_by_slave(se_sql)
            return dict(total=count, data=rows)
        else:
            return dict(total=0, data=[])
        
    """
    Func : 获取某人喜欢的business列表
    """
    def get_liked_pager_list_by_user(self, pager, uid, category=const.Business.CATEGORY_RESTAURANT):
        like_user_table = self._get_mo_split_table(uid, "b_like_user", const.DB.B_LIKE_USER_SPLIT)
    
        size = pager['ps']
        offset = size*(pager['p']-1)
        
        where_sql = ' WHERE a.uid=%d ' % uid
        count_sql = "SELECT count(1) as total FROM %s a " % like_user_table + where_sql
        count =  self.get_one(count_sql)['total']
        if count<>0:
            se_sql = "SELECT b.id, b.name, b.name_cn, b.phone, b.phone2, b.city, b.category, b.city_id, " \
                     " b.lat, b.lon, b.address, b.uuid, b.cover,b.country_id, b.currency_id, b.menu_num, b.comment_num, b.like_num, b.score, b.price_avg " \
                        " FROM %s a " \
                        " LEFT JOIN %s b ON a.business_id=b.id" \
                        " %s " \
                        " limit %s,%s"  \
            % (like_user_table, self._business_table, where_sql, offset, size)
            rows = self.get_rows_by_slave(se_sql)
            return dict(total=count, data=rows)
        else:
            return dict(total=0, data=[])
    
    def get_signed_contract_pager_list(self, pager):
        size = pager['ps']
        offset = size*(pager['p']-1)
        
        where_sql = ' WHERE signed_contract=1 '
        count_sql = "SELECT count(1) as total FROM %s " % self._business_table + where_sql
        count =  self.get_one(count_sql)['total']
        if count<>0:
            se_sql = "SELECT id, uuid, name, name_cn, phone, address, city_id, country_id, currency_id, lat, lon, state, city, owner, cover, meal_num, menu_num" \
                        " FROM %s " \
                        " %s " \
                        " limit %s,%s"  \
            % (self._business_table, where_sql, offset, size)
            rows = self.get_rows(se_sql)
            return dict(total=count, data=rows)
        else:
            return dict(total=0, data=[])
        
    ####################################
    # 以下均迁移到module/sys_data模块中
    def get_all_continents(self, field='EN'):
        sql = "SELECT id, %s as name FROM %s order by id asc" % (field, self._continent_table)
        return self.get_rows(sql)

    def get_all_weekdays(self, field='EN'):
        sql = "SELECT id, %s as name FROM %s order by id asc" % (field, self._weekday_table)
        return self.get_rows(sql)
    def get_weekday_by_id(self,wid, field='EN'):
        sql = "select %s as name FROM %s where id=%s" %(field, self._weekday_table,wid)
        return self.get_one(sql)['name']
    def get_closeday(self,ids,field='EN'):
        if ids is None or ids=='':
            return []
        sql = "SELECT %s as name FROM %s WHERE id IN (%s)" % (field, self._weekday_table,ids)
        return self.get_rows(sql)
    
    def get_closeday_names(self,ids,field='EN'):
        if ids is None or ids=='':
            return []
        sql = "SELECT %s as name FROM %s WHERE id IN (%s)" % (field, self._weekday_table,ids)
        return self.get_rows(sql)
    
    def get_all_paymenttool(self, field='EN'):
        _field = field
        if _field<>'CN' and _field<>'EN':
            _field = 'EN'
        sql = "SELECT id, icon, %s as name FROM %s order by id asc" % (_field, self._paymenttool_table)
        return self.get_rows(sql)
    
    def get_paymenttool(self,ids,field='EN'):
        if ids is None or ids=='':
            return []
        _field = field
        if _field<>'CN' and _field<>'EN':
            _field = 'EN'
        sql = "SELECT %s as name ,icon FROM %s WHERE id IN (%s)" \
                % (_field, self._paymenttool_table,ids)
        return self.get_rows(sql)
    
    def get_all_portionunit(self,field='EN'):
        sql = "SELECT id, %s as name FROM %s order by id asc" \
                % (field, self._portionunit)
        return self.get_rows(sql) 
    
    def get_portionunit_by_group(self, group,field='EN'):
        sql = "SELECT id, %s as name FROM %s WHERE `group`=%s or `group`=0 order by id asc" % (field, self._portionunit, group)
        return self.get_rows(sql) 
    
    def get_all_foodingredient(self,field='EN'):
        sql = "SELECT id, %s as name FROM %s order by id asc" \
                % (field, self._foodingredient_table)
        return self.get_rows(sql) 
    
    def get_all_cooktechnique(self,field='EN'):
        sql = "SELECT id, %s as name FROM %s order by id asc" \
                % (field, self._cooktechnique_table)
        return self.get_rows(sql) 
    
    def get_all_mouthfeel(self,field='EN'):
        sql = "SELECT id, %s as name FROM %s order by id asc" \
                % (field, self._mouthfeel_table)
        return self.get_rows(sql) 
    
    def get_all_foodtypes(self, field='EN'):
        sql = "SELECT id, %s as name FROM %s order by id asc" \
                % (field, self._foodtype_table)
        return self.get_rows(sql) 
    
    def get_all_languages(self, field='EN'):
        sql = "SELECT id, icon, %s as name FROM %s order by id asc" \
                % (field, self._language_table)
        return self.get_rows(sql)
    
    def get_servicelanguage(self,ids,field='EN'):
        if ids is None or ids=='':
            return []
        # TODO 暂时language支持四中语言
        if field not in ['EN', 'CN', 'FR', 'DE']:
            field= 'EN'
        sql = "SELECT %s as name FROM %s WHERE id IN (%s)" \
                % (field, self._language_table,ids)
        return self.get_rows(sql)
    
    def get_all_country(self, field='EN'):
        sql = "SELECT id, icon, %s as name, phone_code FROM %s order by id asc" \
                % (field, self._country_table)
        return self.get_rows(sql)
    
    def get_all_city(self, field='EN'):
        sql = "SELECT id, %s as name FROM %s order by id asc" \
                % (field, self._city_table)
        return self.get_rows(sql)
    
    def get_city_by_id(self, id, field='EN'):
        sql = "SELECT id, `%s` as name from %s where id=%d" % (field, self._city_table, id)
        return self.get_one(sql)
    
    def get_city_by_ids(self, ids, field='EN'):
        sql = "SELECT id, `%s` as name from %s where id in (%s)" % (field, self._city_table, ids)
        return self.get_rows(sql)
    
    def get_all_currency(self, field='EN'):
        _field = field
        if _field<>'CN' and _field<>'EN':
            _field = 'EN'
        sql = "SELECT id, icon, %s as name, iso_code FROM %s order by id asc" \
                % (_field, self._currency_table)
        return self.get_rows(sql)
    
    def get_currency(self, id, field='EN'):
        _field = field
        if _field<>'CN' and _field<>'EN':
            _field = 'EN'
        sql = "SELECT id, icon, %s as name, iso_code FROM %s WHERE id=%d" \
                % (_field, self._currency_table, id)
        return self.get_one(sql)
        
    
    def get_country_name(self,cid,field='EN'):
        sql = "SELECT  %s as name FROM %s WHERE id=%s" \
                % (field, self._country_table,int(cid))
        ret = self.get_one(sql)
        if ret:
            return ret.name
        else:
            return ''
        
    def get_city_name(self,cid,field='EN'):
        sql = "SELECT  %s as name FROM %s WHERE id=%s" \
                % (field, self._city_table, int(cid))
        ret = self.get_one(sql)
        if ret:
            return ret.name
        else:
            return ''
    
    #######################################################
    
    def _mod(self, args):
        business = {
            'name': {'type':'s'},
            'name_cn': {'type':'s'},
            'description': {'type':'s'},
            'description_cn' : {'type':'s'},
            'address' : {'type':'s'},
            'zip' : {'type':'s'},
            'city' : {'type':'s'},
            'city_id' : {'type':'d'},
            'country_id' : {'type':'d'},
            'currency_id' : {'type':'d'}, # 默认欧元
            'phone' : {'type':'s'},
            'phone2' : {'type':'s'},
            'email' : {'type':'s'},
            'fax' : {'type':'s'},
            'website' : {'type':'s'},
            'state' : {'type':'s'},
            'servicelanguage' : {'type':'s'},
            'transportation' : {'type':'s'},
            'closeday' : {'type':'s'},
            'paymenttool' : {'type':'s'},
            'reg_language' : {'type':'s'},
            'cover' : {'type':'s'},
            'mobile' : {'type':'s'},
            'status' : {'type':'d'},
            'collect_num' : {'type':'d'},
            'score_total' : {'type':'d'},
            'score_avg' : {'type':'f'},
            'price_num' : {'type':'d'},
            'price_total' : {'type':'d'},
            'price_avg' : {'type':'f'},
            'menu_num' : {'type':'d'},
            'meal_num' : {'type':'d'},
            'subcategory_id': {'type':'d'},
            
            'like_num' : {'type':'d'},
            'menu_version' : {'type':'d'},
            
            'owner' : {'type':'d'},
            'lat' : {'type':'f'},
            'lon' : {'type':'f'},
            'extra' : {'type':'s'},
            'hour' : {'type':'s'},
        }   
        if not args.has_key('business_id'):
            return False

        ret = self._args_handle('update', args, business)               
        if not ret[0]:
            return False
        
        if len(business) == 0:
            return True
        
        where = "id=%d" % (int(args['business_id']))
        business['last_update'] = {'type': 'd', 'value': Common.get_current_time()}
        ret = self._update(self._business_table, business, where)
        if not ret[0]:
            return False
        """
        args['id'] = int(args['business_id'])
        
        if args.has_key('lon'):
            args['coordinate'] = [args['lon'], args['lat']]
        self.update_search_poi(args['id'], args)
        """
        return True
    
    
    def mod(self, kwarg):
        return self._mod(kwarg)
    
    ####################################
    """ 交通   """
    def add_transportation(self,transportation):   
        sql = "INSERT INTO %s(station,route,distance) values ('%s','%s','%s');" \
                % (self._transportation_table,transportation[0],
                   str(transportation[1]),str(transportation[2]))
        return self.execute(sql)
    
    def get_transportation(self,tids):
        tids = Common.filter_comma_ids(tids)
        if not tids:
            return []
        sql = "SELECT * FROM %s WHERE id IN (%s);" % (self._transportation_table,tids)
        return self.get_rows(sql)  
    
    def delete_transportation(self,tids):
        tids = Common.filter_comma_ids(tids)
        if tids is None or tids=='':
            return []
        sql = "DELETE FROM %s WHERE id IN (%s);" %  (self._transportation_table,tids)
        return self.execute(sql)
      

    """营业时间"""
    
    def add_opentime(self,opentime):    
        sql = "INSERT INTO %s(from_time,to_time) values (%s,%s);" \
                % (self._opentime_table,opentime[0],opentime[1])
        return self.execute(sql)
    
    def get_opentime(self, timeids):  
        timeids = Common.filter_comma_ids(timeids)
        if not timeids:
            return []
        sql = "SELECT * FROM %s WHERE id IN (%s) order by `from_time`;" \
                % (self._opentime_table,timeids)
        return self.get_rows(sql) 
    
    def delete_opentime(self,otids):
        otids = Common.filter_comma_ids(otids)
        if len(otids)==0:
            return True
        sql = "DELETE FROM %s WHERE id IN (%s);" % (self._opentime_table,otids)
        return self.execute(sql)[0]
    
    
    def delete_business_image(self,bid):
        # images = self.get_business_image(bid)
        sql = "UPDATE %s set status=%d where business_id=%d" % (self._image_table, const.Image.STATUS_DELETE, int(bid))
        ret =  self.execute(sql)
        if not ret[0]:
            return False
        """
        for image in images:
            Common.remove_file(image['uuid'])
        """
        return True
    
    def delete_business_image_by_uuid(self, uuid):
        sql = "UPDATE %s set status=%d where uuid='%s'" % (self._image_table, const.Image.STATUS_DELETE, uuid)
        ret =  self.execute(sql)
        if not ret[0]:
            return False
        #Common.remove_file(uuid)
        return True
    
    def get_business_owner(self,uuid):
        sql = "SELECT owner FROM %s WHERE  `uuid`='%s';" % (self._business_table,uuid)
        ret = self.get_one(sql)
        if ret:
            return ret['owner']
        else:
            return -1
    
    def get_uuid_by_bid(self,bid):
        sql = "SELECT uuid FROM %s WHERE `id`=%s limit 1" % (self._business_table,bid)
        return self.get_one(sql).uuid
    
    def get_business_transporttation_by_bid(self,bid):
        sql = "SELECT  transportation FROM %s WHERE id=%s;" % (self._business_table,bid)
        transportation = self.get_one(sql)
        if transportation:
            return transportation.transportation
        else:
            return None
    
    def get_business_opentime_by_bid(self,bid):
        sql = "SELECT opentime FROM %s WHERE id=%s;" % (self._business_table,bid)
        opentime = self.get_one(sql)
        if opentime:
            return opentime.opentime
        else:
            return None
    
    def get_id_by_uuid(self,uuid):
        if uuid.strip() == '':
            return 0
        sql = "SELECT id FROM %s WHERE uuid='%s' limit 1;" % (self._business_table,uuid)
        b =  self.get_one(sql)
        if b:
            return b.id
        else:
            return 0

    
        
    def get_all_business(self, uid=None, category=None):
        sql="SELECT id, uuid, mobile, name, name_cn, status, score, lat, lon, source_type, source_id," \
            " description, address, category,cover, owner,country_id " \
            " FROM %s " \
            " WHERE `status`!=%s " % (self._business_table, const.Business.STATUS_DELETE)
        if uid is not None:
            sql += " AND owner=%s " % uid
        if category is not None:
            sql += " AND `category`=%s " % category
        list = self.get_rows(sql)
        for l in list:
            if l['category']==const.Business.CATEGORY_HOTEL:
                l['category_name'] = 'hotel'
            elif l['category']==const.Business.CATEGORY_RESTAURANT:
                l['category_name'] = 'restaurant'
            elif l['category']==const.Business.CATEGORY_SHOP:
                l['category_name'] = 'shop' 
        return list
    
    def get_list_by_creator(self, uid, type=None):
        sql = "SELECT id, name, name_cn, mobile, description, score, lat, " \
                " lon, address, uuid, status, cover, owner,country_id, currency_id " \
                " FROM %s " \
                " WHERE owner=%s and status> %s " % (self._business_table, uid, const.Business.STATUS_DELETE)
        if type<>None:
            sql += " and `category`=%d " % type
        return self.get_rows(sql)
    
    def get_list_of_reg_users(self, type=None):
        sql = "SELECT name, name_cn, uuid" \
                " FROM %s " \
                " WHERE owner<>0 and status not in (%s,%s) " % (self._business_table, const.Business.STATUS_DELETE, const.Business.STATUS_NOT_VERIFIED)
        if type<>None:
            sql += " and `category`=%d " % type
        return self.get_rows(sql)
    
    def _get_openday_time(self, dayid):
        sql = "SELECT from_time,to_time FROM %s WHERE openday_id=%d order by `from_time` asc" \
                % (self._openday_time_table,dayid)
        return self.get_rows(sql)
    
    # 获取假期时间
    def get_closedays(self, business_id):
        sql = "SELECT * FROM %s WHERE business_id=%d order by `from_time` asc" \
                % (self._closeday_table, business_id)
        return self.get_rows(sql)
    
    # 清除营业时间
    def clear_closedays(self, business_id):
        sql = "DELETE FROM %s WHERE business_id=%d" \
                % (self._closeday_table,business_id)
        self.execute(sql)

    # 修改营业日期及时间
    def add_closedays(self, days):
        
        sql = "INSERT INTO %s(`business_id`,`from_time`,`to_time`) " \
                " VALUES" % self._closeday_table
        for day in days:
            tmp_sql = sql+'(%d,%d,%d)' % (day['business_id'],
                                         day['from'],
                                         day['to'])
            self.execute(tmp_sql)
        return True

    # 获取营业日期及时间
    def get_opendays(self, business_id):
        sql = "SELECT * FROM %s WHERE business_id=%d order by `weekday` asc" \
                % (self._openday_table,business_id)
        days = self.get_rows(sql)
        for day in days:
            day['times'] = self._get_openday_time(day['id'])
        return days
        
    # 清除营业时间
    def clear_opendays(self, business_id):
        sql = "DELETE FROM %s WHERE business_id=%d" \
                % (self._openday_table,business_id)
        self.execute(sql)
        sql = "DELETE FROM %s WHERE business_id=%d" \
                % (self._openday_time_table,business_id)
        self.execute(sql)

    # 修改营业日期及时间
    def add_opendays(self, days):
        
        sql_1 = "INSERT INTO %s(`business_id`,`weekday`,`is_regular`,`is_free`) " \
                " VALUES" % self._openday_table
        sql_2 = "INSERT INTO %s(`openday_id`,`from_time`,`to_time`,`business_id`) " \
                " VALUES" % self._openday_time_table
        for day in days:
            tmp_sql = sql_1+'(%d,%d,%d,%d)' % (day['business_id'],
                                         day['weekday'],
                                         day['is_regular'],
                                         day['is_free'])
            ret = self.execute(tmp_sql)
            for time in day['times']:
                tmp_sql2 = sql_2+'(%d,%d,%d,%d)'% (ret[1],
                                             time['from'],
                                             time['to'],
                                             day['business_id'])
                self.execute(tmp_sql2)
        return True
    
    def search(self, key, category=const.Business.CATEGORY_RESTAURANT, skeys=['name','name_cn']):
        sql="SELECT id, uuid, mobile, status,name, name_cn, phone, score, lat, " \
            " lon, description, address, city, category,cover, owner, menu_num, like_num, collect_num " \
            " FROM %s " \
            " WHERE `status`!=%s AND ( " \
            % (self._business_table, const.Business.STATUS_DELETE)
        
        index = 0
        for k in skeys:
            if index == 0:
                sql += "%s like '%%%%%s%%%%' " % (k, self.escape_string(key)) 
            else:
                sql += "or %s like '%%%%%s%%%%' " % (k, self.escape_string(key)) 
            index = index+1
        sql += " )"
            
        if category is not None:
            sql += " AND `category`=%s " % category
        sql += " limit 50"
        list = self.get_rows(sql)
        for l in list:
            if l['category']==const.Business.CATEGORY_HOTEL:
                l['category'] = 'hotel'
            elif l['category']==const.Business.CATEGORY_RESTAURANT:
                l['category'] = 'restaurant'
            elif l['category']==const.Business.CATEGORY_SHOP:
                l['category'] = 'shop' 
        return list
    
    def delete(self,bid):
        sql = "UPDATE %s SET `status`=%d WHERE id=%s;" % (self._business_table, const.Business.STATUS_DELETE, bid)
        return self.update(sql)
    
    # 位置搜索
        
    def update_search_poi(self, id, poi):
        allow_arr = ["category", "name", "coordinate", "name_cn", "phone", "cover", "meal_num", "menu_num", "status"]
        poi = self._filt_array(poi, allow_arr)
        client = MgDB.get_client()
        db = client.tubban
        pois_collection = db.business_pois
        pois_collection.update({"id": id}, {"$set":poi})
        return True
        
        """
        if not poi.has_key('id'):
            return False
        s = ''
        if poi.has_key('lat') and poi.has_key('lon'):
            s += " `location` = GeomFromText('POINT(%s %s)')," % (poi['lat'], poi['lon'])
        if poi.has_key('status'):
            s += " `status` = %d," % (poi['status'])
        if poi.has_key('status'):
            s += " `status` = %d," % (poi['status'])
        if poi.has_key('menu_num'):
            s += " `menu_num` = %d," % (poi['menu_num'])
        if poi.has_key('menu_num'):
            s += " `meal_num` = %d," % (poi['meal_num'])
            
        if len(s) <= 0:
            return True
        s = s[0:len(s)-1]
        sql = "UPDATE %s SET %s WHERE id = %d" % (self._search_poi_table, s, int(poi['id']))
        #print sql
        sql = sql.replace('%', '%%')
        ret = self.update(sql)
        return ret[0]
        """
    
    def update_menu_version(self, id):
        sql = "UPDATE %s set menu_version=%d WHERE id=%d" % (self._business_table, Common.get_current_time(), int(id))
        return self.update(sql)[0]
    
    
    #-------------------- OP ---------------------
    
    def get_pager_list(self, pager, status=None, key=None, w_sql=None):
        size = pager['ps']
        offset = size*(pager['p']-1)
        
        if status is not None :
            where_sql = " WHERE status=%d " % status
        else:
            where_sql = ' WHERE status>%d ' % const.Business.STATUS_DELETE
        
        
        if key is not None and key <> '':
            #where_sql = where_sql+" AND uuid like '%%%s%%' " % (key)
            where_sql = where_sql+" AND (uuid = '%s' or name like '%%%%%s%%%%')" % (self.escape_string(key), self.escape_string(key))
            
        if w_sql is not None and w_sql <> '':
            where_sql = where_sql+" AND "+w_sql
            
        count_sql = "SELECT count(*) as total FROM %s b " % self._business_table + where_sql
        count =  self.get_one(count_sql)['total']
        if count<>0:
            se_sql = "SELECT b.* FROM %s b " \
                        " %s " \
                        " order by b.id desc " \
                        " limit %s,%s"  \
            % (self._business_table, where_sql, offset, size)
            rows = self.get_rows(se_sql)
            return dict(total=count, data=rows)
        else:
            return dict(total=0, data=[])
     
    def get_no_cover_but_has_image_pager_list(self, pager):
        
        size = pager['ps']
        offset = size*(pager['p']-1)
        
        sql = "SELECT distinct business_id from b_image"
        business_ids1 = self.get_rows(sql)
        
        sql = "SELECT distinct business_id from b_image_ugc"
        business_ids2 = self.get_rows(sql)
        
        business_ids = {}
        for b in business_ids1:
            business_ids[b['business_id']] = 1
        for b in business_ids2:
            business_ids[b['business_id']] = 1 
        business_ids = business_ids.keys()
        
        business_ids = [str(i) for i in business_ids]
        if len(business_ids)>0:
            sql = "SELECT id from business where cover='' and id in (%s)" % ','.join(business_ids)
            business_ids = self.get_rows(sql)
        count =  len(business_ids)
        
        if count==0:
            return dict(total=0, data=[])
        
        ids = {}
        for b in business_ids:
            ids[b['id']] = 1 
        ids = ids.keys()
        
        select_ids = [ str(i) for i in ids[offset:offset+size]]
        select_ids.append('0')
        if count<>0:
            se_sql = "SELECT b.* FROM %s b " \
                        " WHERE id in (%s) " \
                        " order by b.id desc " \
            % (self._business_table, ','.join(select_ids))
            rows = self.get_rows(se_sql)
            return dict(total=count, data=rows)
        else:
            return dict(total=0, data=[])
        
    def get_business_ugc_image_pager_list(self, pager, status=None):
        size = pager['ps']
        offset = size*(pager['p']-1)
        
        where_sql = ' WHERE 1=1 '
        if status is not None or status <> -1:
            where_sql = where_sql+" AND verified=%d " % status
        
        count_sql = "SELECT count(*) as total FROM %s b " % self._image_ugc_table + where_sql
        count =  self.get_one(count_sql)['total']
        if count<>0:
            se_sql = "SELECT * FROM %s " \
                        " %s " \
                        " order by add_time asc " \
                        " limit %s,%s"  \
            % (self._image_ugc_table, where_sql, offset, size)
            rows = self.get_rows(se_sql)
            return dict(total=count, data=rows)
        else:
            return dict(total=0, data=[])
    
    def get_uploadmenu_list(self):
        se_sql = "SELECT b.* FROM %s b " \
                        " WHERE b.id in (SELECT DISTINCT rid FROM %s WHERE status=%s) " \
                        " order by b.id desc " \
        % (self._business_table, self._carte_source, const.CarteSource.STATUS_UNHANDLED)
        return self.get_rows(se_sql)
    
    def change_ugc_images_verified(self, uuids, verified):
        uuids = uuids.split(',')
        for uuid in uuids:
            sql = "UPDATE %s set verified=%d WHERE uuid='%s' " % (self._image_ugc_table, verified, uuid)
            self.update(sql)[0]
        return True

    #########一下为导入工具用到的方法，有可能需要优化#############

    def is_exist(self, name, state, address):
        sql = "SELECT id, count(1) as total FROM %s where name='%s' and state='%s' and address='%s'" % \
                (self._business_table, self.escape_string(name), self.escape_string(state), self.escape_string(address))
        one = self.get_one(sql)
        if one['total'] == 0:
            return [False, 0]
        return [True, one['id']]
    
    def is_name_exist(self, name):
        sql = "SELECT id, count(1) as total FROM %s where name='%s'" % \
                (self._business_table, self.escape_string(name))
        one = self.get_one(sql)
        if one['total'] == 0:
            return [False, 0]
        return [True, one['id']]
    
    def get_unlocate_by_index(self, index):
        #sql = "SELECT * FROM %s WHERE lat>47.7983333333 or lat<45.819023 or lon<5.957344 or lon>10.492577 order by id desc LIMIT %s,1" % (self._business_table, index)
        sql = "SELECT * FROM %s WHERE lat=1 and lon=1 order by id asc LIMIT %s,1" % (self._business_table, index)
        row = self.get_one(sql)
        if row:
            sql = "UPDATE %s SET lat=0, lon=0 WHERE id=%d" % (self._business_table, row['id'])
            self.execute(sql)
        return row
    
    def get_by_extra(self, extra):
        sql = "SELECT * FROM %s WHERE `extra`='%s'" % (self._business_table, extra)
        return self.get_one(sql)
    
    ######### 统计用
    
    def get_desc_cn_empty_cnt(self, city_id):
        sql = "SELECT count(1) as total FROM %s WHERE `description_cn`='' AND city_id=%d AND status>%d" % (self._business_table, city_id, const.Business.STATUS_DELETE)
        return self.get_one(sql)['total']
    
    def get_desc_cn_not_empty_cnt(self, city_id):
        sql = "SELECT count(1) as total FROM %s WHERE `description_cn`!='' AND city_id=%d AND status>%d" % (self._business_table, city_id, const.Business.STATUS_DELETE)
        return self.get_one(sql)['total']
    
    def get_menu_need_not_upload(self, city_id):
        sql = "SELECT count(1) as total FROM %s b LEFT JOIN restaurant r ON b.id=r.id WHERE b.`menu_num`=0 AND r.has_menu=1 AND b.city_id=%d AND b.status>%d" % (self._business_table, city_id, const.Business.STATUS_DELETE)
        return self.get_one(sql)['total']
        
    def get_menu_need_and_upload(self, city_id):
        sql = "SELECT count(1) as total FROM %s b LEFT JOIN restaurant r ON b.id=r.id WHERE b.`menu_num`=1 AND r.has_menu=1 AND b.city_id=%d AND b.status>%d" % (self._business_table, city_id, const.Business.STATUS_DELETE)
        return self.get_one(sql)['total']
    
    def get_menu_upload_num(self, city_id):
        sql = "SELECT count(1) as total FROM %s WHERE `menu_num`>0 AND city_id=%d AND status>%d" % (self._business_table, city_id, const.Business.STATUS_DELETE)
        return self.get_one(sql)['total']
        