#!/usr/bin/env python2.7
#-*- coding:utf8 -*-
#
# 2015-5-21 by Victor
# Copyright 2014 Tubban
from _module._lib.common import Common
import json

class WeixinTool:
    
    APPID = "wx0ce819199405301d"
    APPSECRET = "f93fa5df1bb62bbdd1c92de8c2b28ecc"
    
    """
    Func: 获取access_token
    """
    @staticmethod
    def get_access_token():
        URL = "https://api.weixin.qq.com/cgi-bin/token"
        params = {
            "grant_type": "client_credential",
            "appid": WeixinTool.APPID,
            "secret": WeixinTool.APPSECRET
        }
        try:
            ret = Common.sendGetRequest(URL, params)
            ret = json.loads(ret)
        except Exception as e:
            return None
        
        if ret.has_key('access_token'):
            return ret['access_token']
        return None
    
    """
    Func: 生成qrcode ticket
    """
    @staticmethod
    def create_qrcode_ticket(scene_id, access_token, temporary=True):
        URL = "https://api.weixin.qq.com/cgi-bin/qrcode/create?access_token=%s" % access_token
        
        if temporary:
            action_name = 'QR_SCENE' # 临时二维码
        else: 
            action_name = 'QR_LIMIT_SCENE' # 永久二维码
        params = {
                    "action_name": action_name, 
                    "action_info": {
                        "scene": {
                            "scene_id": int(scene_id)
                        }
                    }
                 }
        
        try:
            ret = Common.sendPostBodyRequst(URL, json.dumps(params))
            ret = json.loads(ret)
        except Exception as e:
            return None
        
        if ret.has_key('ticket'):
            return ret
        return None
        
    @staticmethod
    def create_text_xml(FromUserName, ToUserName, Content):
        MSG_TYPE = 'text'
        MSG_TEXT_RESPONSE_TEMPLATE = "<xml><ToUserName><![CDATA[%(ToUserName)s]]></ToUserName><FromUserName><![CDATA[%(FromUserName)s]]></FromUserName><CreateTime>%(CreateTime)s</CreateTime><MsgType><![CDATA[%(MsgType)s]]></MsgType><Content><![CDATA[%(Content)s]]></Content></xml>"

        out_data = {
            "ToUserName": ToUserName,
            "FromUserName": FromUserName,
            "CreateTime": Common.get_current_time(),
            "MsgType": MSG_TYPE,
            "Content": Content
        }
        out = MSG_TEXT_RESPONSE_TEMPLATE % out_data
        return out
    
    @staticmethod
    def create_news_xml(FromUserName, ToUserName, Articles):
        MSG_TYPE = 'news'
        MSG_RESPONSE_TEMPLATE = "<xml><ToUserName><![CDATA[%(ToUserName)s]]></ToUserName><FromUserName><![CDATA[%(FromUserName)s]]></FromUserName><CreateTime>%(CreateTime)s</CreateTime><MsgType><![CDATA[%(MsgType)s]]></MsgType><ArticleCount>%(ArticleCount)s</ArticleCount><Articles>%(Articles)s</Articles></xml>"
        ArticleCount = len(Articles)
        
        ARTICLE_ITEM_TEMPLATE = "<item><Title><![CDATA[%(Title)s]]></Title><Description><![CDATA[%(Description)s]]></Description><PicUrl><![CDATA[%(PicUrl)s]]></PicUrl><Url><![CDATA[%(Url)s]]></Url></item>"
        Articles_Str = ''
        
        for one in Articles:
            item_data = {
                "Title": one['Title'],
                "Description": one['Description'],
                "PicUrl": one['PicUrl'],
                "Url": one['Url'],
            }
            Articles_Str += ARTICLE_ITEM_TEMPLATE % item_data

        out_data = {
            "ToUserName": ToUserName,
            "FromUserName": FromUserName,
            "CreateTime": Common.get_current_time(),
            "MsgType": MSG_TYPE,
            "ArticleCount": ArticleCount,
            "Articles": Articles_Str
        }
        out = MSG_RESPONSE_TEMPLATE % out_data
        return out
    
if __name__ == "__main__":
    #print WeixinTool.create_text_xml("FromUname", "ToUs", "test")
    Articles = [{
            "Title": "‘途伴’——2015最贴心的美食服务",
            "Description": "途伴致力于做您出境游的美食小秘书，用母语的温情守护你旅行中的每一餐，‘途’您吃更好，伴您省更多！！",
            "PicUrl": "https://mp.weixin.qq.com/cgi-bin/getimgdata?mode=large&source=file&fileId=207877494&token=58362506&lang=zh_CN",
            "Url": "http://mp.weixin.qq.com/s?__biz=MzAwNzU0MjQwMQ==&mid=207876835&idx=1&sn=c1302ba8dfa024b7dfc32eea6112e261#rd"
        }]
    print WeixinTool.create_news_xml("FromUname", "ToUs", Articles)
    