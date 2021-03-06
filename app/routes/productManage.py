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
import json
import time

# from flask_wtf import csrf
from decimal import Decimal

from bson import ObjectId, json_util

__author__ = 'Max_Pengjb'

from flask import request, g, Blueprint
from app.models.User import User, Permission
from app import jsonReturn
from app.utils.jwt import JWT
from app.models.Product import ProductCategory, Product

# from flask_mongoengine.wtf import model_form

# PostForm = model_form(User)
bp = Blueprint('product', __name__, url_prefix="/api/v1/product")


@bp.route('/get_types', methods=['GET'])
def get_types():
    """
    获取产品的分类来构建前端页面的 NavList
    params: {
            father_id: 不是必须的，如果这个字段是空的，那么说明就是要查找最高级的分类，
          }
    :return: json
    """
    req_json = request.json
    print(req_json)
    if req_json:
        father_category = req_json.get('father_category')
    else:
        father_category = None
    try:
        res = ProductCategory.objects(father_category=father_category)
        return jsonReturn.trueReturn(res, 'ok')
    except Exception as e:
        return jsonReturn.falseReturn(request.path, str(e)) @ bp.route('/get_types', methods=['GET'])


@bp.route('/get_type_tree', methods=['GET'])
def get_types_tree():
    """
    获取产品的所有分类树，不需要参数
    :return: json [
              {value: '健康检测',label: '健康检测', children: [{value: '基因检测',label: '基因检测'},{value: 'xx',label: 'xxx'}]},
              {value: '健康检测',label: '健康检测', children: [{value: '基因检测',label: '基因检测'}]}
          ]
    """
    try:
        res = ProductCategory.get_type_tree(father_category=None)
        return jsonReturn.trueReturn(res, 'ok')
    except Exception as e:
        return jsonReturn.falseReturn(request.path, str(e))


@bp.route('/add_category', methods=['GET', 'POST'])
def add_type():
    """
    获取产品的分类来构建前端页面的 NavList
    params: {
            type: type,
            father_id: not required 父节点的id 如果有这个的话， level  一定要非空
          }
    :return: json
    """
    req_json = request.json
    category = req_json.get('category') or req_json.get('name')
    father_category = req_json.get('father_category')
    description = req_json.get('description')
    if not category:
        return jsonReturn.falseReturn(request.path, 'type 参数是必须的')
    pc = ProductCategory(category=category, father_category=father_category, description=description)
    try:
        res = pc.save()
        return jsonReturn.trueReturn(res, 'ok')
    except Exception as e:
        return jsonReturn.falseReturn(request.path, str(e))


@bp.route('/get_goods', methods=['GET', 'POST'])
def get_goods():
    """
    params: {
        page:  当前第几页，默认 1
        page_size: 一页多少条 ，默认20
        sort: 排序，默认 None
        price_min: 价格区间 最低 默认 None
        price_max: 价格区间，最高 默认 None
        category: 商品类别，默认 None
    }
    :return: total,data:[]
    """
    req_args = request.args
    page = 1
    page_size = 20
    # 请求如果不带参数，那就是默认的，这样最好，什么条件都不用加
    query_set = Product.objects()
    if req_args:
        page = req_args.get('page', 1)
        page_size = req_args.get('page_size', 20)
        sort = req_args.get('sort')
        price_min = req_args.get('price_min')
        price_max = req_args.get('price_max')
        category_lv1 = req_args.get('type')
        category_lv2 = req_args.get('category')
        keyword = req_args.get('keyword')
        # from mongoengine.queryset.visitor import Q
        # 类别空的话，就不需要在类别里面搜索
        if category_lv1:
            query_set = query_set.filter(categories=category_lv1)
        if category_lv2:
            query_set = query_set.filter(categories=category_lv2)
        if price_max:
            query_set = query_set.filter(cur_price__lte=int(price_max))
        if price_min:
            query_set = query_set.filter(cur_price__gte=int(price_min))
        if keyword:
            query_set = query_set.filter(name__contains=keyword)
        if sort:
            if sort == "升序":
                query_set = query_set.order_by('+cur_price')
            else:
                query_set = query_set.order_by('-cur_price')
        else:
            # 时间逆序，最近的时间越大
            query_set = query_set.order_by('-create_time')
    query_set = query_set.paginate(page=int(page), per_page=int(page_size))
    # res 是 'Pagination' object is not iterable
    # 序列化问题 https://www.liaoxuefeng.com/wiki/897692888725344/923056033756832
    # print(query_set.__dict__)
    res = {
        'page': query_set.page,
        'page_size': query_set.per_page,
        'total': query_set.total,
        'data': query_set.items
    }
    return jsonReturn.trueReturn(res, 'ok')


@bp.route('/get_good_detail', methods=['GET'])
def get_good_detail():
    req_args = request.args
    if not req_args:
        return jsonReturn.falseReturn(request.path, '请上传必要的参数productId')
    product_id = req_args.get('productId')
    try:
        pc = Product.objects(id=ObjectId(product_id)).first()
        return jsonReturn.trueReturn(pc, '成功')
    except Exception as e:
        return jsonReturn.falseReturn(request.path, str(e))


