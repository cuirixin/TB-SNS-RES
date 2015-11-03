#-*- coding:utf8 -*-

from _module._lib.log import Log
import os
log = {
    'level' : Log.WARNING,
    'path' : os.path.join(os.path.dirname(__file__), 'logs/api'),
}
listen_port = 3333