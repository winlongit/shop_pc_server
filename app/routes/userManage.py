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

__author__ = 'Max_Pengjb'

from flask import request, g, Blueprint
from app.models.User import User, Permission
from app import jsonReturn
from app.utils.jwt import JWT

# from flask_mongoengine.wtf import model_form

# PostForm = model_form(User)
bp = Blueprint('auth', __name__, url_prefix="/api/v1/user")


@bp.route('/register', methods=['POST'])
def register():
    """
    用户注册
    :return: json
    """
    # form = PostForm(request.form)
    # 跨域就出现问题，我真的是服了这个 flask_mongoengine， bug是真的多
    #  解决前后端分离 'csrf_token': ['The CSRF token is missing.'] 问题
    # TODO 不用 form 传数据，省掉这些麻烦把，直接 json ，然后还可以用 mongo 的 fromjson 的 orm
    # form.csrf_token.data = csrf.generate_csrf()
    # if form.validate():
    #     print(form)
    # else:
    #     print(form.errors)
    #     return jsonReturn.falseReturn('', form.errors)
    # username = request.form.get('username')
    # password = request.form.get('password')
    req_json = request.json
    username = req_json.get('userName')
    password = req_json.get('userPwd')
    if not username or not password:
        return jsonReturn.falseReturn('', '用户名和密码不能为空')
    if User.objects(username=username).first():
        return jsonReturn.falseReturn('', '用户名已存在')
    user = User.register(username, password)
    # 这里User的password做了特别处理，需要加密保存，单独写了方法新建用户
    # password 是通过@property 和 @property.setter 来定义的，真正的 password 是 _password
    print(user.to_mongo())
    if user.id:
        returnUser = {
            'id': str(user.id),
            'username': user.username
        }
        g.username = username
        return jsonReturn.trueReturn(returnUser, "用户注册成功")
    else:
        return jsonReturn.falseReturn('', '用户注册失败')


@bp.route('/login', methods=['POST'])
def login():
    """
    用户登录
    :return: json
    """
    username = request.json.get('username')
    password = request.json.get('password')
    # if not username or not password:
    if not username or not password:
        return jsonReturn.falseReturn('', '用户名和密码不能为空')
    else:
        userInfo = User.objects(username=username).first()
        if userInfo is None:
            return jsonReturn.falseReturn('', '找不到用户')
        else:
            if userInfo.check_password(password):
                # 这里放入 g 的原因：
                # 1.  登录之前默认的是一个临时用户，@app.before_request 为他设置了一个 g.username='__casual_user' + str(uuid_id)
                # 2.  @app.after_request 会在 header 中添加 Authorization->token，
                # 3.  生成token需要的username通过获取 g.username 来生成token的，所以这里需要将临时用户更新为登录后的用户
                g.username = userInfo.username
                # print(token,type(token))  # decode() 方法以指定的编码格式解码 bytes 对象。
                # token = JWT.encode_auth_token(userInfo.username)
                # print(token)
                # TODO 显示的在返回的结果中也传token，为了我测试的时候用，后面需要取消，统一在headers中通过Authorization来拿
                return jsonReturn.trueReturn({'id': str(userInfo.id), 'username': userInfo.username,
                                              # 'avatar': 'data:image/jpeg;base64,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'},
                                              'avatar': 'data:image/jpeg;base64,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'},
                                             '登录成功')
            else:
                return jsonReturn.falseReturn('', '密码不正确')


@bp.route('/user_info', methods=['GET'])
def get():
    """
    获取用户信息
    :return: json
    """
    return jsonReturn.trueReturn(g.username, '获取用户信息')


# 访问地址的管理
@bp.route('/admin/add_permission', methods=['POST'])
def add_permission():
    """
    访问地址的管理
    :return: json
    """
    url = request.args.get('url')
    name = request.args.get('name')
    description = request.args.get('description')
    if not url:
        return jsonReturn.trueReturn('', 'url访问路径是必须的')
    if Permission.objects(url=url).first():
        return jsonReturn.falseReturn(url, '失败：该路径权限已经存在')
    new_permission = Permission(url=url, name=name, description=description)
    new_permission.save()
    return jsonReturn.trueReturn(new_permission, '增加地址成功')


@bp.route('/admin/del_permission', methods=['POST'])
def del_permission():
    """
    获取用户信息
    :return: json
    """
    url = request.args.get('url')
    target_permission = Permission.objects(url=url).first()
    if target_permission:
        r = target_permission.delete()
        return jsonReturn.trueReturn(r, '删除路径权限')
    else:
        return jsonReturn.falseReturn('', '目标路径权限不存在')


# 角色的管理
@bp.route('/admin/add_role', methods=['POST'])
def add_role():
    """
    获取用户信息
    :return: json
    """
    url = request.args.get('url')
    request.args.get('name')
    request.args.get('description')
    if not url:
        return
    new_permission = Permission(url='/login', name='登录', description='谁都能访问')
    new_permission.save()
    return jsonReturn.trueReturn(g.username, '获取用户信息')


@bp.route('/admin/del_role', methods=['POST'])
def del_role():
    """
    获取用户信息
    :return: json
    """
    return jsonReturn.trueReturn(g.username, '获取用户信息')


# 角色权限管理
@bp.route('/admin/add_permission_to_role', methods=['POST'])
def add_permission_to_role():
    """
    获取用户信息
    :return: json
    """
    return jsonReturn.trueReturn(g.username, '获取用户信息')


@bp.route('/admin/del_permission_from_role', methods=['POST'])
def del_permission_from_role():
    """
    获取用户信息
    :return: json
    """
    return jsonReturn.trueReturn(g.username, '获取用户信息')


# 用户管理
@bp.route('/admin/add_user', methods=['POST'])
def add_user():
    """
    获取用户信息
    :return: json
    """
    return jsonReturn.trueReturn(g.username, '获取用户信息')


@bp.route('/admin/del_user', methods=['POST'])
def del_user():
    """
    获取用户信息
    :return: json
    """
    return jsonReturn.trueReturn(g.username, '获取用户信息')


# 用户->角色管理
@bp.route('/admin/add_role_to_user', methods=['POST'])
def add_role_to_user():
    """
    获取用户信息
    :return: json
    """
    return jsonReturn.trueReturn(g.username, '获取用户信息')


@bp.route('/admin/del_role_from_user', methods=['POST'])
def del_role_from_user():
    """
    获取用户信息
    :return: json
    """
    return jsonReturn.trueReturn(g.username, '获取用户信息')
