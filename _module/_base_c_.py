#!/usr/bin/env python2.7
#-*- coding:utf8 -*-
################################################################################
#
# Copyright (c) 2015 Tubban.com, Inc. All Rights Reserved
#
################################################################################
"""
Base Control Module.

Authors: cuirixin(rixin.cui@tubban.com)
Date:    2014/01/01
"""

class BaseControl(object):  

    def _filter_fields(self, target, fields):
        _target = {}
        for key in fields:
            if key in target:
                _target[key] = target[key]
        return _target
        
        