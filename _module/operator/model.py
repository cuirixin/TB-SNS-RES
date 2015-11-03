#!/usr/bin/env python2.7
#-*- coding:utf8 -*-
#
# 2014-2-13 by Victor
# Copyright 2014 Tubban
from _module._base_m_ import BaseModel
from _module._lib.common import Common

class ProfilerModel(BaseModel):
    
    
    def __init__(self, uid = None):
        self._business_table = 'business'
        self._profiler_lock_table = 'op_user_profile_lock'
        self._profiler_log_table = 'op_user_profile_log'
        self._profiler_report = 'op_profile_report'
        self._user_table = 'auth_user'
        
    def get_profiler_statistic(self):
        sql = "SELECT COUNT(a.b_uuid) AS total, a.uid, b.username " \
                " FROM %s a " \
                " LEFT JOIN %s b on b.id=a.uid group by a.uid" % \
                (self._profiler_log_table, self._user_table)
        return self.get_rows(sql)
    
    def get_profiler_reports(self):
        sql = "SELECT a.*, b.name as restaurant_name from %s a left join business b on b.id=a.business_id order by a.add_time asc" % self._profiler_report 
        return self.get_rows(sql)
    
    # 获取一个符合条件的busineee
    def filt_business(self, w_sql):
        sql = "SELECT * FROM %s WHERE %s order by id asc limit 1" % (self._business_table, w_sql)
        return self.get_one(sql)
    
    def is_locked_by_profiler(self, uuid):
        #print "--Delete Lock--"
        #print uuid
        #sql = "DELETE FROM %s WHERE add_time< %d" % (self._profiler_lock_table, Common.get_current_time() - 3*3600)
        #print self.execute(sql)
        sql = "SELECT * FROM %s WHERE `b_uuid`='%s' LIMIT 1" % (self._profiler_lock_table, uuid)
        return True if self.get_one(sql) is not None else False
    
    # 
    def get_locked_business(self, uid):
        sql = "SELECT b.name, b.uuid, b.address, b.city, b.website " \
                " FROM %s a" \
                " LEFT JOIN %s b ON b.uuid=a.b_uuid " \
                " WHERE a.uid=%d limit 1" % (self._profiler_lock_table, self._business_table, uid)
        return self.get_one(sql)
    
    
    def get_log_by_buuid(self, buuid):
        sql = "SELECT * FROM %s WHERE b_uuid='%s'" % (self._profiler_log_table, buuid)
        return self.get_one(sql)
    
    
    def lock_business(self, uid, uuid):
        sql = "REPLACE INTO %s(`uid`,`b_uuid`,`add_time`) VALUES(%d, '%s', %d)" % \
            (self._profiler_lock_table, uid, uuid, Common.get_current_time())
        return self.execute(sql)[0]
    
    def unlock_business(self, uid, uuid):
        sql = "DELETE FROM %s WHERE uid=%d and b_uuid='%s'" % \
                (self._profiler_lock_table, uid, uuid)
        return self.execute(sql)[0]
    
    def finish_edit(self, uuid, uid, has_menu):
        self.unlock_business(uid, uuid)
        sql = "REPLACE INTO %s(`uid`,`b_uuid`,`add_time`, `add_date`, `has_menu`) VALUES(%d, '%s', %d, '%s', %d)" % \
                (self._profiler_log_table, uid, uuid, Common.get_current_time(), Common.get_current_datestr(), has_menu)
        return self.execute(sql)[0]
    
    def get_logs_by_profier(self, uid):
        sql = "SELECT b.name, b.name_cn, b.uuid, b.address, b.city, b.website, b.description_cn, a.add_date, a.verify, a.verify_note, a.has_menu  " \
                " FROM %s a" \
                " LEFT JOIN %s b ON b.uuid=a.b_uuid " \
                " WHERE a.uid=%d order by a.add_time desc" % (self._profiler_log_table, self._business_table, uid)
        return self.get_rows(sql)
    
    
    def get_pager_logs_by_profiler(self, pager, uid):
        size = pager['ps']
        offset = size*(pager['p']-1)
        
        where_sql = ' WHERE a.uid=%d ' % uid
        count_sql = "SELECT count(1) as total FROM %s a " % self._profiler_log_table + where_sql
        count =  self.get_one(count_sql)['total']
        if count<>0:
            se_sql = "SELECT b.name, b.name_cn, b.uuid, b.address, b.city, b.website, b.description_cn, a.add_date, a.verify, a.verify_note, a.has_menu " \
                        " FROM %s a" \
                        " LEFT JOIN %s b ON b.uuid=a.b_uuid " \
                        " %s " \
                        " order by a.add_time desc " \
                        " limit %s,%s"  \
            % (self._profiler_log_table, self._business_table, where_sql, offset, size)
            rows = self.get_rows(se_sql)
            return dict(total=count, data=rows)
        else:
            return dict(total=0, data=[])
    
    def report_business(self, fields):
        report = {
            'business_id': {'type':'d', 'required':1},
            'uuid': {'type':'s', 'required':1},
            'profiler': {'type':'d', 'required':1},
            'profiler_name' : {'type':'s', 'required':1}, 
            'message' : {'type':'s', 'required':1}, 
            'add_time': {'type':'d', 'required':1},
        }
        ret = self._args_handle('insert', fields, report)               
        if not ret[0]:
            return ret
        return self._insert(self._profiler_report, report)
    
    def mod(self, b_uuid, args):
        log = {
            'verify': {'type':'d'},
            'verify_note': {'type':'s'},
        }   
        if not b_uuid:
            return False

        ret = self._args_handle('update', args, log)               
        if not ret[0]:
            return False
        where = "b_uuid='%s'" % b_uuid
        ret = self._update(self._profiler_log_table, log, where)
        if not ret[0]:
            return False
        return True
    
    #################
    def add(self, price):
        sql = "INSERT INTO %s(`portionunit_id`,`price`,`currency_id`,`num`,`target_id`,`target_type`) values(%d,%s,%d,'%s',%d,%d) " \
                % (self._price_table,price['portionunit_id'],price['price'],price['currency_id'],price['num'],price['target_id'],price['target_type'])
        return self.execute(sql)
    
    
    def get_by_target(self, target_type, target_id, field='EN'):
        currency_field = 'EN'
        if field<>'CN' and field<>'EN':
            currency_field = 'EN'
        sql = "SELECT a.*,b.%s as currency_name,b.iso_code as currency_iso_code,c.%s as portionunit_name FROM %s a " \
                " LEFT JOIN %s b on b.id=a.currency_id " \
                " LEFT JOIN %s c on c.id=a.portionunit_id " \
                " WHERE a.target_type=%s and a.target_id=%s " \
                % (currency_field, field, self._price_table, \
                   self._currency_table, self._portionunit_table, target_type, target_id)
        return self.get_rows(sql)
    
    def get_by_id(self, id, field='EN'):
        currency_field = 'EN'
        if field<>'CN' and field<>'EN':
            currency_field = 'EN'
        sql = "SELECT a.*,b.%s as currency_name,b.iso_code as currency_iso_code,c.%s as portionunit_name FROM %s a " \
                " LEFT JOIN %s b on b.id=a.currency_id " \
                " LEFT JOIN %s c on c.id=a.portionunit_id " \
                " WHERE a.id=%d " \
                % (currency_field, field, self._price_table, \
                   self._currency_table, self._portionunit_table, id)
        return self.get_one(sql)
    
    def delete_by_target(self, target_type, target_id):
        sql = "DELETE FROM %s WHERE target_type=%s and target_id=%s" \
                % (self._price_table, target_type, target_id)
        return self.execute(sql)[0]
        
    def delete_by_id(self, id):
        sql = "DELETE FROM %s WHERE id=%s" \
                % (self._price_table, id)
        return self.execute(sql)[0]
    
