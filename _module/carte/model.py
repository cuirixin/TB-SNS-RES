#!/usr/bin/env python2.7
#-*- coding:utf8 -*-
#
# 2013-12-4 by Victor
# Copyright 2013 Tubban
from _module import const
from _module._base_m_ import BaseModel
from _module._lib.common import Common

class CarteModel(BaseModel):
    def __init__(self, uid = None):
        self._uid = uid
        self._carte_table = 'r_carte'
        self._cartetype_table = 'sys_cartetype'
    
    ##carte type 的sys 表
    
    
    def get_brief_list_by_restid(self, rid):
        sql = "SELECT c.id, c.type_id as refer_id,c.`sortrank` FROM %s c " \
                " WHERE c.restaurant_id=%d  and c.status> %d order by c.sortrank asc" % (self._carte_table, rid, const.Carte.STATUS_DELETE)
        return self.get_rows(sql)
        
    def get_by_id(self,cid, field="EN"):
        sql = "SELECT c.*, IFNULL(ct.`%s`,'') as `name` FROM %s c " \
                " LEFT JOIN %s ct ON ct.id=c.type_id " \
                " WHERE c.id=%s" % (field, self._carte_table, self._cartetype_table, cid)
        return self.get_one(sql)
    
    def get_by_restaurant_and_syscarte(self, rid, sys_carte_id):
        sql = "SELECT id FROM %s WHERE restaurant_id=%d and type_id=%d LIMIT 1" \
                % (self._carte_table, rid, sys_carte_id)
        return self.get_one(sql)
        
    
    #########################################

    
    def get_list_by_restid(self, restid, field="EN"):
        sql = "SELECT c.*, IFNULL(ct.`%s`,'') as `name`,c.`sortrank` FROM %s c " \
                " LEFT JOIN %s ct ON ct.id=c.type_id " \
                " WHERE c.restaurant_id=%d and c.status> %d order by c.sortrank asc" % (field, self._carte_table, self._cartetype_table, restid, const.Carte.STATUS_DELETE)
        return self.get_rows(sql)
    
    def get_cnt_by_restid(self, bid):
        sql = "SELECT count(*) as total FROM %s " \
                " WHERE restaurant_id=%d and status> %d" % (self._carte_table, bid, const.Carte.STATUS_DELETE)
        return self.get_one(sql)['total']
    
    def get_restaurant_id(self,carteid):
        sql = "SELECT restaurant_id FROM %s WHERE id=%s " % (self._carte_table, carteid)
        ret = self.get_one(sql)
        if ret:
            return ret['restaurant_id']
        else:
            return None
    
    def add(self, carte):
        sql="INSERT INTO %s" % self._carte_table
        sql +="(`restaurant_id`,`type_id`,`add_time`,`tag`,`version`)VALUES(%s,%s,%s,%s,%s);"
        return self.execute(sql,
                            carte.get('restaurant_id',0),carte.get('type_id',0),
                            carte.get('add_time',0),carte.get('tag',''),carte.get('version',0)
                            )
    
    def mod(self, carte):
        if not carte.has_key('id'):
            return False
        s = ''
        if carte.has_key('type_id'):
            s += " type_id = %d," % (carte['type_id'])
        if len(s) <= 0:
            return True
        s = s[0:len(s)-1]
        sql = "UPDATE %s SET %s WHERE id = %d" % (self._carte_table, s, carte['id'])
        sql = sql.replace('%', '%%')
        ret = self.update(sql)
        return ret[0]
    
    def delete(self, id):
        carte = self.get_by_id(id)
        if not carte:
            return False
        
        # 删除 carte_dish对应的 dish
        # 删除 setmeal，其中删除对应的dishgroup以及dishgroup下dish
        
        sql = "UPDATE %s SET status=%d WHERE id=%s " % (self._carte_table, const.Carte.STATUS_DELETE, id)
        ret = self.execute(sql)
        if not ret[0]:
            return False
        return True
    
    def get_restaurant_by_id(self,carte_id):
        sql = "select restaurant_id from %s where id=%s;" % (self._carte_table,carte_id)
        return self.get_one(sql)

    """
    def edit(self, hotel,hid):
        sql = "UPDATE %s SET " % self._hotel_table
        
        for key in hotel:
            sql += "%s=%%(%s)s," % (key,key)
        sql = sql[0:len(sql)-1] 
        sql += " WHERE id=%s" % hid
        
        return self.update(sql, **hotel)
    """
    
    def set_order(self,orderIds):
        for i, Id in enumerate(orderIds):
            sql = "UPDATE %s SET `sortrank`=%s WHERE `id`=%s" % (self._carte_table,i+1,Id)
            self.update(sql)
        return True
    
    
    #########一下为导入Excel用到的方法，有可能需要优化#############

    def get_one_by_type(self, business_id, type):
        sql = "SELECT * FROM %s WHERE restaurant_id=%d and type_id=%d " \
                " LIMIT 1" % (self._carte_table, business_id, type)
        return self.get_one(sql)
    
