#!/usr/bin/evn python
# -*- coding: utf-8 -*-
# @Time     : 2021/7/16 16:28
# @Author   : dapwn
# @File     : spider_helper.py
# @Software : PyCharm
"""
-------------------------------------------------
   Description :  爬虫助手
   date：          2021/7/16
-------------------------------------------------

-------------------------------------------------
"""
__author__ = 'dapwn'

import time
import requests
import random
from lxml import etree
from requests.models import Response
from requests.packages.urllib3.exceptions import InsecureRequestWarning

from handler.log_handler import LogHandler
from helper.parse_handler import CovertData

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)  # 禁用requests请求HTTPS警告


class SpiderHandler(object):
    name = 'SpiderHandler'

    def __init__(self):
        self.log = LogHandler(self.name, file=True)
        self.response = Response()

    def get(self, url, header=None, params=None, retry_times=3, retry_interval=5, timeout=10, **kwargs):
        """
        Method: GET
        :param url: target url
        :param header: header
        :param params: params
        :param retry_times: retry time
        :param retry_interval: retry interval
        :param timeout: max request time
        :param kwargs:
        :return:
        """
        headers = self.headers
        if headers and isinstance(header, dict):
            headers.update(header)
        while True:
            try:
                if not params:
                    self.response = requests.get(url=url, headers=headers, params=params, timeout=timeout, verify=False,
                                                 **kwargs)
                else:
                    self.response = requests.get(url=url, headers=headers, timeout=timeout, verify=False, **kwargs)
                return self
            except Exception as e:
                self.log.error("get: %s error: %s" % (url, str(e)))
                retry_times -= 1
                if retry_times <= 0:
                    resp = Response()
                    resp.status_code = 200
                    return self
                self.log.info("get retry %s second after" % retry_interval)
                time.sleep(retry_interval)

    def post(self, url, header=None, data=None, retry_times=3, retry_interval=5, timeout=10, **kwargs):
        """
        Method: Post
        :param url:
        :param header:
        :param data:
        :param retry_times:
        :param retry_interval:
        :param timeout:
        :param kwargs:
        :return:
        """
        headers = self.headers
        if headers and isinstance(header, dict):
            headers.update(header)
        while True:
            try:
                if not data:
                    self.response = requests.post(url=url, headers=headers, data=data, timeout=timeout, verify=False,
                                                  **kwargs)
                else:
                    self.response = requests.post(url=url, headers=headers, timeout=timeout, verify=False, **kwargs)
                return self
            except Exception as e:
                self.log.error("post: %s error: %s" % (url, str(e)))
                retry_times -= 1
                if retry_times <= 0:
                    resp = Response()
                    resp.status_code = 200
                    return self
                self.log.info("post retry %s second after" % retry_interval)
                time.sleep(retry_interval)

    @property
    def random_ua(self):
        ua_list = [
            # 'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36',
            # 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
            'mozilla/5.0 (windows NT 10.0; WOW64) applEweBkit/537.36 (KHTML, like gecko) chrome/55.0.2883.87 safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36',
            'mozilla/5.0 (windows NT 10.0; WOW64) applEweBkit/537.36 (KHTML, like gecko) chrome/80.0.3987.106 safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.106 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3947.100 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:68.0) Gecko/20100101 Firefox/68.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:68.0) Gecko/20100101 Firefox/68.0',
            # 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.25 Safari/537.36 Core/1.70.3704.400 QQBrowser/10.4.3587.400',
            # 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.93 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
            # 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.18362',
            'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 UBrowser/6.2.4098.3 Safari/537.36',
            # 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.25 Safari/537.36 Core/1.70.3708.400 QQBrowser/10.4.3620.400',
            # 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
            'mozilla/5.0 (windows NT 10.0; WOW64) applEweBkit/537.36 (KHTML, like gecko) chrome/75.0.3770.100 safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
            # 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36'
        ]
        return random.choice(ua_list)

    @property
    def headers(self):
        """
        basic headers
        :return:
        """
        ua = self.random_ua
        return {
            'User-Agent': ua,
        }

    @property
    def tree(self):
        return etree.HTML(self.response.content)

    @property
    def text(self) -> str:
        return self.response.text

    @property
    def json(self) -> dict:
        try:
            return self.response.json()
        except Exception as e:
            self.log.error(str(e))
            return {}

    @property
    def cookie(self) -> str:
        try:
            return CovertData().cookies_to_cookie(requests.utils.dict_from_cookiejar(self.response.cookies))
        except Exception as e:
            self.log.error(str(e))
            return ''


if __name__ == '__main__':
    url = 'https://www.baidu.com'
    cookie = SpiderHandler().get(url).cookie
    print(cookie, type(cookie))
