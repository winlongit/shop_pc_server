# coding: utf-8
import os


class Config(object):
    RESULT_ERROR = 0
    RESULT_SUCCESS = 1

    MONGODB_SETTINGS = {'ALIAS': 'default',
                        'DB': 'lemong_shop',
                        'host': 'localhost',
                        'username': 'admin',
                        'password': ''}

    """Base config class."""
    # Flask app config
    DEBUG = True
    TESTING = True
    # token 的过期时间，7200 秒
    EXP_SECONDS = 7200

    # TODO 这里下面的所有配置都要全部大写，不然识别不到，不知道为什么，有待查找一下原因
    # 公众号-服务号
    WX_APPID = "wxc6221cda3f95b53f"
    WX_SECRET = "f0e955c30360c2d8aafda507dbb2b908"
    # 商户号信息
    MCH_ID = "1533695991"
    MCH_KEY = "c9a5241f1d9b1a21659f75cb0e3d82ba"
    # 这里不能用 https 地址，吃了大亏
    HTTP_ROOT = "http://swu.mynatapp.cc"

    SECRET_KEY = "\xb5\xb3}#\xb7A\xcac\x9d0\xb6\x0f\x80z\x97\x00\x1e\xc0\xb8+\xe9)\xf0}"

    # Root path of project
    PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    # 允许上传的图片类型
    ALLOWED_IMAGE = {'png', 'jpg', 'jpeg', 'gif'}
    # 允许免登录的 url，不需要登录也可以访问
    ALLOWED_URL = ['/api/v1/marshmallowTest/test',
                   '/api/v1/user/login',
                   '/api/v1/user/register',
                   '/api/v1/user/admin',
                   '/api/v1/product/add_category',
                   '/api/v1/product/get_types',
                   '/api/v1/product/get_goods',
                   '/api/v1/product/add_good',
                   '/api/v1/img/test',
                   '/api/v1/img/img_upload_ui',
                   '/api/v1/product/get_good_detail',
                   '/api/v1/cart/add',
                   '/api/v1/cart/cartList',
                   '/api/v1/cart/edit',
                   '/api/v1/address/addressList',
                   '/api/v1/address/addAddress',
                   '/api/v1/address/editAddress',
                   '/api/v1/address/delAddress',
                   '/api/v1/order/new_order',
                   '/api/v1/order/query_order',
                   '/api/v1/order/get_orders'
                   ]