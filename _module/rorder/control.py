#!/usr/bin/env python2.7
#-*- coding:utf8 -*-
#
# 2014-5-8 by Victor
# Copyright 2014 Tubban

from _module import const
from _module._base_c_ import BaseControl
from _module._lib.common import Common
from _module._lib.lang import Lang
from _module.business.model import BusinessModel
from _module.dish.model import DishModel
from _module.name.control import NameControl
from _module.price.control import PriceControl
from _module.price.model import PriceModel
from _module.rorder.model import ROrderModel
from _module.sys_data.model import SysdataModel
from _module.user.model import UserModel
import json

class ROrderControl(BaseControl):
    def __init__(self, uid = None, userLang=None):
        self._uid = uid
        self._bModel = BusinessModel(self._uid)
        self._oModel = ROrderModel(self._uid)
        self._uModel = UserModel(self._uid)
        self._dModel = DishModel(self._uid)
        self._pModel = PriceModel()
        self._sysDataModel = SysdataModel()
        
        self._pControl = PriceControl(None, userLang)
        self._nControl = NameControl(None, userLang)
        self._field = Lang.get_db_field_name(userLang)
        self._langcode = Lang.get_code_by_req_code(userLang)
    
    #-------------------Base Functions For All-----------------------
    """
    Func: 添加订单
    @param order: 
        {
             'b_uuid': u'IDMm',
             'currency_id': 1L,
             'customer_id': 38L,
             'customer_name': u'test',
             'price': 51.0,      # 实际价格
             'people_cnt': -1,   # -1 未设置
             'r_id': 828L,
             'r_name': u'Restaurant Taverne',
             'refer_code': 0,
             'sequence': '8281504142868664755854',
             'status': 0,
             'extra': '',
             'note': '',
         }
        # 如果是外卖订单，extra则还需要以下信息
        extra: {  # 订餐信息，TODO
            "contactor":"CuiRixin",# 联系人
            "phone":"18310880318",# 联系电话
            "address":"",# 送餐地址
            # 订餐相关
            "arrive_time":"18000000",# 预计到达时间（时间戳）
        }
    @param items: 菜品条目, Eg.
        [{
            'dish_id': 521L,
            'dish_name': u'TATAR',
            'num': 2,
            'price_total': 38.0,
            'price_discount': 19.0,
            'price': 19.0,
            'price_num': u'1.0',  # 38 CHF/ 1份
            'price_unit': 103L
        }]
    """
    def add(self, order, items):
        ret = self._oModel.add(order)
        if not ret[0]:
            return ret
        order_id = ret[1]
        self._oModel.add_items(order_id, items)
        return ret
    
    
    """
    Func: 通过ID获取订单概要信息
    @param order_id: 
    @return: 
    """
    def get_by_id(self, order_id):
        return self._oModel.get_by_id(order_id)
    
    """
    Func: 通过订单ID获取订单条目详细信息
    @param order_id: 
    @return: 
    """
    def _get_detail_dishes(self, order_id):
        data = self._oModel.get_dishes(order_id)
        if not data:
            return []
        
        try:
            dishes = json.loads(data['dishes'])
        except Exception as e:
            return []
            
        for one in dishes:
            dish = self._dModel.get_by_fields(one['id'], ['id', 'name', 'cover', 'price', 'price_num', 'price_unit'])
            one['id'] = dish['id']
            one['name'] = dish['name']
            one['cover'] = dish['cover']
            one['price'] = dish['price']
            one['price_num'] = dish['price_num']
            one['price_unit'] = dish['price_unit']
            name = self._nControl.get_one(dish['name'], self._langcode)
            one['name_i18n'] = ''
            if name.has_key(self._langcode):
                one['name_i18n'] = name[self._langcode]
        return dishes
    
    """
    Func: 通过订单ID获取订单条目详细信息 (暂时不用了)
    @param order_id: 
    @return: 
    """
    def _get_detail_items(self, order_id):
        _items = self._oModel.get_brief_items(order_id)
        items = []
        for one in _items:
            # num 为0的不显示
            if one['num'] <= 0:
                continue
            dish = self._dModel.get_by_id(one['dish_id'])
            item = {
                "id" : one['id'],
                "num" : one['num'],
                "dish" : {
                    "id" : dish['id'],
                    "name" : dish['name'],
                    "names" : self._nControl.get_one(dish['name'], 'all'),
                    "cover" : dish['cover'],
                    "price" : {
                        "price" : one['price'],
                        "num" : one['price_num'],
                        "portionunit_id" : one['price_unit'],
                        "price_discount" : one['price_discount'],
                    },
                },
                "price_total" : one['price_total'],
            }
            items.append(item)
        return items
    
    """
    Func: 获取用户某餐厅的未确认订单（仅有一条）
    @param order_id: 
    @return: 
    """
    def get_last_one(self, bid, uid):
        rorder = self._oModel.get_last_one(bid, uid)
        if not rorder:
            return None
        return self.get_detail_by_id(rorder['id'])

    """
    Func: 通过ID获取订单详细信息
    @param order_id: 
    @return: 
    """
    def get_detail_by_id(self, order_id):
        
        _order = self.get_by_id(order_id)
        if not _order:
            return None
        order = {}
        #order['customer'] = self._uModel.get_brief_user_by_id(_order['customer_id'])
        
        order['currency'] = self._sysDataModel.get_currency(_order['currency_id'], self._field)
        order['id'] = _order['id']
        order['add_time'] = _order['add_time']
        order['scanned_time'] = _order['scanned_time']
        order['status'] = _order['status']
        order['note'] = _order['note']
        order['refer_code'] = _order['refer_code']
        order['price'] = _order['price']
        order['last_waiter'] = {}
        if _order['waiter'] > 0:
            order['last_waiter'] = self._uModel.get_brief_user_by_id(_order['waiter'])
            
        order['dishes'] = self._get_detail_dishes(_order['id'])
        order['payment'] = {}
        return order

    """
    Func: 修改订单
    @param order_id: 
    @param order: "order_id", "people_cnt", "note"
    @return: 
    """
    def mod(self, order_id, order):
        Common.remove_none_value(order)
        
        if order.has_key('dishes') and isinstance(order['dishes'], list):
            dishes = order['dishes']
            price = 0
            for one in dishes:
                d = self._dModel.get_by_fields(one['id'], ['id', 'price'])
                price = price + d['price']
            order['price'] = price
            
            if not self._oModel.mod_dish(order_id, json.dumps(dishes)):
                return False
        
        allow_fields = ["servant", "currency_id", "people_cnt", "note", "refer_code", \
                        "status", "payed", "extra", "arrive_time", "price"]
        order = self._filter_fields(order, allow_fields)
        return self._oModel.mod(order_id, order)
    
    
    """
    Func: 修改订单条目，注意更新价格信息. 注意不删除item，num为0表示删除，而且不会在接口里返回数据
    @param order_id: 
    @param order: "order_id", "people_cnt", "note"
    @return: 
    """
    def mod_item(self, item_id, item):
        _item = self._oModel.get_brief_item_by_id(item_id)
        if not _item:
            return False
        
        allow_fields = ["num", "note", "price_total"]
        item = self._filter_fields(item, allow_fields)
        if item.has_key("num"):
            item['price_total'] = item['num'] * _item['price_discount']
        if self._oModel.mod_item(item_id, item):
            self._oModel.refresh_price(_item['order_id'])
            return True
        else:
            return False
            
    
    """
    @param items: 菜品条目, Eg.
        [{
            'dish_id': 521L,
            'dish_name': u'TATAR',
            'num': 2,
            'price_total': 38.0,
            'price_discount': 19.0,
            'price': 19.0,
            'price_num': u'1.0',  # 38 CHF/ 1份
            'price_unit': 103L
        }]
    """
    def add_items(self, order_id, items):
        if len(items) == 0:
            return True
        self._oModel.add_items(order_id, items)
        self._oModel.refresh_price(order_id)
        return True
        
    def _gen_pager_list_1(self, list):
        _list = []
        for _order in list:
            order = {}
            order['id'] = _order['id']
            order['add_time'] = _order['add_time']
            order['scanned_time'] = _order['scanned_time']
            order['status'] = _order['status']
            _currency = self._sysDataModel.get_currency(_order['currency_id'], self._field)
            order['price'] = {
                "price" : _order['price'],
                "currency_id" : _currency['id'],
                "currency_iso_code" : _currency['iso_code'],
                "currency_name" : _currency['name'],
            }
            business = self._bModel.get_brief_by_id(_order['r_id'])
            order['business'] = {
                "uuid" : business['uuid'],
                "name" : business['name'],
                "zip"  : business['zip'],
                "city_id" : business['city_id'],
                "lon"  : business['lon'],
                "lat"  : business['lat']
            }
            _list.append(order)
        return _list
    
    def _gen_pager_list_2(self, list):
        _list = []
        for _order in list:
            order = {}
            order['id'] = _order['id']
            order['add_time'] = _order['add_time']
            order['scanned_time'] = _order['scanned_time']
            order['status'] = _order['status']
            _currency = self._sysDataModel.get_currency(_order['currency_id'], self._field)
            order['price'] = {
                "price" : _order['price'],
                "currency_id" : _currency['id'],
                "currency_iso_code" : _currency['iso_code'],
                "currency_name" : _currency['name'],
            }
            business = self._bModel.get_brief_by_id(_order['r_id'])
            order['business'] = {
                "uuid" : business['uuid'],
                "name" : business['name'],
                "zip"  : business['zip'],
                "city_id" : business['city_id'],
                "lon"  : business['lon'],
                "lat"  : business['lat']
            }
            order['customer'] = self._uModel.get_brief_user_by_id(_order['customer_id'])
            order['last_waiter'] = {}
            if _order['waiter'] > 0:
                order['last_waiter'] = self._uModel.get_brief_user_by_id(_order['waiter'])
            _list.append(order)
        return _list
    
    """
    Func: 按消费者获取订单分页列表
    @param : 
    @param :
    @return: 
    """
    def get_my_orders_pager_list(self, pager, customer_id, type=1):
        ret = self._oModel.get_my_orders_pager_list(pager, customer_id, type)
        return ret
    
        
    """
    Func: 按消费者获取订单分页列表
    @param order_id: 
    @param order: "order_id", "people_cnt", "note"
    @return: 
    """
    def get_customer_orders_pager_list(self, pager, customer_id, b_uuid=None, status=0):
        ret = self._oModel.get_customer_orders_pager_list(pager, customer_id, b_uuid, status)
        ret['data'] = self._gen_pager_list_1(ret['data'])
        return ret
    
    # ----------------------Only For Client------------------------------
    
    """
    Func: 按桌号获取订单分页列表
    @param pager: 
    @param table_number
    @param b_uuid
    @param status
    @return: 
    """
    def get_table_orders_pager_list(self, pager, table_number, r_id=None, status=0):
        ret = self._oModel.get_table_orders_pager_list(pager, table_number, r_id, status)
        ret['data'] = self._gen_pager_list_2(ret['data'])
        return ret
    
    
    """
    Func: 扫描订单，下订单
    @param order_id: 
    @param order: "order_id", "people_cnt", "note"
    @return: 
    """
    def take(self, order_id, waiter_id=0, table_num=0):
        #order = self._oModel.get_by_id(order_id)
        _order = {
            "status": const.ROrder.STATUS_GRABBED_BY_WAITER, 
            "waiter": waiter_id, 
            "refer_code" : table_num,
            "scanned_time": Common.get_current_time()
        }
        if self._oModel.mod(order_id, _order):
            # TODO 触发消息，发送给用户和原waiter
            pass
            return True
        return False
    
    def untake(self, order_id, waiter_id=0, table_num=0):
        #order = self._oModel.get_by_id(order_id)
        _order = {
            "status": const.ROrder.STATUS_QRCODE_GENERATED, 
            "waiter": 0, 
            "refer_code" : 0,
            "scanned_time": 0
        }
        if self._oModel.mod(order_id, _order):
            return True
        return False
    
    # 关闭订单
    def finish(self, order_id):
        #order = self._oModel.get_by_id(order_id)
        _order = {
            "status": const.ROrder.STATUS_PAYED_AND_CLOSE, 
            "payed": 1 # TODO 其实在关闭前，应该已经支付，此处为了适应，在店内消费的情况
        }
        if self._oModel.mod(order_id, _order):
            return True
        return False
    
    
    def take_all_by_table(self, b_uuid, table_num, waiter_id=0):
        orders = self._oModel.get_unscanned_orders(b_uuid, table_num)
        for one in orders:
            _order = {
                "status": const.ROrder.STATUS_GRABBED_BY_WAITER, 
                "waiter": waiter_id, 
                "scanned_time": Common.get_current_time()
            }
            if self._oModel.mod(one['id'], _order):
                # TODO 触发消息，发送给用户和原waiter
                pass
            else:
                return False
        return True
        
    # TODO 添加权限验证
    def delete(self, order_id):
        _order = {'status': const.ROrder.STATUS_DELETE}
        return self._oModel.mod(order_id, _order)
    
    """
    Func: 获取餐厅某餐桌的当前订单
    @param r_id: 
    @param table_umber: 
    @return: order
    """
    def get_table_current_order(self, r_id, table_number):
        order = self._oModel.get_last_one_by_table(r_id, table_number)
        if not order:
            return None
        order['last_waiter'] = {}
        if order['waiter'] > 0:
            order['last_waiter'] = self._uModel.get_brief_user_by_id(order['waiter'])
        return order
    
    def get_table_unclosed_orders(self, r_id, table_number):
        orders = self._oModel.get_table_unclosed_orders(r_id, table_number)
        for order in orders:
            order['last_waiter'] = {}
            if order['waiter'] > 0:
                order['last_waiter'] = self._uModel.get_brief_user_by_id(order['waiter'])
        return orders
        
    ################################ TODO 
    
    
    
    
    def get_list_by_restaurant(self, business_id, start, end, type=0):
        list = self._oModel.get_list_by_restaurant(business_id, start, end, type)
        for one in list:
            one = self._format(one)
        return list
    
    def get_list_by_servant(self, servant, start, end):
        return []

    def _format(self, order):
        order['add_time'] = Common.seconds_to_str(order['add_time'])
        if order['arrive_time']<>0:
            order['arrive_time'] = Common.seconds_to_str(order['arrive_time'])
        else:
            order['arrive_time'] = ''
        return order

    def _format_item(self, item):
        name = NameControl().get_one(item['name'].strip(), self._langcode)
        if name.has_key(self._langcode):
            item['name'] = name[self._langcode]
        return item

    # 获取某月份订单列表
    def get_list_by_user(self, uid, start, end):
        list = self._oModel.get_list_by_user(uid, start, end)
        for one in list:
            one = self._format(one)
        return list

    def get_detail_by_sequence(self, sequence):
        order = self._oModel.get_by_sequence(sequence)
        if not order:
            return None
        order = self._format(order)
        order['items'] = self._oModel.get_order_items(order['id'])
        for one in order['items']:
            one = self._format_item(one)
        return order

    ########################### Item Temp
    def add_item_tmp(self, rid, uid, dishid, priceid, num):
        dish = self._dModel.get_detail(dishid)
        price = self._pModel.get_by_id(priceid)
        if not dish or not price:
            return False
        item = self._oModel.get_item_tmp(rid, uid, dishid)
        if item:
            if item['price_num'] == price['num'] \
                and item['price_unit'] == price['portionunit_id'] \
                and item['price'] == item['num']*price['price']:
                order_item = {
                    "id":item['id'],
                    "note":"",
                    "price":(item['num']+num)*price["price"],
                    "real_price":(item['num']+num)*price["price"],
                    "num":item['num']+num,
                }
                return self._oModel.mod_item_tmp(order_item)
            
        order_item = {
            "rid":rid,
            "uid": uid,
            "number" : dish['number'],
            "name":dish['name'],
            "refer_id":dish['id'],
            "note":"",
            "price":price["price"],
            "price_num":price["num"],
            "price_unit":price["portionunit_id"],
            "currency_iso_code":price['currency_iso_code'],
            "real_price":price["price"],
            "num":1,
        }
        return self._oModel.add_item_tmp(order_item)[0]
    
    def del_item_tmp(self, id):
        return self._oModel.del_item_tmp(id)
    
    def clear_item_tmp(self, rid, uid):
        return self._oModel.clear_item_tmp(rid, uid)

    def get_item_tmp_list(self, rid, uid):
        list = self._oModel.get_item_tmp_list(rid, uid)
        for l in list:
            l['add_time'] = Common.seconds_to_str(l['add_time'])
            l['price_unit_name'] = self._bModel.get_portionunit_by_id(l['price_unit'], self._field)['name']
            try:
                if l['refer_id']<>0:
                    l['name_i18n']  = NameControl().get_name_by_langcode(l['name'].strip(), self._langcode)
                if l['name_i18n'] == '':
                    l['name_i18n'] = l['name']
            except Exception, e:
                pass
            
        return list
    
    def mod_item_tmp_num(self, id, num):
        item = self._oModel.get_item_tmp_by_id(id)
        if not item:
            return False
        
        order_item = {
            "id":item['id'],
        }
        if item['num']+num<=0:
            return self._oModel.del_item_tmp(id)
        else:
            order_item['num'] = item['num']+num
            order_item['price'] = item['price']/item['num']*order_item['num']
            order_item['real_price'] = order_item['price']
        return self._oModel.mod_item_tmp(order_item)
    
    
