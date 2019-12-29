# coding: utf-8
import os

from .secret import Secret


class Config(Secret):
    RESULT_ERROR = 0
    RESULT_SUCCESS = 1

    MONGODB_SETTINGS = {'ALIAS': 'default',
                        'DB': 'lemong_shop',
                        'host': 'localhost',
                        'username': 'admin',
                        'password': ''}

    """Base config class."""
    # token 的过期时间，7200 秒
    EXP_SECONDS = 7200

    # TODO 这里下面的所有配置都要全部大写，不然识别不到，不知道为什么，有待查找一下原因

    # 这里不能用 https 地址，吃了大亏
    # HTTP_ROOT = "" 这个地址根据不同的环境 开发 和 部署  地址不同

    SECRET_KEY = "\xb5\xb3}#\xb7A\xcac\x9d0\xb6\x0f\x80z\x97\x00\x1e\xc0\xb8+\xe9)\xf0}"

    # Root path of project
    PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    # 允许上传的图片类型
    ALLOWED_IMAGE = {'png', 'jpg', 'jpeg', 'gif'}
    # 允许免登录的 url，不需要登录也可以访问
    ALLOWED_URL = ['/api/v1/marshmallowTest/test',
                   '/api/v1/marshmallowTest/os_mode_test',
                   '/api/v1/user/login',
                   '/api/v1/user/register',
                   '/api/v1/user/admin',
                   '/api/v1/product/add_category',
                   '/api/v1/product/get_types',
                   '/api/v1/product/get_type_tree',
                   '/api/v1/product/get_goods',
                   '/api/v1/product/add_good',
                   '/api/v1/product/get_good_detail',
                   '/api/v1/product/real_delete',
                   '/api/v1/product/update_price',
                   '/api/v1/img/test',
                   '/api/v1/img/img_upload_ui',
                   '/api/v1/cart/add',
                   '/api/v1/cart/cartList',
                   '/api/v1/cart/edit',
                   '/api/v1/address/addressList',
                   '/api/v1/address/addAddress',
                   '/api/v1/address/editAddress',
                   '/api/v1/address/delAddress',
                   '/api/v1/order/new_order',
                   '/api/v1/order/query_order',
                   '/api/v1/order/get_orders',
                   '/api/v1/order/del_order',
                   '/api/v1/order/notifyurl',
                   '/api/v1/home/add_frame',
                   '/api/v1/home/edit_frame',
                   '/api/v1/home/frame_panel/add',
                   '/api/v1/home/frame_panel/del',
                   '/api/v1/home/get_frame'
                   ]
