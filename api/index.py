#!/usr/bin/env python2.7
#-*- coding:utf8 -*-
#
# 2013-1-20 by Victor
# Copyright 2013 www.Tubban.com
from api._base_ import BaseHandler
from calendar import c
from _module._lib.common import Common
import config_base
import os

class UserAppDownH(BaseHandler):
    def get(self, version):
        click_platform = self.get_platform()
        ios_url = "https://itunes.apple.com/cn/app/tubban-dining/id908747827"
        if click_platform == 'IOS':
            self.redirect(ios_url)
            return
        
        file_path = config_base.RESOURCE_PATH+"release/app/user/"+version+'.apk'
        if not os.path.isfile(file_path):
            self.write("No available app to download.")
            return
        apk_name = "tubban_user_V%s.apk" % version
        with open(file_path, "rb") as f:
            self.set_header('Content-Type','application/octet-stream')
            self.set_header("Content-Disposition", "attachment; filename=" + apk_name)
            self.write(f.read())
        