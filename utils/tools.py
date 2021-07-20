#!/usr/bin/evn python
# -*- coding: utf-8 -*-
# @Time     : 2021/7/17 16:58
# @Author   : dapwn
# @File     : tools.py
# @Software : PyCharm
import random
import string


def create_8_digit() -> str:
    return str(random.randint(0, 99999999)).zfill(8)
    # return "".join(map(lambda x:random.choice(string.digits), range(8)))
    # return "".join(random.sample(["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"], 8))
