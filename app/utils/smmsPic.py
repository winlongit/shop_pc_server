#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
-------------------------------------------------

    @   Author  :       pengj
    @   date    :       2019/12/8 16:30
    @   IDE     :       PyCharm
    @   GitHub  :       https://github.com/JackyPJB
    @   Contact :       pengjianbiao@hotmail.com
-------------------------------------------------
    Description :       https://sm.ms/doc/v2#277af2f2a6a9c6679bfc62a51b714c0d
    Python requests库处理 multipart/form-data 请求以及 boundary值问题,看下面
    https://blog.csdn.net/Enderman_xiaohei/article/details/89421773
-------------------------------------------------
"""
import json

__author__ = 'Max_Pengjb'

import requests


class SmmsError(Exception):
    def __init__(self, msg):
        super().__init__(self)  # 初始化父类
        self.msg = msg

    def __str__(self):
        return self.msg


class SMMSV2:
    username = 'Max_pengjb'
    password = 'sd811811'
    api_url = 'https://sm.ms/api/v2'
    login_url = api_url + '/token'
    upload_url = api_url + '/upload'

    @classmethod
    def upload(cls, image):
        # 通过账号密码获取token
        payload = {'username': cls.username, 'password': cls.password}
        r1 = requests.post(cls.login_url, params=payload)
        token_res = r1.json()
        # print(res)
        if 'success' in token_res and token_res['success']:
            token = token_res['data']['token']
            # print(token)
            upload_headers = {'Authorization': token}
            files = {'smfile': image}
            r2 = requests.post(cls.upload_url, headers=upload_headers, files=files)
            upload_res = json.loads(r2.text)
            # print("1: ", r.text)
            # print("2: ", r.json)
            # print("3: ", r.request.body)
            # print("4: ", r.request.headers)
            # print(upload_res)
            if 'code' in token_res and upload_res['code'] == 'success':
                # print(upload_res['code'], upload_res['code'] == 'success')
                # print(upload_res['data'])
                # print(upload_res['data']['url'])
                return upload_res['data']['url']
            elif 'code' in upload_res and upload_res['code'] == 'image_repeated':
                # print(upload_res['images'])
                return upload_res['images']
            else:
                raise SmmsError('sm.ms图片上传失败。请稍后再试。')
        else:
            raise SmmsError('sm.ms登录失败，获取token失败')
