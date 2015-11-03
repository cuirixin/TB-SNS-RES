#!/usr/bin/env python2.7
#-*- coding:utf8 -*-
#
# 2013-12-4 by Victor
# Copyright 2013 Tubban
from _module._base_m_ import BaseModel
from _module._lib.common import Common

class SysdataModel(BaseModel):
    
    def __init__(self):
        self._continent_table = 'sys_continents'
        self._weekday_table = 'sys_weekday'
        self._paymenttool_table = 'sys_paymenttool'
        self._language_table = 'sys_language'
        self._country_table = "sys_country"
        self._city_table = "sys_city"
        self._currency_table = "sys_currency"
        self._portionunit = 'sys_portionunit'
        self._foodingredient_table ="sys_foodingredient"
        self._cooktechnique_table = "sys_cooktech"
        self._mouthfeel_table = "sys_mouthfeel"
        self._foodtype_table = "sys_foodtype"
        self._cartetype_table="sys_cartetype"
        self._dishgroup_table = 'sys_dishgroup'
        self._diningOption_table = 'sys_diningoption'
        self._cuisinestyle_table = 'sys_cuisine'
        self._reserve_position_table = 'sys_reserve_position'
        self._business_district_type_table = 'sys_business_district_type'
        self._currency_exchange_table = 'sys_currency_exchange'
        self._restaurant_subcategory_table = 'sys_restaurant_subcategory'
        self._topic_local_special_tag = 'sys_topic_local_special_tag'
        self._city_sample = 'sys_city_sample'
        
    def get_all_continents(self, field='EN'):
        sql = "SELECT id, %s as name, standard FROM %s order by id asc" % (field, self._continent_table)
        return self.get_rows_by_slave(sql)

    def get_all_weekdays(self, field='EN'):
        sql = "SELECT id, %s as name FROM %s order by id asc" % (field, self._weekday_table)
        return self.get_rows_by_slave(sql)
    
    def get_weekday_by_id(self,wid, field='EN'):
        sql = "select %s as name FROM %s where id=%s" %(field, self._weekday_table,wid)
        return self.get_one_by_slave(sql)['name']
    
    def get_closeday(self,ids,field='EN'):
        ids = Common.filter_comma_ids(ids)
        if ids is None or ids=='':
            return []
        sql = "SELECT %s as name FROM %s WHERE id IN (%s)" % (field, self._weekday_table,ids)
        return self.get_rows_by_slave(sql)
    
    def get_closeday_names(self, ids, field='EN'):
        ids = Common.filter_comma_ids(ids)
        if ids is None or ids=='':
            return []
        sql = "SELECT %s as name FROM %s WHERE id IN (%s)" % (field, self._weekday_table,ids)
        return self.get_rows_by_slave(sql)
    
    def get_all_paymenttool(self, field='EN'):
        _field = field
        if _field<>'CN' and _field<>'EN':
            _field = 'EN'
        sql = "SELECT id, icon, %s as name FROM %s order by id asc" % (_field, self._paymenttool_table)
        return self.get_rows_by_slave(sql)
    
    def get_paymenttool(self, ids, field='EN'):
        ids = Common.filter_comma_ids(ids)
        if ids is None or ids=='':
            return []
        _field = field
        if _field<>'CN' and _field<>'EN':
            _field = 'EN'
        sql = "SELECT id, %s as name ,icon FROM %s WHERE id IN (%s)" \
                % (_field, self._paymenttool_table,ids)
        return self.get_rows_by_slave(sql)
    
    def get_all_portionunit(self,field='EN'):
        sql = "SELECT id, %s as name FROM %s order by id asc" \
                % (field, self._portionunit)
        return self.get_rows_by_slave(sql) 
    
    def get_portionunit_by_group(self, group, field='EN'):
        sql = "SELECT id, %s as name FROM %s WHERE `group`=%s or `group`=0 order by id asc" % (field, self._portionunit, group)
        return self.get_rows_by_slave(sql) 
    
    def get_portionunit_by_id(self, id, field='EN'):
        sql = "SELECT id, %s as name FROM %s WHERE id=%d limit 1" % (field, self._portionunit, id)
        return self.get_one_by_slave(sql) 
    
    def get_all_foodingredient(self,field='EN'):
        sql = "SELECT id, %s as name FROM %s order by id asc" \
                % (field, self._foodingredient_table)
        return self.get_rows_by_slave(sql) 
    
    def get_all_cooktechnique(self,field='EN'):
        sql = "SELECT id, %s as name FROM %s order by id asc" \
                % (field, self._cooktechnique_table)
        return self.get_rows_by_slave(sql) 
    
    def get_all_mouthfeel(self,field='EN'):
        sql = "SELECT id, %s as name FROM %s order by id asc" \
                % (field, self._mouthfeel_table)
        return self.get_rows_by_slave(sql) 
    
    def get_all_foodtypes(self, field='EN'):
        sql = "SELECT id, %s as name FROM %s order by id asc" \
                % (field, self._foodtype_table)
        return self.get_rows_by_slave(sql) 
    
    def get_all_languages(self, field='EN'):
        sql = "SELECT id, icon, %s as name FROM %s order by id asc" \
                % (field, self._language_table)
        return self.get_rows_by_slave(sql)
    
    def get_servicelanguage(self, ids, field='EN'):
        ids = Common.filter_comma_ids(ids)
        if ids is None or ids=='':
            return []
        # TODO 暂时language支持四中语言
        if field not in ['EN', 'CN', 'FR', 'DE']:
            field= 'EN'
        sql = "SELECT id, %s as name FROM %s WHERE id IN (%s)" \
                % (field, self._language_table,ids)
        return self.get_rows_by_slave(sql)
    
    def get_all_country(self, field='EN'):
        sort_index = "EN"
        if field == 'CN':
            sort_index = "CN_INDEX"
        sql = "SELECT id, icon, %s as name, phone_code, continent_id FROM %s order by `%s` asc" \
                % (field, self._country_table, sort_index)
        return self.get_rows_by_slave(sql)
    
    def get_all_city(self, field='EN'):
        sql = "SELECT id, %s as name, lat, lon, `hot`, country_id FROM %s order by `hot` desc" \
                % (field, self._city_table)
        return self.get_rows_by_slave(sql)
    
    def get_all_city_by_sort(self, field='EN'):
        if field == 'EN':
            sort = 'EN'
        else:
            sort = '%s_INDEX' % field
        sql = "SELECT id, %s as name, lat, lon, `hot`, country_id FROM %s order by `%s` asc" \
                % (field, self._city_table, sort)
        return self.get_rows_by_slave(sql)
    
    def get_all_city_with_index(self, field='CN'):
        index_field = '%s_INDEX' % field
        sql = "SELECT id, %s as name, %s as `index`, lat, lon, `hot`, country_id FROM %s order by `%s` asc, `hot` desc" \
                % (field, index_field, self._city_table, index_field)
        return self.get_rows_by_slave(sql)
    
    def get_top_hot_cities(self, limit=10, field='CN'):
        sql = "SELECT id, %s as name, lat, lon, `hot` FROM %s order by `hot` desc limit %d" \
                % (field, self._city_table, limit)
        return self.get_rows_by_slave(sql)
    
    def get_all_city_with_country(self, field='EN'):
        sql = "SELECT id, %s as name, country_id FROM %s order by id asc" \
                % (field, self._city_table)
        return self.get_rows_by_slave(sql)
    
    def get_city_by_id(self, id, field='EN'):
        sql = "SELECT id, `%s` as name, lat, lon, country_id from %s where id=%d" % (field, self._city_table, id)
        return self.get_one_by_slave(sql)
    
    def get_city_by_ids(self, ids, field='EN'):
        ids = Common.filter_comma_ids(ids)
        sql = "SELECT id, `%s` as name from %s where id in (%s)" % (field, self._city_table, ids)
        return self.get_rows_by_slave(sql)
    
    def get_all_currency(self, field='EN'):
        _field = field
        if _field<>'CN' and _field<>'EN':
            _field = 'EN'
        sql = "SELECT id, icon, %s as name, iso_code FROM %s order by id asc" \
                % (_field, self._currency_table)
        return self.get_rows_by_slave(sql)
    
    def get_currency(self, id, field='EN'):
        _field = field
        if _field<>'CN' and _field<>'EN':
            _field = 'EN'
        sql = "SELECT id, icon, %s as name, iso_code FROM %s WHERE id=%d" \
                % (_field, self._currency_table, id)
        return self.get_one_by_slave(sql)
        
    
    def get_country_name(self,cid,field='EN'):
        sql = "SELECT  %s as name FROM %s WHERE id=%s" \
                % (field, self._country_table,int(cid))
        ret = self.get_one_by_slave(sql)
        if ret:
            return ret.name
        else:
            return ''
        
    def get_country(self, cid, field='EN'):
        sql = "SELECT id, %s as name FROM %s WHERE id=%d" \
                % (field, self._country_table, cid)
        return self.get_one_by_slave(sql)
        
    def get_city_name(self,cid,field='EN'):
        sql = "SELECT  %s as name FROM %s WHERE id=%s" \
                % (field, self._city_table, int(cid))
        ret = self.get_one_by_slave(sql)
        if ret:
            return ret.name
        else:
            return ''
        
    def get_city(self, cid, field='EN'):
        sql = "SELECT id, %s as name FROM %s WHERE id=%d" \
                % (field, self._city_table, cid)
        return self.get_one_by_slave(sql) 
        
    def get_all_cartetypes(self,field="EN"):
        sql = "SELECT id, %s as name FROM %s order by id asc" % (field, self._cartetype_table)
        return self.get_rows_by_slave(sql) 
    

    def get_all_ingredient(self, field='EN'):
        sql = "SELECT id, %s as name FROM %s " % (field, self._foodtype_table)
        types = self.get_rows_by_slave(sql)
        for type in types:
            sql = "SELECT id, %s as name FROM %s WHERE foodtype_id=%s order by id asc" \
                % (field, self._foodingredient_table, type['id'])
            ingredient = self.get_rows(sql)
            type['ingredient'] = ingredient
        return types
    
    def get_all_foodtype(self, field="EN"):
        sql = "SELECT id, %s as name FROM %s " % (field, self._foodtype_table)
        return self.get_rows_by_slave(sql)

    def get_ingredient(self,ids, field='EN'):
        ids = Common.filter_comma_ids(ids)
        if len(ids)==0:
            return []
        sql = "SELECT a.id, a.%s as name, a.foodtype_id as type_id, b.%s as type_name " \
                " FROM %s a  " \
                " LEFT JOIN %s b on b.id=a.foodtype_id " \
                " WHERE a.id IN (%s) order by a.foodtype_id " % (field, field, self._foodingredient_table, self._foodtype_table, ids)
        return self.get_rows_by_slave(sql) 
    
    def get_cooktechnique(self,ids, field='EN'):
        ids = Common.filter_comma_ids(ids)
        
        if len(ids)==0:
            return []
        sql = "SELECT id, %s as name FROM %s WHERE id IN (%s)" % (field, self._cooktechnique_table, ids)
        return self.get_rows_by_slave(sql)
    
    def get_mouthfeel(self,ids,field='EN'):
        ids = Common.filter_comma_ids(ids)
        if len(ids)==0:
            return []
        sql = "SELECT id, %s as name FROM %s WHERE id IN (%s)" % (field, self._mouthfeel_table, ids)
        return self.get_rows_by_slave(sql)
    
    def get_dishgoup_by_id(self, id, field='EN'):
        sql = "SELECT `id`, `%s` as name FROM %s WHERE id=%d " % \
                (field, self._dishgroup_table, id)
        return self.get_one_by_slave(sql)
    
    def get_all_dishgroups(self, field="EN"):
        sql = "SELECT id, %s as name FROM %s order by EN asc" % (field, self._dishgroup_table)
        return self.get_rows_by_slave(sql) 
    
    def get_all_diningOptions(self,field='EN'):
        sql = "SELECT id, icon, %s as name FROM %s order by id asc" % (field, self._diningOption_table)
        return self.get_rows_by_slave(sql) 
    
    def get_all_rsubcategories(self,field='EN'):
        sql = "SELECT id, %s as name FROM %s order by id asc" % (field, self._restaurant_subcategory_table)
        return self.get_rows_by_slave(sql) 
    
    def get_rsubcategory(self, id, field='EN'):
        if id == 0:
            return {"id": 0, "name": "暂无归类"}
        sql = "SELECT id, %s as name FROM %s WHERE id=%d limit 1" % (field, self._restaurant_subcategory_table, id)
        return self.get_one_by_slave(sql) 
    
    def get_dining_option(self,ids,field='EN'):
        ids = Common.filter_comma_ids(ids)
        if ids is None or ids=='':
            return []
        sql = "SELECT %s as name FROM %s WHERE id IN (%s)" % (field, self._diningOption_table, ids)
        return self.get_rows_by_slave(sql) 
    
    def get_all_cuisineStyle(self,field='EN'):
        sql = "SELECT id, icon,continent_id, %s as name FROM %s order by id asc" % (field, self._cuisinestyle_table)
        return self.get_rows_by_slave(sql) 
    
    def get_cuisine_style(self,ids, field='EN'):
        ids = Common.filter_comma_ids(ids)
        if ids is None or ids=='':
            return []
        sql = "SELECT id, %s as name FROM %s WHERE id IN (%s)" % (field, self._cuisinestyle_table, ids)
        return self.get_rows_by_slave(sql)
    
    def find_one_cuisine_style(self, key, field='CN'):
        key = key.strip()
        sql = "SELECT id FROM %s WHERE `%s` like '%%%%%s%%%%' limit 1" % (self._cuisinestyle_table, field, self.escape_string(key))
        return self.get_one_by_slave(sql)
    
    def get_all_reserve_positions(self,field='EN'):
        sql = "SELECT id, %s as name FROM %s order by id asc" % (field, self._reserve_position_table)
        return self.get_rows_by_slave(sql) 
    
    def get_reserve_position(self, ids, field='EN'):
        ids = Common.filter_comma_ids(ids)
        if ids is None or ids=='':
            return []
        sql = "SELECT id, %s as name FROM %s WHERE id IN (%s)" % (field, self._reserve_position_table, ids)
        return self.get_rows_by_slave(sql)
    
    def get_all_business_district_type(self, field='EN'):
        sql = "SELECT id, %s as name FROM %s order by id asc" % (field, self._business_district_type_table)
        return self.get_rows_by_slave(sql)
    
    def get_country_by_phone_code(self, phone_code, field='EN'):
        sql = "SELECT id, %s as name FROM %s where phone_code='%s' limit 1" % (field, self._country_table, self.escape_string(phone_code))
        return self.get_one_by_slave(sql)
    
    def mod_city_location(self, city_id, lat, lon):
        sql = "UPDATE %s SET lat=%f, lon=%f WHERE id=%d" % (self._city_table, lat, lon, city_id)
        return self.execute(sql)[0]
    
    def get_current_exchange_rate(self, currency_id):
        sql = "SELECT `rate`, `warning` FROM %s WHERE id=%d limit 1" % (self._currency_exchange_table, currency_id)
        one =  self.get_one(sql)
        if not one:
            return -1
        else:
            return one['rate']
        
    def get_all_currency_exchange(self):
        sql = "SELECT id, rate, iso_code, warning, DATE_FORMAT(`last_update`, '%%%%Y-%%%%m-%%%%d %%%%H:%%%%m:%%%%S') `last_update` FROM %s" % (self._currency_exchange_table)
        return self.get_rows(sql)
    
    def get_currency_exchange(self, currency_id):
        sql = "SELECT id, `rate`, iso_code, `warning`, DATE_FORMAT(`last_update`, '%%%%Y-%%%%m-%%%%d %%%%H:%%%%m:%%%%S') `last_update` FROM %s WHERE id=%d limit 1" % (self._currency_exchange_table, currency_id)
        return self.get_one(sql)
        
    def get_sys_carte_by_id(self, carte_id, field='EN'):
        sql = "SELECT id, %s as name FROM %s WHERE id=%d LIMIT 1" % (field, self._cartetype_table, carte_id)
        return self.get_one(sql)
    
    def get_all_local_special_tags(self, field='EN'):
        sql = "SELECT id, %s as name FROM %s order by sortrank desc" % (field, self._topic_local_special_tag)
        return self.get_rows_by_slave(sql)
    
    def get_local_special_tag_by_id(self, id, field='EN'):
        sql = "SELECT id, %s as name FROM %s WHERE id=%d LIMIT 1" % (field, self._topic_local_special_tag, id)
        return self.get_one_by_slave(sql)
    
    def get_city_samples(self, city_id):
        sql = "SELECT id, lat, lon, address FROM %s WHERE city_id=%d and status=1" % (self._city_sample, city_id)
        return self.get_rows(sql)
    
    def get_city_sample_by_id(self, id):
        sql = "SELECT id, lat, lon, city_id, country_id FROM %s WHERE id=%d " % (self._city_sample, id)
        return self.get_one(sql)
    
    def add_city_sample(self, fields):
        sample = {
            'lat' : {'type':'f', 'required':1},
            'lon' : {'type':'f', 'required':1},
            'city_id' : {'type':'d', 'required':1},
            'country_id': {'type':'d', 'required':1},
            'address' : {'type':'s', 'default':''},
        }
        
        ret = self._args_handle('insert', fields, sample)   
        if not ret[0]:
            # todo:
            return ret
        return self._insert(self._city_sample, sample)
    
    def mod_city_sample(self, id, args):
        sample = {
            'lat': {'type':'f'},
            'lon': {'type':'f'},
        }   
        if not id:
            return False

        ret = self._args_handle('update', args, sample)               
        if not ret[0]:
            return False
        where = "id=%d" % int(id)
        ret = self._update(self._city_sample, sample, where)
        if not ret[0]:
            return False
        return True
    
    def del_city_sample(self, id):
        sql = "UPDATE %s SET status=-1 WHERE id=%d " % (self._city_sample, id)
        return self.execute(sql)[0]
    
    #--------------- Special Below ------------------

    def get_portionunit_by_EN(self, name):
        sql = "SELECT * FROM %s WHERE EN='%s' LIMIT 1" \
                % (self._portionunit, name)
        return self.get_one_by_slave(sql)

    def get_cartetype_by_EN(self, name):
        sql = "SELECT * FROM %s WHERE EN='%s' LIMIT 1" % (self._cartetype_table, self.escape_string(name))
        return self.get_one_by_slave(sql)
    
    def get_dishgroup_by_EN(self, name):
        sql = "SELECT * FROM %s WHERE EN='%s' LIMIT 1" \
                % (self._dishgroup_table, name)
        return self.get_one_by_slave(sql)
    
    