#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
-------------------------------------------------

    @   Author  :       pengj
    @   date    :       2019/12/9 20:47
    @   IDE     :       PyCharm
    @   GitHub  :       https://github.com/JackyPJB
    @   Contact :       pengjianbiao@hotmail.com
-------------------------------------------------
    Description :       购物车
-------------------------------------------------
"""

__author__ = 'Max_Pengjb'

from app.models import db
from app.models.User import User
from app.models.Product import Product


class Cart(db.Document):
    user_id = db.ReferenceField(User, required=True, verbose_name='用户id')
    product_id = db.ReferenceField(Product, required=True, verbose_name='商品id')
    checked = db.IntField(default=1, required=True, verbose_name='是否被选中 1 选中 0 没有选中')
    productNum = db.IntField(default=0, required=True, verbose_name='选中的商品的数量')

    def __unicode__(self):
        return str(self.user_id) + str(self.product_id)
