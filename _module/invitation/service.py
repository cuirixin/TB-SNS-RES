#!/usr/bin/env python2.7
#-*- coding:utf8 -*-
#
# 2014-3-25 by Victor
# Copyright 2013 Tubban

class InvitationService(object):
    
    def __init__(self, uid = None,userLang=None):
        self._uid = uid
