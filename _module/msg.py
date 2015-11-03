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
    
    # Sys Warning
    EXCHANGE_RATE_WARNING = 10001
    
    # 1-50 Format Error
    
    FORMATE_MOBILE_ERROR = 1
    
    # User 
    USER_NOT_BOUNDED_WITH_THIRDPART_ACCOUNT = 98
    USER_HAS_REGIST = 99 # 已经通过验证
    USER_MOBILE_DYNAMIC_CODE_ERROR = 100
    USER_WRONG_PASSWD = 101 #用户密码错误
    USER_ALREADY_EXISTS = 102 #用户已存在
    USER_LOGIN_ERROR = 103 #用户名或者密码错误
    USER_EMAIL_EXISTS = 104 #email已经使用
    USER_MOBILE_EXISTS = 105 # mobile已使用
    USER_EMAIL_ERROR = 106 # email 不匹配
    USER_MOBILE_ERROR = 107 # mobile不匹配
    USER_NOT_EXIST = 108 # 用户不存在
    
    
    
    
    # Business
    BUSINESS_UUID_USED = 110 # Business UUID已被使用
    BUSINESS_NOT_EXIST = 111
    BUSINESS_PUBLIC_DATA_IS_UPDATED = 112
    
    # Dish
    DISH_NUMBER_EXIST = 201 # 菜品编号已存在
    DISH_NOT_EXIST = 202 # 菜品不存在
    DISH_ALREADY_LIKED = 203 # 菜品已点赞
    
    
    SETMEAL_NUMBER_EXIST = 211 # 套餐编号已存在

    # Message
    MSG_DEL_ERROR = 301#删除消息失败
    MSG_PROCCESS_ERROR = 302#处理消息失败
    MSG_POST_ERROR = 303 #消息发送失败
    
    # Dishgroup
    DISHGROUP_EXIST = 401

    # File
    FILE_UNSUPPORT_FORMAT = 501 #不支持的图片类型
    
    # Menu
    MENU_IS_UPDATED = 601
    
    # Invitation
    INVITATION_DOES_NOT_EXIST = 701
    INVITATION_WAS_DELETED = 702
    
    # Business News
    BNEWS_DOES_NOT_EXIST = 801
    BNEWS_WAS_DELETED = 802
    
    # Restaurant Table
    RESTAURANT_TABLE_EXIST = 901
    
    # Meal
    MEAL_TICKET_INVALID = 1001
    
    # Meal Order
    MEAL_ORDER_NOT_EXIST = 1101
    MEAL_ORDER_HAS_PAIED = 1102
    MEAL_ORDER_NOT_ALLOW_TO_REFUND = 1103
    
    # Meal 
    MEAL_NOT_EXIST = 1201
    
    
    #
    
class API_Desc:

    SYS_OK='Success.' # 执行成功
    SYS_TOKEN_ERROR='Secure Token Error.' # 参数校验失败
    SYS_ACCESS_EXPIRES='Access expired.' # Session过期或失效
    SYS_PARAM_ERROR='Params error.' # 输入参数错误
    SYS_INTERNAL_ERROR='System internal error.' # 系统内部错误，请稍后再试
    SYS_NO_PERMISSION = 'No permission' # 没有权限
    SYS_NO_DATA = 'No Data' # 没有权限
    
    EXCHANGE_RATE_WARNING = "Exchange rate warning."
    
    
    FORMATE_MOBILE_ERROR = "Mobile format error."
    
    USER_NOT_BOUNDED_WITH_THIRDPART_ACCOUNT = "No tubban account has bounded to the thirdpart account."
    USER_HAS_REGIST = "User has regist successfully. Pleas login in."
    USER_MOBILE_DYNAMIC_CODE_ERROR = "Mobile dynamic code is mismatched or out of date."
    USER_WRONG_PASSWD = 'Wrong password'
    USER_ALREADY_EXISTS = 'User already exist.'
    USER_LOGIN_ERROR = 'Username or password error.'
    USER_EMAIL_EXISTS = 'Email already exists.'
    USER_MOBILE_EXISTS = 'Mobile already exists.'
    USER_NOT_EXIST = 'User does not exist.'
    
    
    BUSINESS_UUID_USED = "Business UUID has been used, please try another one."
    BUSINESS_NOT_EXIST = "Business does not exist."
    BUSINESS_PUBLIC_DATA_IS_UPDATED = "Business is updated"
    
    DISH_NUMBER_EXIST = "Dish number is already used."
    DISH_NOT_EXIST = "Dish not exist."
    DISH_ALREADY_LIKED = "Duplicated operation."
    
    SETMEAL_NUMBER_EXIST = "Setmeal number is already used."

    MENU_IS_UPDATED = 'Menu is already the lastest version.'
    
    INVITATION_DOES_NOT_EXIST = "Invitation does not exist."
    INVITATION_WAS_DELETED = "Invitation was deleted."
    
    BNEWS_DOES_NOT_EXIST = "Business news does not exist."
    BNEWS_WAS_DELETED = "Business news was deleted."
    
    RESTAURANT_TABLE_EXIST = "Restaurant table is already exist."
    
    MEAL_TICKET_INVALID = "Meal ticket not exist or status invalid."
    
    
    MEAL_ORDER_NOT_EXIST = "Meal order not exist."
    MEAL_ORDER_HAS_PAIED = "Meal order has been paid."
    MEAL_ORDER_NOT_ALLOW_TO_REFUND = "Meal order is not available to refund."
    
    MEAL_NOT_EXIST = "Meal not exist."
    
    