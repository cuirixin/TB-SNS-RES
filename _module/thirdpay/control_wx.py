#!/usr/bin/env python2.7
#-*- coding:utf8 -*-
#
# 2014-2-9 by Victor
# Copyright 2014 Tubban
from _module import const
from _module._base_c_ import BaseControl
from _module._lib.common import Common
from _module._lib.generator import Generator
from _module._lib.lang import Lang
from _module._lib.log import Log
import ConfigParser
import hashlib
import json
import os
import pingpp
import pprint

CURRENT_PATH = os.path.dirname(__file__)
class WeixinControl(BaseControl):
    def __init__(self, debug=False):
        self.cf = ConfigParser.ConfigParser() 
        #read config
        
        self.cf.read(CURRENT_PATH+"/../config_src/weixin.conf") 
        self._APPID = self.cf.get("auth", "APPID")
        self._MERCHANT_ACCOUNT = self.cf.get("pay", "MERCHANT_ACCOUNT")
        self._NOTIFY_URL = self.cf.get("pay", "NOTIFY_URL")
        self._PAY_AUTH_KEY = self.cf.get("pay", "PAY_AUTH_KEY")
        
        # 统一支付URL
        self._PAY_API_URL = self.cf.get('func-pay', "URL")
        self._QUERY_API_URL = self.cf.get('func-query', "URL")
        
    """
    ["a":1, "b":2] => a=1&b=2
    """
    def _gen_url_prams_str(self, params):
        _tmp_arr = []
        for one in params:
            if one[1] <> '':
                _tmp_arr.append("%s=%s"% (one[0], one[1]))
        return '&'.join(_tmp_arr)
    
    def _gen_sign(self, params):
        params.append(('key', self._PAY_AUTH_KEY))
        string1 = self._gen_url_prams_str(params)
        m = hashlib.md5()
        m.update(string1)
        return m.hexdigest().upper()
            
    
    """
    Func: 创建Weixin订单
    @param openid: 
    @param out_trade_no, 同时确定一个订单, 使用时用“_”拼接
    @param trade_type: 支付类型
    @param total_fee: 订单总金额, 单位为对应币种的最小货币单位，例如：人民币为分（如订单总金额为 1 元，此处请填 100）

    """
    def make_charge(self, openid, out_trade_no, trade_type, total_fee, product_id=0, spbill_create_ip='127.0.0.1', body='Tubban Goods. Meals', attach=''):
        try:
            current_time = Common.get_current_time()
            _param = {
                "appid": self._APPID,
                "mch_id": self._MERCHANT_ACCOUNT,
                "nonce_str": str(Generator.gen_random_int(6)),
                "body": body,
                "out_trade_no": str(out_trade_no),
                "total_fee": total_fee,
                "spbill_create_ip": spbill_create_ip,
                "time_start": Common.seconds_to_str(current_time, const.Date_Format.DATETIME3),
                "time_expire": Common.seconds_to_str(current_time + 60*30, const.Date_Format.DATETIME3),
                "notify_url": self._NOTIFY_URL,
                "openid": openid,
                "trade_type": trade_type,
                "product_id": product_id,
                "attach": attach
            }
            
            _sorted_param = sorted(_param.iteritems(), key=lambda d:d[0])
                        
            _param['sign'] = self._gen_sign(_sorted_param)
            
            xml_format = """<xml>
            <openid>%(openid)s</openid>
            <appid>%(appid)s</appid> 
            <attach><![CDATA[%(attach)s]]></attach>
            <body><![CDATA[%(body)s]]></body>
            <device_info></device_info>
            <mch_id>%(mch_id)s</mch_id>
            <nonce_str>%(nonce_str)s</nonce_str>
            <notify_url>%(notify_url)s</notify_url>
            <out_trade_no>%(out_trade_no)s</out_trade_no>
            <spbill_create_ip>%(spbill_create_ip)s</spbill_create_ip>
            <total_fee>%(total_fee)d</total_fee>
            <trade_type>%(trade_type)s</trade_type>
            <time_start>%(time_start)s</time_start>
            <time_expire>%(time_expire)s</time_expire>
            <product_id>%(product_id)d</product_id>
            <sign><![CDATA[%(sign)s]]></sign>
            </xml>"""
            xml_input = xml_format % _param
            xml_result = Common.sendPostBodyRequst(self._PAY_API_URL, xml_input)
            ch = Common.xmlToArray(xml_result)
            if ch["return_code"] == 'FAIL' or ch["result_code"] == 'FAIL':
                # 失败
                print ch['return_msg']

        except Exception, e:
            print str(e)
            Log.critical(str(e))
            return [False, None]
        return [True, ch]
    
    def retrieve_charge(self, out_trade_no):
        try:
            _param = {
                "appid": self._APPID,
                "mch_id": self._MERCHANT_ACCOUNT,
                "nonce_str": str(Generator.gen_random_int(6)),
                "out_trade_no": str(out_trade_no),
            }
            
            _sorted_param = sorted(_param.iteritems(), key=lambda d:d[0])
                        
            _param['sign'] = self._gen_sign(_sorted_param)
            
            xml_format = """<xml>
            <appid>%(appid)s</appid> 
            <mch_id>%(mch_id)s</mch_id>
            <nonce_str>%(nonce_str)s</nonce_str>
            <out_trade_no>%(out_trade_no)s</out_trade_no>
            <sign><![CDATA[%(sign)s]]></sign>
            </xml>"""
            xml_input = xml_format % _param
            xml_result = Common.sendPostBodyRequst(self._QUERY_API_URL, xml_input)
            ch = Common.xmlToArray(xml_result)
            if ch["return_code"] == 'FAIL' or ch["result_code"] == 'FAIL':
                # 失败
                print ch['return_msg']

        except Exception, e:
            print str(e)
            Log.critical(str(e))
            return [False, None]
        return [True, ch]
        
if __name__ == "__main__":
    print WeixinControl().make_charge(openid="ogXRDs7JvvRVhYMEKouufKMl6PRU", 
                                      out_trade_no="10000002", 
                                      trade_type="JSAPI", 
                                      total_fee=100, 
                                      product_id=102, 
                                      spbill_create_ip='127.0.0.1', 
                                      body='Tubban Goods. Meals', 
                                      attach='')
    
    print WeixinControl().retrieve_charge("10000002")
                                      
    