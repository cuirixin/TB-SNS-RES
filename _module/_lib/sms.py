#-*- coding:utf8 -*-

'''
Created on 2015-05-19
@author: cuirixin
'''
from _module._lib.common import Common
class SMS(object):
    
    def __init__(self, url, params):  
        self.url = url
        self.params = params
        
    def send(self, mobile, content):
        self.params['mobile'] = mobile
        self.params['content'] = content
        return Common.sendPostRequest(self.url, self.params)
        
        
    