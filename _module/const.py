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
    
    B_LIKE_USER_SPLIT = 20000
    B_LIKE_SPLIT = 10000
    SN_MESSAGE_SPLIT = 20000
    SN_FRIEND_SPLIT = 10000
    FRIEND_SPLIT = 10000
    MESSAGE_SPLIT = 10000
    INVITATION_USER_SPLIT = 300000
    INVITATION_USER_USER_SPLIT = 20000
    B_COMMENT_SPLIT = 10000
    R_MEAL_LIKE_SPLIT = 10000
    R_MEAL_LIKE_USER_SPLIT = 20000
    R_MEAL_COMMENT_SPLIT = 10000
    R_TABLE_SPLIT = 10000
    B_NEWS_REPLY_SPLIT = 50000
    B_NEWS_LIKE_SPLIT = 50000
    
    DISH_LIKE_USER_SPLIT = 20000


class Date_Format(object):
    DATE = '%Y-%m-%d'
    DATE2 = '%Y/%m/%d'
    TIME = '%H:%M:%S'
    DATETIME = '%Y-%m-%d %H:%M:%S'
    DATETIME2 = '%Y-%m-%d %H:%M'
    DATETIME3 = '%Y%m%d%H%M%S'
    
    
class Common(object):
    
    SOURCE_TYPE_CUSTOM = 1 # 商户添加
    SOURCE_TYPE_OPERATE = 2 # 运维添加
    SOURCE_TYPE_CRAWLED = 3 # 爬取
    SOURCE_TYPE_UGC = 4 # UGC


'''
   用户相关常量
'''
class User(object):
    
    STATUS_UNVERIFY = -1 #未验证
    #STAT_CELLPHONE_UNVERIFY = 0 #手机号未验证
    STATUS_EMAIL_UNVERIFY = 1 #未激活
    STATUS_NORMAL = 2 #状态正常
    STATUS_FORBIDDEN = 3 #封禁
    STATUS_DESTROYED = 4 #删除
    
    REG_PLAT_WEB = 'Web'  # Web平台注册
    REG_PLAT_IOS = 'IOS' # IOS平台注册
    REG_PLAT_AND = 'Android' # Android平台注册
    
    THIRDPART_ACCOUNT_TYPE_WEIXIN = 1 #微信账号
    
    SEX_UNKOWN = -1
    SEX_WOMAN = 0
    SEX_MAN = 1
    
    GROUP_SUPER_ADMIN = 1
    GROUP_ADMIN = 2  # 商户
    GROUP_EMPLOYEE = 3
    GROUP_NORMAL = 4
    GROUP_GUEST = 5
    GROUP_MENUER = 11
    GROUP_PROFILE = 12
    GROUP_DISHER = 13
    GROUP_SALE = 14
    GROUP_TRANSLATOR = 15
    GROUP_TOPIC_MANAGER = 16
    
    SOURCE_NORMAL = 1
    SOURCE_CLAIM = 2
    SOURCE_FACEBOOK = 3
    SOURCE_MOBILE_IMPORT = 4
    SOURCE_WEIXIN = 5
    
'''
         角色常量
'''
class Role(object):
    
    TYPE_SYS = 0
    TYPE_RESTAURANT = 1000
    TYPE_HOTEL = 2000
    TYPE_SHOP = 3000
    STATUS_VALID = 1
    STATUS_DELETE = 2
    STATUS_FORBIDDEN = 3

'''
         名称相关常量
'''
class Name(object):

    STATUS_DELETED = -1
    STATUS_NEW = 0
    STATUS_TRANSLATING = 1
    STATUS_LOCKED = 10
    
'''
   Business相关常量
'''
class Business(object):
    
    #STAT_CELLPHONE_UNVERIFY = 0 #手机号未验证
    CATEGORY_HOTEL = 1
    CATEGORY_SHOP = 2
    CATEGORY_RESTAURANT = 3
    
    STATUS_DELETE = 0
    STATUS_VALID = 1 # 有效可见，
    STATUS_NOT_VERIFIED = 2 # 商户店铺信息修改需运维审核，   STATUS_VALID和STATUS_NOT_VERIFIED以后与payed一起决定对一般用户是否可见
    STATUS_UNCLAIMED = 5 # 未认领
    STATUS_CLAIMED = 6 # 已认领未审核
    
    STATUS_NOT_OPENED = 10 # 一个特殊状态，不开放
    
    PORTIONUNIT_GROUP_NONE = 0 # 无分组
    PORTIONUNIT_GROUP_DISH = 1 # 菜品类
    PORTIONUNIT_GROUP_BEVERAGE = 2 # 饮料类
    
