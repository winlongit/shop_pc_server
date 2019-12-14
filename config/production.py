# coding: utf-8
from .default import Config


class ProductionConfig(Config):
    # App config
    # 这里不能用 https 地址，吃了大亏
    HTTP_ROOT = "http://ailemong.com"

