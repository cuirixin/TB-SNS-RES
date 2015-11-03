#!/usr/bin/env python2.7
#-*- coding:utf8 -*-
#
# 2014-2-13 by Victor
# Copyright 2014 Tubban
from _module._base_m_ import BaseModel

class TagModel(BaseModel):
    
    def __init__(self, uid = None):
        self._tag_table = 'r_tag'
        self._uid = uid
        
    def add(self, tag):
        sql="INSERT INTO %s" % self._tag_table
        sql +="(`name`,`language_id`,`type`,`sortrank`)VALUES(%s,%s,%s,%s);"
        return self.execute(sql,
                            tag.get('name',''),tag.get('language_id',0),
                            tag.get('type',0),tag.get('sortrank',0)
                            )
    def get_list(self, in_ids, language_id=None, type=None):
        if len(in_ids)<1:
            return []
        
        sql = "SELECT id, name, language_id FROM %s WHERE 1=1 " % self._tag_table
        if in_ids and len(in_ids)>0:
            sql += " AND id in (%s) " % in_ids
        if language_id:
            sql += " AND language_id=%s " % language_id
        if type:
            sql += " AND type=%s " % type
        sql += " ORDER BY sortrank desc"
        return self.get_rows(sql)
    
    def delete_by_ids(self, in_ids):
        if len(in_ids)<1:
            return True
        sql = "DELETE FROM %s WHERE id in(%s)" % (self._tag_table, in_ids)
        return self.execute(sql)[0]
    