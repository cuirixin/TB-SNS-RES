#!/usr/bin/env python2.7
#-*- coding:utf8 -*-
#
# 2014-3-25 by Victor
# Copyright 2013 Tubban
from _module._lib.common import Common

class EmailService:
    def __init__(self, uid = None, userLang=None):
        
        self._uid = uid
        self._field = 'EN'
        if userLang:
            if userLang == 'zh_CN':
                self._field = "CN"
            elif userLang == 'fr':
                self._field = 'FR'
            elif userLang == 'de':
                self._field = 'DE'
    
    """
    email Str
    password Str
    """
    def send_regist_email(self, args):
        
        content =   ('<style>'
                    '*{font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;}'
                    'b{color:green}'
                    'ti_p{ text-indent:4em; padding:0px; margin:0px; }'
                    '</style>'
                    '<div id="main" style="font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;">'
                    '<p>Welcome to <b><a href="http://b.tubban.com">tubban.com</a></b>. You can manage your restaurant menu in multi-languages for your guests.</p>' 
                    '<p>Your account:</p>'
                    '<p><b>Email/Username</b>: '+args['email']+'</p>'
                    '<p><b>Password</b>: '+args['password']+'</p>'
                    '<p><b><a href="http://b.tubban.com/login">Member Login</a></b></p>'
                    '<p><b>Create...</b></p>'
                    '<p class="ti_p">&nbsp;&nbsp;Your restaurant profile (contact info, cuisine style, etc.)</p>'
                    '<p class="ti_p">&nbsp;&nbsp;Your online menu (multi-language, mobile access, etc.)</p>'
                    '<p>Get started<p>'
                    '<p>Ask us<p>'
                    '<p>Don\'t forget we are always happy to help so feel free to contact us at any time.<p>'
                    '<br/>'
                    '<p><b>Best wishes, </b></p>'
                    '<p style="color:green">Tubban Team</p>'
                    '<br/>'
                    '<p style="color:green">Tubban GmbH</p>'
                    '<p>Neuengasse 39</p>'
                    '<p>2502 Biel/Bienne</p>'
                    '<p>Switzerland</p>'
                    '<p>+41 32 322 67 59</p>'
                    '<p>info@tubban.com</p>'
                    '</div>')

        #content = "Welcome to Tubban,Your account is："+user['email']+", password is："+user['password']+"&nbsp;<a href='http://b.tubban.com'>Enter Tubban</a>"
        try:
            flag = Common.send_mail('no-reply@tubban.com', 'chino2014', 'Tubban', [args['email']], 'Tubban User Center', content)
            if flag:
                return True
            return False
        except Exception, e:
            return False
    
    
    