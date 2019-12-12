#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
-------------------------------------------------

    @   Author  :       pengj
    @   date    :       2019/12/10 16:24
    @   IDE     :       PyCharm
    @   GitHub  :       https://github.com/JackyPJB
    @   Contact :       pengjianbiao@hotmail.com
-------------------------------------------------
    Description :       
-------------------------------------------------
"""
from bson import ObjectId

from app.models.Address import Address

__author__ = 'Max_Pengjb'

from flask import request, Blueprint
from app import jsonReturn
from app.utils import mongo2dict

# from flask_mongoengine.wtf import model_form

# PostForm = model_form(User)
bp = Blueprint('address', __name__, url_prefix="/api/v1/address")


@bp.route('/addressList', methods=['POST', 'GET'])
def get_add_list():
    req_json = request.json
    if not req_json:
        return jsonReturn.falseReturn(request.path, '请上传必要参数')
    user_id = req_json.get('userId')
    if not user_id:
        return jsonReturn.falseReturn(request.path, '请上传必要参数')
    #   通过 userId 来查找他对应的购物车，购物车里面只有
    res = []
    addresses = Address.objects(user_id=ObjectId(user_id)).all()
    if addresses:
        for address in addresses:
            res.append(mongo2dict.m2d(address))
    return jsonReturn.trueReturn(res, 'ok')


@bp.route('/addAddress', methods=['POST', 'GET'])
def add():
    req_json = request.json
    if not req_json:
        return jsonReturn.falseReturn(request.path, '请上传必要参数')
    user_id = req_json.get('userId')
    streetName = req_json.get('streetName')
    userName = req_json.get('userName')
    isDefault = req_json.get('isDefault')
    tel = req_json.get('tel')
    if not all([user_id, streetName, userName, isDefault is not None, tel]):
        return jsonReturn.falseReturn(request.path, '请上传必要参数')
    #  存储
    try:
        # 如果是要设置这个地址是默认地址，那么其他的就要设置为 false 了
        if isDefault:
            Address.objects(user_id=ObjectId(user_id), isDefault=True).update(set__isDefault=False)
        address = Address(user_id=ObjectId(user_id), streetName=streetName, userName=userName, isDefault=isDefault,
                          tel=tel).save()
        return jsonReturn.trueReturn(mongo2dict.m2d(address), 'ok')
    except Exception as e:
        print(e)
        return jsonReturn.falseReturn(request.path, str(e))


@bp.route('/editAddress', methods=['POST', 'GET'])
def edit():
    req_json = request.json
    if not req_json:
        return jsonReturn.falseReturn(request.path, '请上传必要参数')
    addressId = req_json.get('addressId')
    user_id = req_json.get('userId')
    streetName = req_json.get('streetName')
    userName = req_json.get('userName')
    isDefault = req_json.get('isDefault')
    tel = req_json.get('tel')
    if not all([addressId, streetName, userName, isDefault is not None, tel]):
        return jsonReturn.falseReturn(request.path, '请上传必要参数')
    #  存储
    try:
        if isDefault:
            # 那其他的就要设置为不是默认地址了
            Address.objects(user_id=ObjectId(user_id)).update(isDefault=False)
        # 返回的是修改的个数，可以使用update_one 只修改一个
        _n = Address.objects(id=ObjectId(addressId)).update(streetName=streetName, userName=userName,
                                                            isDefault=isDefault, tel=tel)
        return jsonReturn.trueReturn(_n, 'ok')
    except Exception as e:
        print(e)
        return jsonReturn.falseReturn(request.path, str(e))


@bp.route('/delAddress', methods=['POST', 'GET'])
def del_address():
    req_json = request.json
    if not req_json:
        return jsonReturn.falseReturn(request.path, '请上传必要参数')
    addressId = req_json.get('addressId')
    if not addressId:
        return jsonReturn.falseReturn(request.path, '请上传必要参数 addressId')
    #  存储
    try:
        address = Address.objects(id=ObjectId(addressId)).delete()
        return jsonReturn.trueReturn(address, 'ok')
    except Exception as e:
        print(e)
        return jsonReturn.falseReturn(request.path, str(e))
