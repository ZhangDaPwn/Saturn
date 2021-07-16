#!/usr/bin/evn python
# -*- coding: utf-8 -*-
# @Time     : 2021/7/16 15:36
# @Author   : dapwn
# @File     : six.py
# @Software : PyCharm
"""
-------------------------------------------------
   Description :   用来兼容python2和python3双环境的工具类
   Author :        dapwn
   date：          2021/7/7
-------------------------------------------------
   Point:
   from collections import Iterable
   isinstance(object,Iterable)  # 判断是否为支持可迭代对象

   iter(object[, sentinel])  # 迭代生成器

   reload: 用于重新载入之前的模块
-------------------------------------------------
"""
__author__ = 'dapwn'

import sys

PY3 = sys.version_info[0] == 3

if PY3:
    def iteritems(d, **kwargs):
        return iter(d.items(**kwargs))
