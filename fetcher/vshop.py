#!/usr/bin/evn python
# -*- coding: utf-8 -*-
# @Time     : 2021/8/4 18:36
# @Author   : dapwn
# @File     : vshop.py
# @Software : PyCharm
import random
import json
import time

from helper.http_helper import HttpHelper
from handler.log_handler import LogHandler
from helper.parse_helper import ParseVShop
from utils.ua import ua_pc


class VShop(object):
    def __init__(self):
        self.name = 'VShop'
        self.log = LogHandler(self.name)
        self.header = {'User-Agent': random.choice(ua_pc)}
        self.url = ''
        self.data = {}
        self.pv = ParseVShop(url=self.url)

    # 获取商品数据
    def get_goods_info(self, source: int) -> dict:
        goods = {}
        try:
            goods['goodsSpu'] = self.pv.parse_goods_spu(data=self.data)
            goods['goodsResources'] = self.pv.parse_goods_resources(data=self.data)
            # 定制化
            if source == 1:
                goods['goodsOptions'] = self.pv.parse_options(data=self.data)
            # 多规格
            elif source == 2:
                print("VShop 平台暂时不支持多规格商品爬取")
        except Exception as e:
            self.log.error(str(e))
        finally:
            return goods

    def main(self, url: str, source: int = 1, goods: int = 0, comment: int = 0, products: int = 0):
        data = {}
        self.url = url
        try:
            # 只爬去商品信息
            if goods == 1 and comment == 0:
                self.pv = ParseVShop(url=self.url)
                domain = self.pv.parse_domain
                product_id = self.pv.parse_product_id
                self.data = HttpHelper().post(url=domain + "productinfo", data={"id": product_id}).json
                data = self.get_goods_info(source=source)
            # 只爬去评论数据
            elif goods == 0 and comment == 1:
                self.log.info("目前暂时不支持评论爬取，望大人慎重，莫频繁请求，若真的有需求，请联系爬虫工程师！")

            # 爬取商品数据和评论数据
            elif goods == 1 and comment == 1:
                self.pv = ParseVShop(url=self.url)
                domain = self.pv.parse_domain
                product_id = self.pv.parse_product_id
                self.data = HttpHelper().post(url=domain + "productinfo", data={"id": product_id}).json
                data = self.get_goods_info(source=source)
                self.log.info("目前暂时不支持评论爬取，望大人慎重，莫频繁请求，若真的有需求，请联系爬虫工程师！")

            # 获取商品列表url
            if products == 1:
                self.log.info("目前暂时不支持批量爬取，望大人慎重，莫频繁请求，若真的有需求，请联系爬虫工程师！")
        except Exception as e:
            self.log.error(str(e))
        finally:
            if isinstance(data, dict):
                data['source'] = self.name.lower()
            return data


if __name__ == '__main__':
    start_time = time.time()
    # 单品爬取测试：
    url = 'https://www.joujouy.com/product?prodId=14782'
    source = 1
    goods = 1
    result = VShop().main(url=url, source=source, goods=goods)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print("耗时：", time.time() - start_time)
