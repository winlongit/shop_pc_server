# coding: utf-8
from .default import Config


class DevelopmentConfig(Config):
    # Flask app config
    DEBUG = True
    TESTING = True
    # 这里不能用 https 地址，吃了大亏
    HTTP_ROOT = "http://swu.mynatapp.cc"