class Dish(object):
    STATUS_VALID = 1
    STATUS_DELETE = -1
    
class DishGroup(object):
    STATUS_VALID = 1
    STATUS_DELETE = -1

class Image(object):
    STATUS_VALID = 1
    STATUS_DELETE = -1
    
class Price(object):
    TYPE_DISH = 1 # Dish Price
    TYPE_SETMEAL = 2 # Setmeal Price TO DELETE
    TYPE_BEVERAGE = 3 # BEVERAGE Price
    
class Discover(object):
    STATUS_DELETE = 0
    STATUS_VALID = 1
    
class Invitation(object):
    
    STATUS_VALID = 1
    STATUS_DELETE = -1
    STATUS_CANCELED= 2
    
    TYPE_EAT_BREAKFAST = 1
    TYPE_EAT_LUNCH = 2
    TYPE_EAT_DINNER = 3
    TYPE_EAT_DRINK = 4
    
    TYPE_NUM_SINGLE = 1
    TYPE_NUM_MULTIPLE = 2
    
    TYPE_SEX_MAN = 1
    TYPE_SEX_WOMAN = 2
    TYPE_SEX_ANYONE = 3
    
    TYPE_PAY_MYTRAIT = 1
    TYPE_PAY_YOURTRAIT = 2
    TYPE_PAY_AA = 3
    TYPE_PAY_DEPENDS = 4
    
    TYPE_VISIBLE_FRIEND_ONLY = 1
    TYPE_VISIBLE_STRANGER_ONLY = 2
    TYPE_VISIBLE_ANYONE = 3
    
class NotificationMessage(object):
    
    INVITATION_CANCELD = "Invitation is canceld."
    INVITATION_DELETED = "Invitation is deleete."
    INVITATION_ACCEPTED = 'Accept your invitation request'
    INVITATION_QUIT = "Quit your invitation."
    
class ApplyFriend(object):
    
    STATUS_UNHANDLED = 0
    STATUS_ACCEPT = 1
    STATUS_REJECT = 2
    STATUS_IGNORE = 3

class InvitationUser(object):
    
    STATUS_DELETE = -1
    STATUS_UNHANDLED = 0
    STATUS_ACCEPT = 1
    STATUS_REJECT = 2
    STATUS_IGNORE = 3

# 套餐
class Meal(object):
    STATUS_DELETE = -1
    STATUS_VALID = 1
    STATUS_SOLDOUT = 2
    
    CATEGORY_SETMEAL = 1 # 一般套餐
    CATEGORY_COUPON = 2 # 优惠券
    
    PREORDER_TYPE_NONE = 0 # 无需预约
    PREORDER_TYPE_PHONE = 1 # 电话预约
    
    
class Topic(object):
    STATUS_DELETE = -1
    STATUS_INVISIBLE = 0 # 
    STATUS_VALID = 1

# 套餐订单
class MealOrder(object):
    
    STATUS_DELETE = -1
    STATUS_UNPAYED = 0
    STATUS_PAYED = 1 # 已支付／未消费
    STATUS_CONSUMED = 2 # 已消费
    STATUS_PAYED_NOT_CONFIRMED = 5 # 支付处理中
    
    STATUS_REFUNDING = 8 # 正在退款
    STATUS_REFUND = 10 # 已退款
    
    
    STATUS_COMMENT_NOT_ALLOWED = 0 # 不允许评价 （订单没使用）
    STATUS_COMMENT_WAITING = 1 # 待评价（有一个券已使用）
    STATUS_COMMENT_SUBMITED = 2 # 已评价
    
    #STATUS_PAYED_NOT_USED = 1
    #STATUS_PAYED_USED = 2
    #STATUS_PAYED_ASK_RETURN = 3
    #STATUS_PAYED_RETURNED = 4
    
    REFUND_REASION_TYPE_OTHER = 1
    REFUND_NOT_CONSUMED = 2
    
