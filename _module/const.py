#!/usr/bin/env python2.7
#-*- coding=utf8 -*-

class Operation(object):
    
    DEL = -1
    UPDATE = 0
    ADD = 1
    
'''
    DB 常量
'''
class DB(object):
    
    SORT_ASC = 'ASC'
    SORT_DESC = 'DESC'
    
    OP_LIKE = 'like' #小写
    OP_IN = 'in'#小写
    OP_NOTIN = 'not in'#小写
    OP_GT = '>' 
    OP_LT = '<'
    OP_GTEQ = '>='
    OP_LTEQ = '<='
    OP_NOTEQ = '<>'
    OP_AND = '&'
    

class Date_Format(object):
    DATE = '%Y-%m-%d'
    DATE2 = '%Y/%m/%d'
    TIME = '%H:%M:%S'
    DATETIME = '%Y-%m-%d %H:%M:%S'
    DATETIME2 = '%Y-%m-%d %H:%M'
    DATETIME3 = '%Y%m%d%H%M%S'
