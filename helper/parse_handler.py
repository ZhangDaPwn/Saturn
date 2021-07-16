#!/usr/bin/evn python
# -*- coding: utf-8 -*-
# @Time     : 2021/7/16 17:23
# @Author   : dapwn
# @File     : parse_handler.py
# @Software : PyCharm


class CovertData(object):
    def __init__(self):
        pass

    # dict形式cookie转化成str形式的cookie
    def cookies_to_cookie(self, cookie_dict: dict) -> str:
        return ';'.join([str(i) + '=' + str(j) for i, j in cookie_dict.items()])

    # str形式的cookie转化成dict形式cookie
    def cookie_to_cookies(self, cookie_str: str) -> dict:
        return {cookie.split('=')[0]: cookie.split('=')[-1] for cookie in cookie_str.split(';')}