@bp.route('/add_good', methods=['POST'])
def add_good():
    """
    {'name': '士大夫撒旦',
    'title': '撒的发斯蒂芬',
    'origin_price': '1.1',
    'cur_price': '1.1',
    'type': '健康服务',
    'category': '户外运动',
    'specification': [{'value': '', 'canDelete': False}, {'value': '', 'canDelete': True}],
    'swiperImages': [{'order': 1, 'sm_url': 'https://i.loli.net/2019/12/08/MlICziL9AsJ5bku.jpg', 'name': 'timg.jpg'}],
    'descImages': [{'order': 1, 'sm_url': 'https://i.loli.net/2019/12/08/MlICziL9AsJ5bku.jpg', 'name': 'timg.jpg'}]}
    """
    print(request.json)
    req_json = request.json
    if not req_json:
        return jsonReturn.falseReturn(request.path, '请上传必要参数')
    name = req_json.get('name')
    title = req_json.get('title')
    description = req_json.get('description')
    origin_price = int(Decimal(req_json.get('origin_price')) * 100)
    cur_price = int(Decimal(req_json.get('cur_price')) * 100)
    # 这个分类是多个的，比如
    # categories = [req_json.get('type'), req_json.get('category')]
    categories = req_json.get('categories')
    swiperImages = req_json.get('swiperImages')
    descImages = req_json.get('descImages')
    if not all([name, title, origin_price, cur_price, categories, swiperImages, descImages]):
        return jsonReturn.falseReturn(request.path, '请上传必须的参数')
    swiper_pics = [swiper_image['sm_url'] for swiper_image in sorted(swiperImages, key=lambda x: x['order'])]
    desc_pics = [desc_image['sm_url'] for desc_image in sorted(descImages, key=lambda x: x['order'])]
    try:
        rs = Product(name=name, title=title, origin_price=origin_price, cur_price=cur_price, categories=categories,
                     swiper_pics=swiper_pics, desc_pics=desc_pics, description=description).save()
        return jsonReturn.trueReturn(rs, 'ok')
    except Exception as e:
        return jsonReturn.trueReturn('', '上传失败 ' + str(e))


@bp.route('/edit_good', methods=['POST'])
def edit_good():
    """
    {'name': '士大夫撒旦',
    'title': '撒的发斯蒂芬',
    'origin_price': '1.1',
    'cur_price': '1.1',
    'type': '健康服务',
    'category': '户外运动',
    'specification': [{'value': '', 'canDelete': False}, {'value': '', 'canDelete': True}],
    'swiperImages': [{'order': 1, 'sm_url': 'https://i.loli.net/2019/12/08/MlICziL9AsJ5bku.jpg', 'name': 'timg.jpg'}],
    'descImages': [{'order': 1, 'sm_url': 'https://i.loli.net/2019/12/08/MlICziL9AsJ5bku.jpg', 'name': 'timg.jpg'}]}
    """
    print(request.json)
    req_json = request.json
    if not req_json:
        return jsonReturn.falseReturn(request.path, '请上传必要参数')
    pro_id = req_json.get('id')
    name = req_json.get('name')
    title = req_json.get('title')
    # TODO
    origin_price = int(req_json.get('origin_price'))
    cur_price = int(req_json.get('cur_price'))
    # 这个分类是多个的，比如
    categories = [req_json.get('type'), req_json.get('category')]
    swiper_pics = req_json.get('swiperImages')
    desc_pics = req_json.get('descImages')
    if not all([pro_id, name, origin_price, cur_price, categories, swiper_pics, desc_pics]):
        return jsonReturn.falseReturn(request.path, '请上传必要参数')
    try:
        rs = Product.objects(id=ObjectId(pro_id)).update_one(name=name, title=title, origin_price=origin_price,
                                                             cur_price=cur_price, categories=categories,
                                                             swiper_pics=swiper_pics, desc_pics=desc_pics)
        return jsonReturn.trueReturn(rs, 'ok')
    except Exception as e:
        return jsonReturn.trueReturn('', '上传失败 ' + str(e))


@bp.route('/real_delete', methods=['POST'])
def real_delete():
    req_json = request.json
    if not req_json:
        return jsonReturn.falseReturn(request.path, '请上传必要参数')
    product_id = req_json.get('productId')
    if not product_id:
        return jsonReturn.falseReturn(request.path, '请上传必要的参数productId')
    try:
        Product.objects(id=ObjectId(product_id)).delete()
        return jsonReturn.trueReturn('', '删除成功')
    except Exception as e:
        return jsonReturn.falseReturn('', str(e))


@bp.route('/update_price', methods=['POST'])
def update_price():
    req_json = request.json
    if not req_json:
        return jsonReturn.falseReturn(request.path, '请上传必要参数')
    product_id = req_json.get('productId')
    cur_price = req_json.get('cur_price')
    origin_price = req_json.get('origin_price')
    if not all([product_id, cur_price is not None, origin_price is not None]):
        return jsonReturn.falseReturn(request.path, '请上传必要的参数productId,cur_price,origin_price')
    try:
        Product.objects(id=ObjectId(product_id)).update_one(cur_price=int(cur_price), origin_price=int(origin_price))
        return jsonReturn.trueReturn('', '修改成功')
    except Exception as e:
        return jsonReturn.falseReturn('', str(e))
