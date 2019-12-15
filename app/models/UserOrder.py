#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
-------------------------------------------------

    @   Author  :       pengj
    @   date    :       2019/12/10 20:07
    @   IDE     :       PyCharm
    @   GitHub  :       https://github.com/JackyPJB
    @   Contact :       pengjianbiao@hotmail.com
-------------------------------------------------
    Description :       订单
-------------------------------------------------
"""
from mongoengine import queryset_manager

from app.models.User import User

__author__ = 'Max_Pengjb'

import datetime

from . import db


# 一个订单里面的每一个商品的信息
class ProductOrder(db.EmbeddedDocument):
    productId = db.StringField(max_length=255, required=True, verbose_name='商品id')
    name = db.StringField(max_length=255, verbose_name='商品名称', required=True)
    title = db.StringField(max_length=255, verbose_name='小标题，吸引人看的那个', required=True)
    salePrice = db.IntField(verbose_name='价格，注意单位是 分 ！', required=True)
    productNum = db.IntField(verbose_name='购买的数量', required=True)
    productImg = db.StringField(max_length=1024, verbose_name='商品图url地址（就一张头像图）')


# 订单管理model
class UserOrder(db.Document):
    # 这个id对应的是微信的商户订单号 out_trade_no
    user_id = db.ReferenceField(User, required=True, verbose_name='用户id')

    goodsList = db.EmbeddedDocumentListField(ProductOrder, required=True, verbose_name='所有订单')
    code_url = db.StringField(max_length=512, verbose_name='微信支付的二维码链接')

    total_fee = db.IntField(verbose_name='订单总金额,单位是 分！', required=True)

    ischeck = db.BooleanField(required=True, verbose_name='支付状态', default=False)  # 已支付，未支付
    status = db.StringField(max_length=64, verbose_name='当前订单状态', default='支付中')  # 支付中，支付成功，支付关闭,待发货，已发货，待收货，订单完成
    # 收件人信息
    userName = db.StringField(max_length=255, verbose_name='收货人姓名', required=True)
    tel = db.StringField(max_length=64, verbose_name='收货人手机号', required=True)
    streetName = db.StringField(max_length=1024, verbose_name='收货人地址', required=True)

    create_time = db.DateTimeField(default=datetime.datetime.now, verbose_name='创建时间')

    @queryset_manager
    def live_posts(doc_cls, queryset):
        # 使用 UserOrder.live_posts().first()  这里这个自定义的 live_posts 类似于 objects() 的用法
        return queryset.filter(status='支付中')

    def __unicode__(self):
        return str(self.user_id)
