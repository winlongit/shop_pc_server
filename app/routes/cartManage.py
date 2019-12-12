#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
-------------------------------------------------

    @   Author  :       pengj
    @   date    :       2019/11/25 21:53
    @   IDE     :       PyCharm
    @   GitHub  :       https://github.com/JackyPJB
    @   Contact :       pengjianbiao@hotmail.com
-------------------------------------------------
    Description :       
-------------------------------------------------
"""
import time

# from flask_wtf import csrf
from bson import ObjectId

from app.models.Cart import Cart
from app.models.Product import Product

__author__ = 'Max_Pengjb'

from flask import request, Blueprint
from app import jsonReturn
from app.utils import mongo2dict

# from flask_mongoengine.wtf import model_form

# PostForm = model_form(User)
bp = Blueprint('cart', __name__, url_prefix="/api/v1/cart")


@bp.route('/cartList', methods=['POST'])
def get():
    req_json = request.json
    if not req_json:
        return jsonReturn.falseReturn(request.path, '请上传必要参数')
    user_id = req_json.get('userId')
    if not user_id:
        return jsonReturn.falseReturn(request.path, '请上传必要参数')
    #   通过 userId 来查找他对应的购物车，购物车里面只有
    carts = Cart.objects(user_id=ObjectId(user_id))
    res = []
    for cart in carts:
        prod = mongo2dict.m2d(cart)
        prod_info = Product.objects(id=prod['product_id']).first()
        if prod_info:
            prod.update(mongo2dict.m2d(prod_info))
        res.append(prod)
    print(res)
    return jsonReturn.trueReturn(res, 'ok')


@bp.route('/add', methods=['POST'])
def add():
    req_json = request.json
    if not req_json:
        return jsonReturn.falseReturn(request.path, '请上传必要参数')
    user_id = req_json.get('userId')
    product_id = req_json.get('productId')
    productNum = req_json.get('productNum')
    if not user_id or not product_id or not productNum:
        return jsonReturn.falseReturn(request.path, '请上传必要参数')
    try:
        """
        http://docs.mongoengine.org/guide/querying.html
        set – set a particular value
        unset – delete a particular value (since MongoDB v1.3)
        inc – increment a value by a given amount
        dec – decrement a value by a given amount
        push – append a value to a list
        push_all – append several values to a list
        pop – remove the first or last element of a list depending on the value
        pull – remove a value from a list
        pull_all – remove several values from a list
        add_to_set – add value to a list only if its not in the list already
        """
        # upsert_one Overwrite or add the first document matched by the query.
        # http://docs.mongoengine.org/apireference.html#mongoengine.queryset.QuerySet.upsert_one
        rs = Cart.objects(user_id=ObjectId(user_id), product_id=ObjectId(product_id)).upsert_one(
            inc__productNum=productNum, set__checked=1)
        return jsonReturn.trueReturn(rs, 'ok')
    except Exception as e:
        return jsonReturn.falseReturn('', str(e))


@bp.route('/edit', methods=['POST'])
def edit():
    req_json = request.json
    if not req_json:
        return jsonReturn.falseReturn(request.path, '请上传必要参数')
    user_id = req_json.get('userId')
    product_id = req_json.get('productId')
    productNum = req_json.get('productNum')
    checked = req_json.get('checked')
    # 这里 checked 是 0 和 1，当时 0 的时候 not checked 就是 true 了，不要这么判断
    if not user_id or not product_id or not productNum or checked is None:
        return jsonReturn.falseReturn(request.path, '请上传必要参数')
    try:
        # upsert_one Overwrite or add the first document matched by the query.
        # http://docs.mongoengine.org/apireference.html#mongoengine.queryset.QuerySet.upsert_one
        rs = Cart.objects(user_id=ObjectId(user_id), product_id=ObjectId(product_id)).upsert_one(
            set__productNum=productNum, set__checked=checked)
        return jsonReturn.trueReturn(mongo2dict.m2d(rs), 'ok')
    except Exception as e:
        return jsonReturn.falseReturn('', str(e))
