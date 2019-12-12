#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
-------------------------------------------------

    @   Author  :       pengj
    @   date    :       2019/12/7 15:39
    @   IDE     :       PyCharm
    @   GitHub  :       https://github.com/JackyPJB
    @   Contact :       pengjianbiao@hotmail.com
-------------------------------------------------
    Description :       
-------------------------------------------------
"""
# from mongoengine import NULLIFY

__author__ = 'Max_Pengjb'

from app.models import db

import datetime


class ProductCategory(db.Document):
    category = db.StringField(max_length=255, required=True, verbose_name='分类名', unique=True)
    level = db.IntField(required=True, default=1, verbose_name='分类级别，1 为最高级')
    # reverse_delete_rule 有五个options，
    #
    #       * DO_NOTHING (0)  - don't do anything (default).
    #       * NULLIFY    (1)  - Updates the reference to null.
    #       * CASCADE    (2)  - Deletes the documents associated with the reference.
    #       * DENY       (3)  - Prevent the deletion of the reference object.
    #       * PULL       (4)  - Pull the reference from a :class:`~mongoengine.fields.ListField` of references
    # father_id = db.ReferenceField("self", reverse_delete_rule=NULLIFY, verbose_name='父级分类，如果为空，那就说明是最高级别')
    father_category = db.StringField(max_length=255, verbose_name='父级分类，如果为空，那就说明是最高级别')
    description = db.StringField(max_length=255)
    create_time = db.DateTimeField(default=datetime.datetime.now, verbose_name='创建时间')

    def __str__(self):
        return self.category

    def __unicode__(self):
        return self.category


# class OnePicture(db.EmbeddedDocument):
# order = db.IntField(min_value=1, verbose_name="一组图片中，这张图片的序号")
# 这里需要另外的一个 Picture 来存储图片，我这里就不用 gridf 来保存图片了，直接用图床，所以这里就直接保存图床的url了
# pic_id = db.ReferenceField(Picture, verbose_name="图片在Picture表中的id")
# pic_url = db.ListField(db.StringField(max_length=1024, verbose_name='图传的图片url地址'))

# 产品model
class Product(db.Document):
    name = db.StringField(max_length=255, verbose_name='商品名称', required=True)
    title = db.StringField(max_length=255, verbose_name='小标题，吸引人看的那个', required=True)
    # description = db.StringField(max_length=255, verbose_name='商品描述')
    origin_price = db.IntField(verbose_name='原价 ，价格(整数:分)，注意单位是分', required=True)
    cur_price = db.IntField(verbose_name='现价格（折扣价）价格(整数:分)，注意单位是分', required=True)
    # 这个分类是多个的，比如 比如
    categories = db.ListField(db.StringField(max_length=255, verbose_name='分类'), default=[])
    specification = db.ListField(db.StringField(max_length=255, verbose_name="规格"), default=[])

    # list_swipers = db.ListField(db.EmbeddedDocumentField(OnePicture, verbose='轮播图list'))
    swiper_pics = db.ListField(db.StringField(max_length=1024, verbose_name='图传的图片url地址，产品主图是第一张轮播图'), default=[])
    # list_desc = db.ListField(db.EmbeddedDocumentField(OnePicture, verbose='详情图list'))
    desc_pics = db.ListField(db.StringField(max_length=1024, verbose_name='图传的图片url地址'), default=[])

    state = db.IntField(default=0, verbose_name='商品状态：1已上架，0待上架，2已下架')

    create_time = db.DateTimeField(default=datetime.datetime.now, verbose_name='创建时间')

    def __unicode__(self):
        return str(self.name)