class CarteSourceModel(BaseModel):
    def __init__(self, uid = None):
        self._uid = uid
        self._carte_table = 'r_carte'
        self._carte_source_table="r_carte_source"
    
    def get_list_by_restid(self, restid):
        sql = "SELECT * FROM %s WHERE rid=%d and status!=%d ORDER BY id asc " \
                % (self._carte_source_table, restid, const.CarteSource.STATUS_DELETE)
        return self.get_rows(sql)

    def get_by_id(self, id):
        sql = "SELECT * FROM %s WHERE id=%d limit 1" \
                % (self._carte_source_table, int(id))
        return self.get_one(sql)
    
    def find_last(self, rid):
        sql = "SELECT * FROM %s WHERE rid=%d order by id desc limit 1" \
                % (self._carte_source_table, int(rid))
        return self.get_one(sql)
    
    def get_by_pure_name(self, name):
        sql = "SELECT * FROM %s WHERE pure_name='%s' limit 1" \
                % (self._carte_source_table, name)
        return self.get_one(sql)
    
    def add(self, fields):
        return self._add(fields)


    def _add(self, fields):
        carte_source = {
            'rid': {'type':'d', 'required':1},
            'uuid': {'type':'s', 'required':1},
            'md5_file': {'type':'s', 'required':1},
            'pure_name': {'type':'s', 'required':1},
            'size': {'type':'s', 'required':1},
            'name': {'type':'s', 'default':''},
            'carte_type': {'type':'d', 'required':1},
            'status': {'type':'d', 'default':const.CarteSource.STATUS_UNHANDLED},
            'add_time': {'type':'d', 'default':Common.get_current_time()},
        }
        
        ret = self._args_handle('insert', fields, carte_source)               
        if not ret[0]:
            # todo:
            return ret
        return self._insert(self._carte_source_table, carte_source)
    
    def change_status(self, id, status):
        sql = "Update %s set status=%s where id=%d" \
                %(self._carte_source_table, status, id)
        return self.update(sql)[0]
    
    
    def get_pager_list(self, pager, status=None, key=None):
        
        size = pager['ps']
        offset = size*(pager['p']-1)
        
        where_sql = ' WHERE a.status>%d ' % const.CarteSource.STATUS_DELETE
        if status is not None:
            where_sql = where_sql+" AND a.status=%d " % status
        
        if key is not None and key<>'':
            #where_sql = where_sql+" AND uuid like '%%%s%%' " % (key)
            where_sql = where_sql+" AND a.uuid = '%s' " % (key)

        count_sql = "SELECT count(*) as total FROM %s a " % self._carte_source_table + where_sql
        count =  self.get_one(count_sql)['total']
        if count<>0:
            se_sql = "SELECT a.*, b.CN as carte_type_name FROM %s a " \
                        " LEFT JOIN %s b on a.carte_type = b.id " \
                        " %s " \
                        " order by a.status asc,a.id desc " \
                        " limit %s,%s"  \
            % (self._carte_source_table, self._sys_carte_table, where_sql, offset, size)
            rows = self.get_rows(se_sql)
            return dict(total=count, data=rows)
        else:
            return dict(total=0, data=[])