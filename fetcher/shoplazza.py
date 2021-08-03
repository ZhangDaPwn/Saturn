#!/usr/bin/evn python
# -*- coding: utf-8 -*-
# @Time     : 2021/8/2 15:21
# @Author   : dapwn
# @File     : shoplazza.py
# @Software : PyCharm
import random
import json
import time

from helper.http_helper import HttpHelper
from handler.log_handler import LogHandler
from helper.parse_helper import ParseShoplazza


class Shoplazza(object):
    def __init__(self):
        self.name = 'Shoplazza'
        self.log = LogHandler(self.name)
        self.text = ''
        self.url = ''
        self.ps = ParseShoplazza(text=self.text, url=self.url)

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
                self.text = HttpHelper().get(url=url).content
                self.ps = ParseShoplazza(text=self.text, url=self.url)
                data = self.get_goods_info(source=source)

            # 只爬去评论数据
            elif goods == 0 and comment == 1:
                pass

            # 爬取商品数据和评论数据
            elif goods == 1 and comment == 1:
                pass

            # 获取商品列表url
            if products == 1:
                pass

        except Exception as e:
            self.log.error(str(e))
        finally:
            if isinstance(data, dict):
                data['source'] = self.name.lower()
            return data


if __name__ == '__main__':
    start_time = time.time()

    url = 'https://www.mobimiu.com/products/fashion-round-neck-long-sleeve-printed-t-shirt'
    source = 1
    goods = 1
    comment = 0
    products = 0

    result = Shoplazza().main(url=url, goods=goods)

    print(json.dumps(result, indent=2, ensure_ascii=False))

    print("耗时：", time.time() - start_time)
