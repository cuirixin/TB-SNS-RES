#!/usr/bin/env python2.7
#-*- coding:utf8 -*-
#
# 2013-12-4 by Victor
# Copyright 2013 Tubban
from _module import const
from _module._base_m_ import BaseModel
from _module._lib.common import Common

class DiscoverModel(BaseModel):
    
    def __init__(self, uid = None):
        self._discover_table = 'discover'
        self._business_table = 'business'
        self._discover_like_table = 'discover_like'
        self._uid = uid
        
    def get_by_id(self, id):
        sql = "SELECT * FROM %s WHERE id = %d" % (self._discover_table, int(id))
        return self.get_one(sql)
        
    def _add(self, fields):
        
        discover = {
            'business_id': {'type':'d', 'required':1},
            'business_uuid': {'type':'s', 'required':1},
            'image_uuid': {'type':'s', 'default':''},
            'title': {'type':'s', 'default':''},
            'uid': {'type':'d', 'required':1},
            'username': {'type':'s', 'required':1},
            'lat': {'type':'f', 'default':0},
            'lon': {'type':'f', 'default':0},
            'add_time' : {'type':'d', 'default':Common.get_current_time()},
            'version' : {'type':'d', 'default':Common.get_current_time()}
        }
        
        ret = self._args_handle('insert', fields, discover)   
        if not ret[0]:
            # todo:
            return ret
        return self._insert(self._discover_table, discover)
    
    def add(self, kwarg):
        return self._add(kwarg)
    
    def has_like(self, id, uid):
        sql = "SELECT count(1) as total from %s where discover_id=%d and uid=%d" % (self._discover_like_table, id, uid)
        if self.get_one(sql)['total'] <> 0:
            return True
        return False
    def add_like(self, id, uid):
        #delta = 60*60*24/10
        sql = "UPDATE %s SET like_num=like_num+1, version=version+864 WHERE id=%d;" % (self._discover_table, int(id))
        ret =  self.execute(sql)[0]
        
        sql = "INSERT INTO %s(discover_id, uid) values(%d,%d)" % (self._discover_like_table, int(id), int(uid))
        self.execute(sql)
        return ret
    
    def change_status(self, id, status):
        sql = "UPDATE %s SET status=%d WHERE id=%d;" % (self._discover_table, status, int(id))
        ret =  self.execute(sql)[1]
        return ret
    
    def get_pager_list(self, pager, order_type, position=None):
        size = pager['ps']
        offset = size*(pager['p']-1)
        where_sql = ' WHERE d.status>%d ' % const.Discover.STATUS_DELETE
        count_sql = "SELECT count(*) as total FROM %s d " % self._discover_table + where_sql
        count =  self.get_one(count_sql)['total']
        if count<>0:
            
            order_sql = "d.add_time desc"
            select_extra = ''
            if order_type == 1:
                order_sql = "d.add_time desc"
            elif order_type == 2:
                order_sql = "d.like_num desc"
            elif order_type == 3:
                order_sql = "d.comment_num desc"
            elif order_type == 4:
                order_sql = "d.version desc"
            elif order_type == 5:
                order_sql = "p_distance asc, d.version desc"
                select_extra = ", sqrt((d.lat-%f)*(d.lat-%f)+(d.lon-%f)*(d.lat-%f)) as p_distance" % (position['lat'], position['lat'], position['lon'], position['lon'])
            
            # c.uid as user_id, c.username as user_name
            se_sql = "SELECT d.*,b.name as business_name, b.name_cn as business_name_cn %s FROM %s d " \
                        " LEFT JOIN %s b on b.id=d.business_id " \
                        " %s " \
                        " order by %s " \
                        " limit %s,%s"  \
            % (select_extra, self._discover_table, self._business_table, where_sql, order_sql, offset, size)
            rows = self.get_rows(se_sql)
            
            for one in rows:
                if one.has_key('p_distance'):
                    del one['p_distance']
            return dict(total=count, data=rows)
        else:
            return dict(total=0, data=[])

    """
    Func: 通过Image UUID获取discover
    """
    def get_by_uuid(self, uuid):
        sql = "SELECT * FROM %s WHERE image_uuid = '%s' limit 1" % (self._discover_table, uuid)
        return self.get_one(sql)
