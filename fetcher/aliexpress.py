#!/usr/bin/evn python
# -*- coding: utf-8 -*-
# @Time     : 2021/8/3 18:44
# @Author   : dapwn
# @File     : aliexpress.py
# @Software : PyCharm
import random
import json
import time

from helper.http_helper import HttpHelper
from handler.log_handler import LogHandler
from helper.parse_helper import ParseShopify
from utils.ua import ua_pc


class Aliexpress(object):
    def __init__(self):
        self.name = 'Aliexpress'
        self.log = LogHandler(self.name)
        self.ua = random.choice(ua_pc)
        self.data = ''
        self.url = ''
        self.ps = ParseShopify(data=self.data, url=self.url)
        self.set_common_cookie_url = 'https://login.aliexpress.ru/setCommonCookie.htm'
        self.region = 'US'
        self.currency = 'USD'

    # 获取cookie，再带上cookie进行商品请求，不带cookie请求aliexpress会返回假数据
    @property
    def get_cookie(self) -> str:
        cookie = ''
        try:
            params = {
                'fromApp': 'false',
                'region': self.region,
                'currency': self.currency,
                'bLocale': 'en_US',
                'site': 'glo',
                'province': '',
                'city': '',
                '_': int(round(time.time() * 1000))
            }

            cookie = HttpHelper().get(url=self.set_common_cookie_url, header={'User-Agent': self.ua}, params=params).cookie
        except Exception as e:
            self.log.error(str(e))
        finally:
            return cookie

    def main(self, url: str, source: int = 1, goods: int = 0, comment: int = 0, products: int = 0):
        data = {}
        self.url = url
        try:
            # 只爬去商品信息
            if goods == 1 and comment == 0:
                cookie = self.get_cookie
                header = {
                    'User-Agent': self.ua,
                    'Cookie': cookie
                }
                text = HttpHelper().get(url=self.url, header=header).content

                self.data = HttpHelper().get(url=url).json
                self.ps = ParseShopify(data=self.data, url=self.url)
                data = self.get_goods_info(source=source)

            # 只爬去评论数据
            elif goods == 0 and comment == 1:
                self.log.info("目前暂时不支持评论爬取，望大人慎重，莫频繁请求，若真的有需求，请联系爬虫工程师！")

            # 爬取商品数据和评论数据
            elif goods == 1 and comment == 1:
                url = url + '.json'
                self.data = HttpHelper().get(url=url).json
                self.ps = ParseShopify(data=self.data, url=self.url)
                data = self.get_goods_info(source=source)
                self.log.info("目前暂时不支持评论爬取，望大人慎重，莫频繁请求，若真的有需求，请联系爬虫工程师！")

            # 获取商品列表url
            if products == 1:
                url = url + '.oembed'
                self.data = HttpHelper().get(url=url).json
                self.ps = ParseShopify(data=self.data, url=self.url)
                data = self.ps.parse_products
        except Exception as e:
            self.log.error(str(e))
        finally:
            if isinstance(data, dict):
                data['source'] = self.name.lower()
            return data
