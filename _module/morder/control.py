#!/usr/bin/env python2.7
#-*- coding:utf8 -*-
#
# 2013-12-4 by Victor
# Copyright 2013 Tubban
from _module import const
from _module._base_c_ import BaseControl
from _module._lib.common import Common
from _module._lib.generator import Generator
from _module._lib.lang import Lang
from _module._lib.log import Log
from _module._lib.sms import SMS
from _module.business.model import BusinessModel
from _module.meal.model import MealModel
from _module.morder.model import MealOrderModel, MealTicketModel
from _module.push.control import PushControl
from _module.restaurant.model import RestaurantModel
from _module.sys_data.model import SysdataModel
from _module.user.model import UserModel
import json

class MealOrderControl(BaseControl):
    def __init__(self, uid = None,userLang=None):
        self._uid = uid
        self._mealModel = MealModel(self._uid)
        self._bModel = BusinessModel(self._uid)
        self._oModel = MealOrderModel(self._uid)
        self._uModel = UserModel(self._uid)
        self._mealOrderModel = MealOrderModel(self._uid)
        self._mealTicketModel = MealTicketModel(self._uid)
        self._rModel = RestaurantModel(self._uid)
        self._sdModel = SysdataModel()
        self._field = Lang.get_db_field_name(userLang)
        
    def get_detail(self, id):
        order = self._oModel.get_by_id(id)
        order = self._detail(order)
        return order

    def get_list_by_servant(self, servant, start, end):
        return []
    
    def mod(self, order):
        return self._oModel.mod(order)
    
    def make_refund(self, order_id, reasion_type=const.MealOrder.REFUND_REASION_TYPE_OTHER, reasion=""):
        meal_order = self.get_by_id(order_id)
        if not meal_order or meal_order['status'] <> const.MealOrder.STATUS_PAYED:
            return False
        
        refund_order = {
            "pay_order_id": meal_order['pay_order_id'],
            "reasion_type": reasion_type,
            "reasion": reasion
        }
        
        
        _mod_meal_order = {
            "id": order_id,
            "status": const.MealOrder.STATUS_REFUNDING
        }
        
        if not self.mod(_mod_meal_order):
            Log.critical("Modify meal order to status refund error: %s" % json.dumps(_mod_meal_order))
            return False
    
    def do_order_payed(self, order_id):
        
        meal_order = self._mealOrderModel.get_by_id(order_id)
        if not meal_order:
            return False
        # 防止重复生成团购券
        if meal_order['status'] not in [const.MealOrder.STATUS_UNPAYED, const.MealOrder.STATUS_PAYED_NOT_CONFIRMED]:
            return True
        
        # 修改订单为已支付
        _meal_order = {
            "id": order_id,
            "status": const.MealOrder.STATUS_PAYED,
            "payed": 1,
            "payed_time": Common.get_current_time()
        }
        if not self.mod(_meal_order):
            return False
        
        meal = self._mealModel.get_by_id(meal_order['meal_id'])
        if not meal:
            return False
        
        _tickets = []
        for i in range(meal_order['meal_num']):
            ticket = {
                'sequence': Generator.gen_ticket(meal_order['r_id']),
                'order_id': meal_order['id'],
                'meal_id': meal_order['meal_id'],
                'uid': meal_order['uid'],
                'username': meal_order['username'],
                'r_id': meal_order['r_id'],
                'status': const.MealTicket.STATUS_NOT_USED,
                'validity_from': meal['nt_validity_from'],
                'validity_to': meal['nt_validity_to'],
                'price': meal['d_price'],
                'currency_id': meal['currency_id']
            }
            self._mealTicketModel.add(ticket)
            _tickets.append(ticket['sequence'])
            
        # 修改套餐购买数
        self._mealModel.add_order_num(meal_order['meal_id'], 1)
        
        if len(_tickets) > 0:
            # 发送短信
            # TODO 推送短信, 暂时不剥离
            user = self._uModel.get_brief_user_by_id(meal_order['uid'], ['mobile_code', 'mobile'])
            if user['mobile'].strip() <> '':
                msg = {
                  "type": const.PUSH.CODE_MOBILE_CHECK,
                  "code": "push_mobile_check",
                  "receiver": 0,
                  "content": "您已成功购买途伴团购券，序号：%s。团购信息：%s %s。如有疑问请拨打01062985368" % (','.join(_tickets), meal_order['r_name'], meal['name_cn']),
                  "extra": json.dumps({"mobile_code": user['mobile_code'], "mobile": user['mobile']})
                }
                PushControl().push_one(msg)
        return True
        
        """
        meal_order = self.get_by_id(order_id)
        if not meal_order:
            return False
        
        _meal_order = {
            "id": meal_order['id'], 
            "status": const.MealOrder.STATUS_PAYED, 
            "payed": 1, 
            "payed_time": Common.get_current_time()
        }
        if not self.mod(_meal_order):
            return False
        
        for i in range(meal_order['meal_num']):
            ticket = {
                'sequence': Generator.gen_ticket(meal_order['r_id']),
                'order_id': meal_order['id'],
                'meal_id': meal_order['meal_id'],
                'uid': meal_order['uid'],
                'username': meal_order['username'],
                'r_id': meal_order['b_id'],
                'status': const.MealTicket.STATUS_NOT_USED
            }
            self._mealTicketModel.add(ticket)
        
        return True
        """

    """
    def _format(self, order):
        list = ["add_time", "arrive_time", "used_time", "payed_time"]
        for one in list:
            if order.has_key(one):
                if order[one] <> 0:
                    order[one] = Common.seconds_to_str(order[one])
                else:
                    order[one] = '-'
        return order
    """
    def get_pager_list_by_restaurant(self, pager, business_id, status=const.MealOrder.STATUS_PAYED):
        data = self._oModel.get_pager_list_by_restaurant(pager, business_id, status)
        list = data['data']
        for one in list:
            one['meal'] = self._mealModel.get_brief_by_id(one['meal_id'])
        data['data'] = list
        return data
    
    def submit(self, order):
        return self._mealOrderModel.add(order)
        
    """
    # type: 0 未支付 1 未消费  2 已消费 3 待评价
    """
    def get_my_pager_list(self, pager, type=None):
        if type is None or type == -1:
            data = self._mealOrderModel.get_my_pager_list(pager, self._uid, status=None)
        elif type in [0, 1, 2]:
            data = self._mealOrderModel.get_my_pager_list(pager, self._uid, status=type)
        # 待评价
        elif type == 3:
            data = self._mealOrderModel.get_my_pager_list(pager, self._uid, status_comment=1)
        for one in data['data']:
            self._detail(one)
        
        return data

    def _detail(self, order):
        order['meal'] = self._mealModel.get_brief_by_id(order['meal_id'])
        order['meal']['has_like'] = 0
        if self._uid is not None and self._mealModel.has_like(order['meal']['id'], self._uid):
            order['meal']['has_like'] = 1
                
        order['currency'] = self._sdModel.get_currency(order['currency'], self._field)
        return order
        
    def detail(self, id):
        order = self._mealOrderModel.get_by_id(id)
        if order:
            order['business'] = self._bModel.get_brief_by_id(order['r_id'])
            order['meal'] = self._mealModel.get_by_id(order['meal_id'])
            order['meal']['has_like'] = 0
            if self._uid is not None and self._mealModel.has_like(order['meal']['id'], self._uid):
                order['meal']['has_like'] = 1
            order['tickets'] = self._mealTicketModel.get_all_by_meal_order(order['id'])
            order['currency'] = self._sdModel.get_currency(order['currency'], self._field)
            
        return order
        
    def get_by_sequence(self, sequence):
        order = self._mealOrderModel.get_by_sequence(sequence)
        if not order:
            return None
        return order
    
    def get_by_id(self, id):
        order = self._mealOrderModel.get_by_id(id)
        if not order:
            return None
        return order
    
    def get_brief_by_id(self, id):
        fields = ['id', 'meal_id', 'price', 'title', 'currency', 'meal_num', 'status', 'r_id']
        order = self._mealOrderModel.get_by_fields(id, fields)
        if not order:
            return None
        order['currency'] = self._sdModel.get_currency(order['currency'], self._field)
        return order
    
    def get_detail_by_sequence(self, sequence):
        order = self._oModel.get_by_sequence(sequence)
        if not order:
            return None
        order = self._format(order)
        order['items'] = self._oModel.get_order_items(order['id'])
        for one in order['items']:
            one = self._format_item(one)
        return order
    
    """
    Func: 根据消费的ticket，更新order状态和ticket已使用数量
    """
    def update_ticket(self, order_id):
        order = self._mealOrderModel.get_by_id(order_id)
        if not order:
            return False
        used_cnt = self._mealTicketModel.get_used_cnt_by_orderid(order_id)
        if used_cnt <= 0:
            return True
        
        _order = {
            "id": int(order_id),
            "used_time": Common.get_current_time(),
            "used_num": used_cnt,
        }
        # 如果券全部消费则更新订单状态为已消费
        if used_cnt == order['meal_num']:
            _order['status'] = const.MealOrder.STATUS_CONSUMED
        # 如果券使用数大于0且订单没有评价则设置定贷状态为“待评价”
        if used_cnt > 0 and order['status_comment'] <> const.MealOrder.STATUS_COMMENT_SUBMITED:
            _order['status_comment'] = const.MealOrder.STATUS_COMMENT_WAITING
        return self._mealOrderModel.mod(_order)
    
    