class Bill(object):
    
    STATUS_DELETE = -1 # 暂时未用到，如果删除，涉及到其他业务逻辑
    STATUS_UNSETTLED = 0
    STATUS_SETTLED = 1
    
    TYPE_PRODUCT = 1 # 团购产品账单
    # TODO 其他账单
    
class MealTicket(object):
    
    STATUS_DELETE = -1
    STATUS_FROZEN = -2 # 冻结，退款中等情况下为此状态
    STATUS_OUT_OF_DATE = 0
    STATUS_NOT_USED = 1
    STATUS_USED = 2

class Ticket(object):
    TYPE_MEAL = 1

class Message(object):
    
    TYPE_APPLY_FOR_FRIEND = 1
    TYPE_APPLY_FOR_FRIEND_RESPONSE = 2
    TYPE_RESTAURANT_INVITATION = 11
    TYPE_RESTAURANT_INVITATION_RESPONSE = 12
    TYPE_RESTAURANT_INVITATION_NOTIFICATION = 13
    
    STATUS_DELETE = -1
    STATUS_UNHANDLED = 0
    STATUS_ACCEPT = 1
    STATUS_REJECT = 2
    STATUS_IGNORE = 3
    
    HANDLE_TYPE_ACCEPT = 1
    HANDLE_TYPE_REJECT = 2
    HANDLE_TYPE_IGNORE = 3
    HANDLE_TYPE_DELETE = -1
    
'''
   Restaurant Order 相关常量
'''
class ROrder(object):

    TYPE_ORDER = 1     # 店内点餐
    TYPE_BOOKING = 2   # 预定
    TYPE_DELIVERY = 3  # 外卖
    TYPE_MEAL = 4      # 套餐  （套餐订单单独维护了）
    
    #-1: 已取消   0: 未处理  5：下单  10：结账  15：正常关闭，中间预留做扩展，但状态码保持流程顺序
    STATUS_DELETE = -1
    STATUS_QRCODE_GENERATED = 1  # 二维码已创建， 用户仍可以修改订单
    STATUS_GRABBED_BY_WAITER = 2 # 被餐厅服务员扫描锁定, 锁定，不能修改
    STATUS_SUBMIT = 5
    STATUS_CLOSE = 15  # Payed and close
    
class ROrderItem(object):
    pass
    
'''
   Restaurant Order 相关常量
'''
class PayOrder(object):

    #0: 支付中  1：支付成功  2：支付失败
    STATUS_INVALID = -1
    STATUS_DOING = 0
    STATUS_SUCCESS = 1
    STATUS_FAIL = 2
    
    CHARGE_STATUS_NOT_EXIST = -2
    CHARGE_STATUS_INVALID = -1
    CHARGE_STATUS_PAYING = 0
    CHARGE_STATUS_PAID = 1
    CHARGE_STATUS_PAY_FAILED = 2
    
    SOURCE_PINGPP = 1
    SOURCE_WEIXIN = 2
    
    TYPE_ALIPAY = 1
    TYPE_WINXIN = 2
    TYPE_BFB = 3
    TYPE_UPACP = 4
    TYPE_UPMP = 5
    TYPE_YEEPAY = 6
    TYPE_APPLEPAY = 7
    
    """
    alipay:支付宝手机支付
    alipay_wap:支付宝手机网页支付
    alipay_qr:支付宝扫码支付
    apple_pay:Apple Pay
    bfb:百度钱包移动快捷支付
    bfb_wap:百度钱包手机网页支付
    upacp:银联全渠道支付（2015 年 1 月 1 日后的银联新商户使用。若有疑问，请与 ping++ 或者相关的收单行联系）
    upacp_wap:银联全渠道手机网页支付（2015 年 1 月 1 日后的银联新商户使用。若有疑问，请与 ping++ 或者相关的收单行联系）
    upmp:银联手机支付（限个人工作室和 2014 年之前的银联老客户使用。若有疑问，请与 ping++ 或者相关的收单行联系）
    upmp_wap:银联手机网页支付（限个人工作室和 2014 年之前的银联老客户使用。若有疑问，请与 ping++ 或者相关的收单行联系）
    wx:微信支付
    wx_pub:微信公众账号支付
    wx_pub_qr:微信公众账号扫码支付
    yeepay_wap:易宝移动端网页支付
    """
    
    CHANNELS = ['alipay', 
                'alipay_wap',
                'alipay_qr',
                'apple_pay', 
                'bfb',
                'bfb_wap',
                'upacp',
                'upacp_wap',
                'upmp',
                'upmp_wap',
                'wx',
                'wx_pub',
                'wx_pub_qr',
                'yeepay_wap']
    
    CHANNEL_ALIPAY = ['alipay', 'alipay_wap', 'alipay_qr', 'apple_pay']
    CHANNEL_APPLEPAY = ['apple_pay']
    CHANNEL_BFB = ['bfb', 'bfb_wap']
    CHANNEL_UPACP = ['upacp', 'upacp_wap']
    CHANNEL_UPMP = ['upmp', 'upmp_wap']
    CHANNEL_WEIXIN = ['wx', 'wx_pub', 'wx_pub_qr']
    CHANNEL_YEEPAY = ['yeepay_wap']
    
