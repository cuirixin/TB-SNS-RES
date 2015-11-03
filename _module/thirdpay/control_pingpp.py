#!/usr/bin/env python2.7
#-*- coding:utf8 -*-
#
# 2014-2-9 by Victor
# Copyright 2014 Tubban
from _module import const
from _module._base_c_ import BaseControl
from _module._lib.common import Common
from _module._lib.lang import Lang
from _module._lib.log import Log
import ConfigParser
import json
import os
import pingpp

CURRENT_PATH = os.path.dirname(__file__)
class PingppControl(BaseControl):
    def __init__(self, debug=False):
        self.cf = ConfigParser.ConfigParser() 
        #read config
        self.cf.read(CURRENT_PATH+"/../config_src/pingpp.conf") 
        self._APPID = self.cf.get("auth", "APPID")
        if debug:
            self._APIKEY = self.cf.get("auth", "APPKEY_TEST")
        else:
            self._APIKEY = self.cf.get("auth", "APPKEY_LIVE")
        
        pingpp.api_key = self._APIKEY
    
    """
    Func: 创建Pingpp订单
    @param order_no order_type, 同时确定一个订单, 使用时用“_”拼接
    @param amount: 订单总金额, 单位为对应币种的最小货币单位，例如：人民币为分（如订单总金额为 1 元，此处请填 100）
    @param client_ip: 发起请求的ip
    @param currency: 
    """
    def make_charge(self, order_no, channel, amount, client_ip, subject='Tubban Goods', body='Tubban Goods. Meals', extra={}):
        try:
            currency = 'cny' # 目前pingpp仅支持人民币
            ch = pingpp.Charge.create(
                order_no = order_no,
                amount = int(amount),
                app = dict(id=self._APPID),
                channel = channel,
                currency = currency,
                client_ip = client_ip,
                subject = subject,
                body = body,
                extra = extra
            )
        except Exception, e:
            Log.critical(str(e))
            return [False, None]
        return [True, ch]
    
    
    def retrieve_charge(self, charge_id):
        try:
            ch = pingpp.Charge.retrieve(charge_id)
        except Exception, e:
            Log.critical(str(e))
            return [False, str(e)]
        return [True, ch]
    
    def retrive_fund(self, charge_id, refund_id):
        
        try:
            ch = pingpp.Charge.retrieve(charge_id)
            re = ch.refunds.retrieve(refund_id)
        except Exception, e:
            Log.critical(str(e))
            return [False, str(e)]
        return [True, re]
    
    def make_refund(self, charge_id, amount, description = "Refund"):
        try:
            ch = pingpp.Charge.retrieve(charge_id)
            if description.strip() == '':
                description = "Refund"
            re = ch.refunds.create(description=description, amount=amount)
        except Exception, e:
            Log.critical(str(e))
            return [False, str(e)]
        return [True, re]
    
    
    def get_charge_status(self, charge_id):
        
        ret = self.retrieve_charge(charge_id)
        if not ret[0]:
            if ret[1].find('No such charge'):
                return const.PayOrder.CHARGE_STATUS_NOT_EXIST
            return const.PayOrder.CHARGE_STATUS_INVALID
        
        ch = ret[1]
        
        if ch.has_key('paid'):
            if ch['paid'] == True:
                return const.PayOrder.CHARGE_STATUS_PAID
            elif ch['paid'] == False:
                if ch['time_expire'] - ch['created'] > 3600:
                    return const.PayOrder.CHARGE_STATUS_PAY_FAILED
        else:
            return const.PayOrder.CHARGE_STATUS_INVALID
        
if __name__ == "__main__":
    #print PingppControl().make_charge(Common.gen_order_id('m'), "wx_pub", 2000, "127.0.0.1", extra={"open_id":"ogXRDs7yYlUkXE2AM_lpyA3xDf9o"})
    print PingppControl(debug=True).retrive_fund("ch_nb1uTKHmHenL80OSi1OyzfLK", "re_jr10a5yjHaXDmzzr1GDCuv14")
    #print PingppControl(debug=True).make_refund("ch_e1SmX9enDO4S00a5m5XrvnjD", 1500, "dddd")
    
    