class MealTicketControl(BaseControl):
    
    def __init__(self, uid = None,userLang=None):
        self._uid = uid
        self._uModel = UserModel(self._uid)
        self._ticketModel = MealTicketModel(self._uid)
        self._orderModel = MealOrderModel(self._uid)
        self._mealModel = MealModel(self._uid)
        self._bModel = BusinessModel(self._uid)
        self._sdModel = SysdataModel()
        self._field = Lang.get_db_field_name(userLang)
        
        self._orderControl = MealOrderControl(self._uid)
        
    def add(self, ticket):
        return self._ticketModel.add(ticket)
    
    def get_by_sequence(self, r_id, sequence):
        return self._ticketModel.get_by_sequence(r_id, sequence)
    
    def get_all_by_meal_order(self, order_id):
        return self._ticketModel.get_all_by_meal_order(order_id)

    def is_valid_by_sequence(self, r_id, sequence):
        ticket = self._ticketModel.get_by_sequence(r_id, sequence)
        if not ticket \
            or ticket['status'] <> const.MealTicket.STATUS_NOT_USED:
            return False
        return True
    
    def frozon_by_sequence(self, r_id, sequence):
        ticket = self._ticketModel.get_by_sequence(r_id, sequence)
        if not ticket:
            return False
        return self._ticketModel.mod(ticket['id'], {"status": const.MealTicket.STATUS_FROZEN})
        
    def is_valid(self, r_id, ticket_id):
        ticket = self._ticketModel.get_by_id(ticket_id)
        if not ticket \
            or ticket['r_id'] <> r_id \
            or ticket['status'] <> const.MealTicket.STATUS_NOT_USED:
            return False
        return True
    
    def get_detail(self, ticket_id):
        ticket = self._ticketModel.get_brief_by_id(ticket_id)
        if not ticket:
            return None
        ticket['meal'] = self._mealModel.get_brief_by_id(ticket['meal_id'])
        return ticket
    
    def get_detail_by_sequence(self, r_id, sequence):
        ticket = self._ticketModel.get_by_sequence(r_id, sequence)
        if not ticket:
            return None
        ticket['meal'] = self._mealModel.get_brief_by_id(ticket['meal_id'])
        ticket['meal']['currency'] = self._sdModel.get_currency(ticket['meal']['currency_id'], self._field)
        return ticket
    
    """
    Func: 通过某个ticket id获取此用户下所有的可用的同类型（meal_id）的ticket
    """
    def get_all_unused_list_by_id(self, ticket_id):
        """
        ticket = self._ticketModel.get_by_id(ticket_id)
        if not ticket:
            return []
        
        meal_id = ticket['meal_id']
        order_id = ticket['order_id']
        """
        pass
        
    def consume_by_sequence(self, r_id, sequence):
        ticket = self._ticketModel.get_by_sequence(r_id, sequence)
        if not ticket:
            return False
        _ticket = {"status": const.MealTicket.STATUS_USED, "used_time": Common.get_current_time()}
        ret = self._ticketModel.mod(ticket['id'], _ticket)
        if not ret:
            return False
        self._orderControl.update_ticket(ticket['order_id'])
        
        # 发送短信
        try:
            user = self._uModel.get_brief_user_by_id(ticket['uid'], ['mobile_code', 'mobile'])
            if user['mobile'].strip() <> '':
                msg = {
                  "type": const.PUSH.CODE_MOBILE_CHECK,
                  "code": "push_mobile_check",
                  "receiver": 0,
                  "content": "您的途伴团购券%s已经消费，感谢您的支持。" % (sequence),
                  "extra": json.dumps({"mobile_code": user['mobile_code'], "mobile": user['mobile']})
                }
                PushControl().push_one(msg)
        except Exception as e:
            Log.critical("Send ticket consume sms error. %s" % str(e))

        return True

    def get_pager_list_for_restaurant(self, pager, r_id):
        data = self._ticketModel.get_pager_list_by_restaurant(pager, r_id, status=const.MealTicket.STATUS_USED)
        for one in data['data']:
            one['meal'] = self._mealModel.get_brief_by_id(one['meal_id'])
            one['meal']['currency'] = self._sdModel.get_currency(one['meal']['currency_id'], self._field) 
        return data
    
    def get_my_pager_list(self, pager, status):
        data = self._ticketModel.get_pager_list_by_user(pager, self._uid, status)
        for one in data['data']:
            one['meal'] = self._mealModel.get_brief_by_id(one['meal_id'])
            one['currency'] = self._sdModel.get_currency(one['meal']['currency_id'], self._field)
        return data

    ########### For Op
    def get_unsettled_pager_list_by_restaurant(self, pager, b_id):
        data = self._ticketModel.get_unsettled_pager_list_by_restaurant(pager, b_id)
        for one in data['data']:
            one['currency'] = self._sdModel.get_currency(one['currency_id'], self._field) 
            one['used_time'] = Common.seconds_to_str(one['used_time'], const.Date_Format.DATETIME)
        return data
    
    def get_unsettled_count_by_restaurant(self, b_id):
        return self._ticketModel.get_unsettled_count_by_restaurant(b_id)
        
    def get_all_by_bill(self, bill_id):
        return self._ticketModel.get_all_by_bill(bill_id)
    
    ########### For MDS
    def get_pager_log_list(self, pager):
        data = self._ticketModel.get_pager_log_list(pager)
        for one in data['data']:
            one['currency'] = self._sdModel.get_currency(one['currency_id'], self._field) 
            one['used_time'] = Common.seconds_to_str(one['used_time'], const.Date_Format.DATETIME)
            one['add_time'] = Common.seconds_to_str(one['add_time'], const.Date_Format.DATETIME)
            one['meal'] = self._mealModel.get_brief_by_id(one['meal_id'])
            one['business'] = self._bModel.get_by_fields(one['r_id'], ['name', 'address', 'phone', 'uuid'])
        return data
        
        