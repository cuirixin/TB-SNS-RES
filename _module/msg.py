#!/usr/bin/env python2.7
#-*- coding=utf8 -*-

class API_Code:
        
    # System
    SYS_OK = 0
    SYS_TOKEN_ERROR = -1
    SYS_ACCESS_EXPIRES = -2
    SYS_PARAM_ERROR = -3
    SYS_INTERNAL_ERROR = -4
    SYS_NO_PERMISSION = -5
    SYS_NO_DATA = -6
    
    
    
    
    #
    
class API_Desc:

    SYS_OK='Success.' # 执行成功
    SYS_TOKEN_ERROR='Secure Token Error.' # 参数校验失败
    SYS_ACCESS_EXPIRES='Access expired.' # Session过期或失效
    SYS_PARAM_ERROR='Params error.' # 输入参数错误
    SYS_INTERNAL_ERROR='System internal error.' # 系统内部错误，请稍后再试
    SYS_NO_PERMISSION = 'No permission' # 没有权限
    SYS_NO_DATA = 'No Data' # 没有权限
    
    