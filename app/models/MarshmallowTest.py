#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
-------------------------------------------------

    @   Author  :       pengj
    @   date    :       2019/12/11 14:15
    @   IDE     :       PyCharm
    @   GitHub  :       https://github.com/JackyPJB
    @   Contact :       pengjianbiao@hotmail.com
-------------------------------------------------
    Description :       https://marshmallow-mongoengine.readthedocs.io/en/latest/tutorial.html
    marshmallow_mongoengine 初次使用尝试
-------------------------------------------------
"""

__author__ = 'Max_Pengjb'

from . import db
from flask_marshmallow import fields, Schema


class Task(db.EmbeddedDocument):
    content = db.StringField(required=True)
    priority = db.IntField(default=1)


class MarshmallowTest(db.Document):
    name = db.StringField()
    password = db.StringField(required=True)
    email = db.StringField()
    tasks = db.ListField(db.EmbeddedDocumentField(Task))


class TitleCase(fields.fields.Field):
    def _serialize(self, value, attr, obj, **kwargs):
        if not value:
            return ''
        print('1111', value)
        print('2222', attr)
        print('3333', obj)
        return str(value).title()


class MarshmallowTestSchema(Schema):
    class Meta:
        # Fields to expose
        fields = ("name", "password", "email", "tasks", "_links", "id")

    # Smart hyperlinking
    _links = fields.Hyperlinks({
        'self': fields.URLFor('marshmallowTest.test_schema', name='<name>'),
        'collection': fields.URLFor('marshmallowTest.test_schema')
    })
    id = TitleCase()
