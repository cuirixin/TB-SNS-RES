#!/usr/bin/env python2.7
#-*- coding:utf8 -*-
#
# 2014-3-13 by Victor
# Copyright 2014 Tubban
from _module import const
from _module._base_m_ import BaseModel
from _module._lib.common import Common

class ClaimModel(BaseModel):
    
    def __init__(self, uid = None):
        self._uid = uid
        self._claim_talbe = 'b_claim'
        self._business_table = 'business'
        
    def get_by_id(self, id):
        sql = "SELECT * FROM %s WHERE id=%d" % (self._claim_talbe, id)
        return self.get_one(sql)
     
    def add(self, fields):
        '''
            'business_id': {'type': 'd', 'value': 'notNone'},
            'uid': {'type': 'd', 'value': 'notNone'},
            'contactor': {'type': 's', 'value': 'notNone'},
            'phone': {'type': 's', 'value': 'notNone'},
            'email': {'type': 's', 'value': 'notNone'},
            'note': {'type': 's', 'value': 'notNone'},
            'status': {'type': 'd', 'value': const.Claim.STATUS_NEW},
            'add_time': {'type': 'd', 'value': Common.get_current_time()},
        '''       
        return self._add(fields)

    def _add(self, fields):
        claim = {
            'business_id': {'type':'d', 'required':1},
            'uid': {'type':'d', 'required':1},
            'contactor': {'type':'s', 'required':1},
            'mobile': {'type':'s', 'default':''},
            'mobile_code': {'type':'s', 'default':''},
            'email': {'type':'s', 'default':''},
            'note': {'type':'s', 'default':''},
            'status': {'type':'d', 'default':const.Claim.STATUS_NEW},
            'add_time': {'type':'d', 'default':Common.get_current_time()},
        }
        
        ret = self._args_handle('insert', fields, claim)               
        if not ret[0]:
            # todo:
            return ret
        return self._insert(self._claim_talbe, claim)

    def get_pager_list(self, pager, status=const.Claim.STATUS_NEW):
        size = pager['ps']
        offset = size*(pager['p']-1)
        
        where_sql = ' WHERE 1=1 '
        if status is not None:
            where_sql = where_sql+" AND c.status=%d " % status
        count_sql = "SELECT c.* FROM %s c " % self._claim_talbe + where_sql
        count =  self._db.execute_rowcount(count_sql)
        if count<>0:
            se_sql = "SELECT c.*, b.id as business_id, b.name as business_name, " \
                        " b.uuid as business_uuid FROM %s c " \
                        " left join %s b on b.id=c.business_id " \
                        " %s " \
                        " order by c.business_id asc " \
                        " limit %s,%s"  \
            % (self._claim_talbe, self._business_table, where_sql, offset, size)
            rows = self.get_rows(se_sql)
            return dict(total=count, data=rows)
        else:
            return dict(total=0, data=[])
        
    def get_list_by_bid(self, business_id, status=const.Claim.STATUS_NEW):
        sql = "SELECT * FROM %s WHERE `business_id`=%d AND `status`=%d" % \
                (self._claim_talbe, business_id, status)
        return self.get_rows(sql)
    
    def agree(self, bid, uid):
        sql1 = "Update %s set status=%s where business_id=%d and uid=%d" \
                %(self._claim_talbe, const.Claim.STATUS_AGREE, bid, uid)
        ret = self.update(sql1)[0]
        if not ret:
            return False
        sql2 = "Update %s set status=%s where business_id=%d" \
                %(self._claim_talbe, const.Claim.STATUS_REJECT, bid)
        self.update(sql2)[0]
        return True
    
    def reject(self, bid, uid):
        sql1 = "Update %s set status=%s where business_id=%d and uid=%d" \
                %(self._claim_talbe, const.Claim.STATUS_REJECT, bid, uid)
        return self.update(sql1)[0]
    
    def change_status(self, bid, uid, status):
        sql1 = "update %s set status=%s where business_id=%d and uid=%d" \
                %(self._claim_talbe, status, bid, uid)
        return self.update(sql1)[0]
    
    def mod(self, id, kwarg):
        return self._mod(id, kwarg)
    
    def _mod(self, id, args):
        claim = {
            'status': {'type':'d'},
            'uid': {'type':'d'},
        }   
        if not id or id == 0:
            return False

        ret = self._args_handle('update', args, claim)               
        if not ret[0]:
            return False
        where = "id=%d" % int(id)
        
        ret = self._update(self._claim_talbe, claim, where)
        if not ret[0]:
            return False
        return True
    
    
    def change_status_by_bid(self, bid, status):
        sql1 = "update %s set status=%s where business_id=%d" \
                %(self._claim_talbe, status, bid)
        return self.update(sql1)[0]
    
        
    def get_all_by_id(self,bid):
        sql = "select * from business where id=%s"  % bid
        return self.get_one(sql)
    
