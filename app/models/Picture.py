#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
-------------------------------------------------

    @   Author  :       pengj
    @   date    :       2019/12/8 14:44
    @   IDE     :       PyCharm
    @   GitHub  :       https://github.com/JackyPJB
    @   Contact :       pengjianbiao@hotmail.com
-------------------------------------------------
    Description :       
-------------------------------------------------
"""
import datetime

from app.models import db

__author__ = 'Max_Pengjb'


class Picture(db.Document):
    creator = db.StringField(max_length=255, verbose_name='上传者，创建人 id')
    url = db.StringField(max_length=512, required=True, verbose_name='smms图床url', unique=True)

    # 本地也保存的时候用，我们这里姑且保存一下吧
    image = db.ImageField(verbose_name='图片', thumbnail_size=(200, 200, True))
    img_name = db.StringField(max_length=128, verbose_name='图片名称')
    img_type = db.StringField(max_length=64, verbose_name='图片type')
    family = db.StringField(max_length=64, verbose_name='分类', default='商品图')
    create_time = db.DateTimeField(default=datetime.datetime.now, verbose_name='创建时间')

    def __unicode__(self):
        return self.img_name + '-' + self.smms_url
