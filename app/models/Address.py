#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
-------------------------------------------------

    @   Author  :       pengj
    @   date    :       2019/12/10 15:45
    @   IDE     :       PyCharm
    @   GitHub  :       https://github.com/JackyPJB
    @   Contact :       pengjianbiao@hotmail.com
-------------------------------------------------
    Description :       
-------------------------------------------------
"""
import datetime

__author__ = 'Max_Pengjb'

from app.models import db
from app.models.User import User


class Address(db.Document):
    user_id = db.ReferenceField(User, required=True, verbose_name='用户id')
    streetName = db.StringField(max_length=512, required=True, verbose_name='地址')
    userName = db.StringField(max_length=128, required=True, verbose_name='收货人姓名')
    tel = db.StringField(max_length=64, required=True, verbose_name='收货人手机号')
    isDefault = db.BooleanField(default=False, required=True, verbose_name='是否默认地址')

    create_time = db.DateTimeField(default=datetime.datetime.now, verbose_name='创建时间')

    def __unicode__(self):
        return str(self.streetName) + str(self.userName)
