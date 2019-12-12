#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
-------------------------------------------------

    @   Author  :       pengj
    @   date    :       2019/12/11 14:42
    @   IDE     :       PyCharm
    @   GitHub  :       https://github.com/JackyPJB
    @   Contact :       pengjianbiao@hotmail.com
-------------------------------------------------
    Description :       
-------------------------------------------------
"""
from pprint import pprint

from bson import ObjectId

from app.models.MarshmallowTest import MarshmallowTestSchema
from app.models.UserOrder import UserOrder

__author__ = 'Max_Pengjb'

from flask import request, Blueprint, jsonify

bp = Blueprint('marshmallowTest', __name__, url_prefix="/api/v1/marshmallowTest")


@bp.route('/test', methods=['POST', 'GET'])
def test_schema():
    user_order = UserOrder.objects(id=ObjectId("5defb0e49f64adc8308d559f")).first()
    testSchema = MarshmallowTestSchema()
    # u = testSchema.load(
    #     {"name": "John Doe", "email": "jdoe@example.com", "password": "123456", "tasks": [{"haha": "hehe"}],
    #      "id": "wo shi ni ma"})
    print(user_order.to_mongo())
    u = testSchema.load(user_order.to_mongo().to_dict())
    print(type(u))
    print(u['tasks'][0])
    print(u)
    print(jsonify(u))
    # testSchema.dump(u) 才能通过 MarshmallowTestSchema 中自定义的操作返回一个结果的 dict（）
    # 然后再使用 jsonify 往 header 中添加 application/json 才表示返回的事 json
    print(testSchema.dump(u))
    return jsonify(testSchema.dump(u))
