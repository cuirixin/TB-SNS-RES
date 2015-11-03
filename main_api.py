#!/usr/bin/env python2.7
#-*- coding:utf8 -*-
# author: victor
# Copyright 2013 Tubban

from _module._base_m_ import BaseModel
from _module._lib.log import Log
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.web import Application, StaticFileHandler
import config_api
import config_base
import sys
import tornado

urls = [

    (r'/app/user/download/([0-9a-z-A-Z.]*)[/]?', 'api.index.UserAppDownH'),
    (r"/uploads/image_ugc/(.*).jpg", 'api.image.ImageUGCRedirectH'),
    (r"/uploads/images_ugc/(.*)", StaticFileHandler, {"path": config_base.setting['upload_image_ugc']}),
    (r"/uploads/image/(.*).jpg", 'api.image.ImageRedirectH'),
    (r"/uploads/images/(.*)", StaticFileHandler, {"path": config_base.setting['upload_image']}),
    
    #(r"/uploads/discover/(.*)", StaticFileHandler, {"path": config_base.setting['upload_discover']}),
    #(r"/uploads/print/(.*)", StaticFileHandler, {"path": config_base.setting['upload_print']}),
    (r"/uploads/avator/(.*)", StaticFileHandler, {"path": config_base.setting['upload_avator']}),
    #(r"/uploads/temp/(.*)", StaticFileHandler, {"path": config_base.setting['upload_temp']}),
    
    # 上传API
    (r"/image/upload/common", 'api.image.UploadCommonH'),
    (r"/image/upload/ugc", 'api.image.UploadUGCH'),
    (r"/image/upload/avator", 'api.image.UploadAvatorH'),
    ('.*', 'api.image.PageNotFoundH'),
    
]

application = Application(
    urls,
    cookie_secret = "61oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
    login_url = "/login",
    template_path = config_base.setting['template'],
    static_path = config_base.setting['static'],
    debug = True,
    xsrf_cookies = True,
    autoescape = None,
    ui_modules = dict(),
)

if __name__ == "__main__":
    reload(sys)
    sys.setdefaultencoding("utf-8")
    Log.start(config_api.log['path'], config_api.log['level'])
    BaseModel.start()
    http_server = HTTPServer(application, xheaders = True)
    print "Start listening: %s" % str(config_api.listen_port)
    if len(sys.argv) >= 2:
        http_server.listen(int(sys.argv[1]))
    else:
        http_server.listen(config_api.listen_port)
    tornado.autoreload.start(IOLoop.instance(), 500)
    IOLoop.instance().start()