class SalerModel(BaseModel):
    
    def __init__(self, uid = None):
        self._business_table = 'business'
        self._sale_log_table = 'op_user_sale_log'
        self._sale_report = 'op_sale_report'
        self._user_table = 'auth_user'
        
        
    def add_log(self, fields):
        log = {
            'b_uuid': {'type':'s', 'required':1},
            'uid': {'type':'d', 'required':1},
            'b_id': {'type':'d', 'required':1},
            'status': {'type':'d', 'default':0},
            'note': {'type':'s', 'default':''},
            'uid': {'type':'d', 'required':1},
            'add_time': {'type':'d', 'default':Common.get_current_time()},
        }
        ret = self._args_handle('insert', fields, log)               
        if not ret[0]:
            return ret
        return self._insert(self._sale_log_table, log)
        
    def del_log(self, b_uuid, uid):
        sql = "DELETE FROM %s " \
                " WHERE b_uuid='%s' and uid=%d " % \
                (self._sale_log_table, b_uuid, uid)
        return self.execute(sql)[0]
        
        
    def has_sale_log(self, uuid):
        sql = "SELECT COUNT(1) AS total " \
                " FROM %s a WHERE a.b_uuid='%s'" % \
                (self._sale_log_table, uuid)
        if self.get_one(sql)['total'] > 0:
            return 1
        return 0
        
    def get_saler_statistic(self):
        sql = "SELECT COUNT(a.b_uuid) AS total, a.uid " \
                " FROM %s a " \
                " group by a.uid" % \
                (self._sale_log_table)
                
        rows = self.get_rows(sql)
        
        for one in rows:
            one['username'] = self.get_one("SELECT username FROM %s WHERE id=%d" % (self._user_table, one['uid']))['username']
        return rows
    
    def get_saler_reports(self):
        sql = "SELECT a.*, b.name as restaurant_name from %s a left join business b on b.id=a.business_id order by a.add_time asc" % self._saler_report 
        return self.get_rows(sql)
    
    def get_logs_by_saler(self, uid):
        sql = "SELECT b.id, b.uuid, b.name, b.name_cn, b.description, b.description_cn, b.city, b.mobile, b.phone, b.phone2, a.* " \
                " FROM %s a" \
                " LEFT JOIN %s b ON b.uuid=a.b_uuid " \
                " WHERE a.uid=%d order by a.add_time desc" % (self._sale_log_table, self._business_table, uid)
        return self.get_rows(sql)
    
    def get_pager_logs_by_saler(self, pager, uid):
        size = pager['ps']
        offset = size*(pager['p']-1)
        
        where_sql = ' WHERE a.uid=%d ' % uid
        count_sql = "SELECT count(1) as total FROM %s a " % self._sale_log_table + where_sql
        count =  self.get_one(count_sql)['total']
        if count<>0:
            se_sql = "select b.id, b.uuid, b.name, b.name_cn, b.description, b.description_cn, b.city, b.mobile, b.phone, b.phone2, a.* " \
                        " FROM %s a" \
                        " LEFT JOIN %s b ON b.uuid=a.b_uuid " \
                        " %s " \
                        " order by a.add_time desc " \
                        " limit %s,%s"  \
            % (self._sale_log_table, self._business_table, where_sql, offset, size)
            rows = self.get_rows(se_sql)
            return dict(total=count, data=rows)
        else:
            return dict(total=0, data=[])

    def get_log_by_uuid(self, uuid):
        sql = "SELECT * " \
                " FROM %s a" \
                " WHERE b_uuid='%s' limit 1" % (self._sale_log_table, uuid)
        return self.get_one(sql)
    
    def mod_log(self, args):
        log = {
            'b_uuid': {'type':'s', 'required':1},
            'uid': {'type':'d', 'required':1},
            'b_id': {'type':'d', 'required':1},
            'status': {'type':'d', 'default':0},
            'note': {'type':'s', 'default':''},
            'uid': {'type':'d', 'required':1},
        }   
        if not args.has_key('b_uuid'):
            return False

        ret = self._args_handle('update', args, log)               
        if not ret[0]:
            return False
        
        where = "b_uuid='%s'" % (args['b_uuid'])
        ret = self._update(self._sale_log_table, log, where)
        if not ret[0]:
            return False
        return True
