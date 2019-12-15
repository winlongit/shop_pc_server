#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
-------------------------------------------------

    @   Author  :       pengj
    @   date    :       2019/11/25 21:09
    @   IDE     :       PyCharm
    @   GitHub  :       https://github.com/JackyPJB
    @   Contact :       pengjianbiao@hotmail.com
-------------------------------------------------
    Description :       
-------------------------------------------------
"""

__author__ = 'Max_Pengjb'
import os


def load_config():
    """Load config."""
    # 这也是为了解决 uwsgi 中的 os.environ.get('MODE') 不起作用，物理吐槽这个坑
    mode = os.environ.get('MODE')
    try:
        if mode == 'development':
            from .development import DevelopmentConfig
            return DevelopmentConfig
        else:
            from .production import ProductionConfig
            return ProductionConfig

    except ImportError:
        from .default import Config
        return Config

