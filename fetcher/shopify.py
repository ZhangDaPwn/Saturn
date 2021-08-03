#!/usr/bin/evn python
# -*- coding: utf-8 -*-
# @Time     : 2021/8/3 16:34
# @Author   : dapwn
# @File     : shopify.py
# @Software : PyCharm
import random
import json
import time

from helper.http_helper import HttpHelper
from handler.log_handler import LogHandler
from helper.parse_helper import ParseShopify
from utils.ua import ua_pc


class Shopify(object):
    def __init__(self):
        self.name = 'Shopify'
        self.log = LogHandler(self.name)
        self.header = {'User-Agent': random.choice(ua_pc)}
        self.data = ''
        self.url = ''
        self.ps = ParseShopify(data=self.data, url=self.url)

    # 获取商品数据
    def get_goods_info(self, source: int) -> dict:
        goods = {}
        try:
            goods['goodsSpu'] = self.ps.parse_goods_spu
            goods['goodsResources'] = self.ps.parse_goods_resources
            # 定制化
            if source == 1:
                goods['goodsOptions'] = self.ps.parse_options
            # 多规格
            elif source == 2:
                goods['skuList'] = self.ps.parse_sku_list
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
                url = url + '.json'
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


if __name__ == '__main__':

    start_time = time.time()

    # 单品爬取测试：
    url = 'https://www.maniko-nails.com/products/ethno-love'
    source = 2
    goods = 1
    result = Shopify().main(url=url, source=source, goods=goods)
    print(json.dumps(result, indent=2, ensure_ascii=False))

    # 列表爬取测试：
    # url = 'https://freshhoods.com/collections/riza-peker'  # 类型二：Ajax翻页
    # products = 1
    # result = Shopify().main(url=url, products=products)
    # print(result, '\n', "商品共计：{}个".format(len(result)))
    #
    # print("耗时：", time.time() - start_time)




