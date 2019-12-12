#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
-------------------------------------------------

    @   Author  :       pengj
    @   date    :       2019/11/25 22:25
    @   IDE     :       PyCharm
    @   GitHub  :       https://github.com/JackyPJB
    @   Contact :       pengjianbiao@hotmail.com
-------------------------------------------------
    Description :       
-------------------------------------------------
"""
from flask import jsonify

__author__ = 'Max_Pengjb'


def trueReturn(data, msg):
    return jsonify({
        "status": "success",
        "message": "success",
        "code": "200",
        "result": data,
        "msg": msg,
        "success": True
    })


def falseReturn(data, msg):
    return jsonify({
        "status": "failed",
        "message": "failed",
        "code": "500",
        "result": data,
        "msg": msg,
        "success": False
    })
