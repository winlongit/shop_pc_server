#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
-------------------------------------------------

    @   Author  :       pengj
    @   date    :       2019/12/9 22:18
    @   IDE     :       PyCharm
    @   GitHub  :       https://github.com/JackyPJB
    @   Contact :       pengjianbiao@hotmail.com
-------------------------------------------------
    Description :      Serializer处理,把mongodb查询的结果转成可以序列化的字典
    主要就是针对他里面的 objectid 不能序列化的问题
-------------------------------------------------
"""
import bson

__author__ = 'Max_Pengjb'


# 自定义函数
# 序列化处理，排除指定字段
def m2d_exclude(obj, *args):
    model_dict = obj.to_mongo().to_dict()
    if args:
        list(map(model_dict.pop, list(args)))
    for k, v in model_dict.items():
        if isinstance(v, bson.objectid.ObjectId):
            model_dict[k] = str(v)
    return model_dict


def m2d(obj):
    model_dict = obj.to_mongo().to_dict()
    # print(model_dict)
    # print(type(model_dict))
    for k, v in model_dict.items():
        # print(k, v)
        if isinstance(v, bson.objectid.ObjectId):
            model_dict[k] = str(v)
    return model_dict


# 序列化处理，只返回特定字段
def m2d_fields(obj, *args):
    model_dict = obj.to_mongo().to_dict()
    if args:
        fields = [i for i in model_dict.keys() if i not in list(args)]
        list(map(model_dict.pop, fields))
    for k, v in model_dict.items():
        if isinstance(v, bson.objectid.ObjectId):
            model_dict[k] = str(v)
    return model_dict
