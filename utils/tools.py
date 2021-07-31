#!/usr/bin/evn python
# -*- coding: utf-8 -*-
# @Time     : 2021/7/17 16:58
# @Author   : dapwn
# @File     : tools.py
# @Software : PyCharm
import random
import string
from html import unescape  # 处理html中的转义字符


# 生成8位数字
def create_8_digit() -> str:
    return str(random.randint(0, 99999999)).zfill(8)
    # return "".join(map(lambda x:random.choice(string.digits), range(8)))
    # return "".join(random.sample(["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"], 8))


class ParseString(object):
    def __init__(self):
        pass

    def delete_useless_string(self, content: str) -> str:
        return content.replace('\r', '').replace('\n', ' ').replace('\t', '').strip(' ')


if __name__ == '__main__':
    str1 = '&#39;'
    result = unescape(str1)
    print(result)
    pass