class RefundOrder(object):

    #0: 退款中  1：退款成功  2：退款失败
    STATUS_INVALID = -1
    STATUS_DOING = 0
    STATUS_SUCCESS = 1
    STATUS_FAIL = 2

class Bnews(object):
    
    STATUS_VALID = 1
    STATUS_DELETE = -1
    
class BnewsReply(object):
    
    STATUS_VALID = 1
    STATUS_DELETE = -1
    
class Version(object):
    
    PUBLIC_DATA = 'public_data'
    
class MessageQueue(object):

    TARGET_TYPE_EMAIL = 1 # Email
    TARGET_TYPE_MOBILE = 2 
    
    STATUS_STAY = 0  # 等待确认是否发送消息
    STATUS_UNSEND = 1 
    STATUS_SEND = 2

class Claim(object):
    
    STATUS_NEW = 1
    STATUS_AGREE = 2
    STATUS_REJECT = 3
    
class Carte(object):
    STATUS_VALID = 1
    STATUS_DELETE = -1
    
class CarteSource(object):
    
    STATUS_DELETE = -1
    STATUS_UNHANDLED = 0
    STATUS_UPLOADING = 1
    STATUS_UPLOADED = 2 
    STATUS_REFUSED = 3
    
class PUSH(object):
    TYPE_NOT_SET = 0
    TYPE_NOTIFICATION = 1
    TYPE_PHONE_MESSAGE = 2
    TYPE_EMAIL = 3
    
    # PUSH码命名只涉及到业务名称，不涉及到PUSH的方式，比如email或者短信等
    CODES = ['push_rorder_taken', 'push_mobile_check', 'push_claim_success', 'push_info_alert']
    
    CODE_RESTAURANT_ORDER_TAKEN = 'push_rorder_taken'
    CODE_MOBILE_CHECK = 'push_mobile_check'  # 验证码短信, 通知短信等等。
    CODE_CLAIM_SUCCESS = "push_claim_success"
    CODE_INFO_ALERT = "push_info_alert"
    
class ThirdpartAccount(object):
    TYPE_WEIXIN = 1

#################################################

class Log_Msg:
    #business 数据库操作日志信息
    BUSINESS_ADD_SUC = "business add success!"
    BUSINESS_EDIT_SUC = "business edit success!"
    BUSINESS_DEL_SUC =  "business delete success!"
    BUSINESS_ADD_FAILED = "business add failed!"
    BUSINESS_EDIT_FAILED = "business edit failed!"
    BUSINESS_DEL_FAILED = "business delete failed!"
    
    #shop数据库操作日志信息
    SHOP_ADD_BEGIN = "begin to add shop!"
    SHOP_ADD_SUC = "shop add success!"
    SHOP_ADD_FAILED = "shop add failed!"
    
    SHOP_EDIT_BEGIN = "begin to edit shop!"
    SHOP_EDIT_SUC = "shop edit success!"
    SHOP_EDIT_FAILED = "shop edit failed!"
    
    SHOP_DEL_BEGIN = "begin to DELETE shop!"
    SHOP_DEL_SUC =  "shop delete success!"
    SHOP_DEL_FAILED = "shop delete failed!"