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
from utils.ua import ua_pc


class Shoplazza(object):
    def __init__(self):
        self.name = 'Shoplazza'
        self.log = LogHandler(self.name)
        self.header = {'User-Agent': random.choice(ua_pc)}
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

    @property
    def get_products_1(self):
        products = []
        try:
            domain = self.ps.parse_domain
            attribute = self.ps.parse_collection_attribute
            products = self.ps.parse_products_first_page
            products_url = domain + '/api/collections/{}/products'.format(attribute['collection_id'])
            params = {
                'page': 1,
                'sort_by': 'manual',
                'limit': attribute['limit'],
                'tags': '',
                'price': '',
            }
            for page in range(1, attribute['pages']):
                try:
                    params['page'] = page
                    data = HttpHelper().get(url=products_url, params=params, header=self.header).json
                    urls = self.ps.parse_products(data=data)
                    products.extend(urls)
                except:
                    pass
        except Exception as e:
            self.log.error(str(e))
        finally:
            return products

    @property
    def get_products_2(self):
        products = []
        try:
            limit = self.ps.parse_limit
            params = {
                'page': 1,
                'limit': limit,
                'sort_by': 'manual',
                'tags': ''
            }
            for page in range(1, 100):
                params['page'] = page
                text = HttpHelper().get(url=self.url, params=params, header=self.header).content
                urls = self.ps.parse_products_2(text=text)
                products.extend(urls)
                if len(urls) < limit:
                    break
        except Exception as e:
            self.log.error(str(e))
        finally:
            return products

    # 获取列表url
    @property
    def get_products(self):
        products = []
        try:
            products = self.get_products_1
            if len(products) == 0:
                products = self.get_products_2
        except Exception as e:
            self.log.error(str(e))
        finally:
            return products

    def main(self, url: str, source: int = 1, goods: int = 0, comment: int = 0, products: int = 0):
        data = {}
        self.url = url
        try:
            # 只爬去商品信息
            if goods == 1 and comment == 0:
                self.text = HttpHelper().get(url=url, header=self.header).content
                self.ps = ParseShoplazza(text=self.text, url=self.url)
                data = self.get_goods_info(source=source)

            # 只爬去评论数据
            elif goods == 0 and comment == 1:
                self.log.info("目前暂时不支持评论爬取，望大人慎重，莫频繁请求，若真的有需求，请联系爬虫工程师！")

            # 爬取商品数据和评论数据
            elif goods == 1 and comment == 1:
                self.text = HttpHelper().get(url=url, header=self.header).content
                self.ps = ParseShoplazza(text=self.text, url=self.url)
                data = self.get_goods_info(source=source)
                self.log.info("目前暂时不支持评论爬取，望大人慎重，莫频繁请求，若真的有需求，请联系爬虫工程师！")

            # 获取商品列表url
            if products == 1:
                self.text = HttpHelper().get(url=url, header=self.header).content
                self.ps = ParseShoplazza(text=self.text, url=self.url)
                data = self.get_products
        except Exception as e:
            self.log.error(str(e))
        finally:
            if isinstance(data, dict):
                data['source'] = self.name.lower()
            return data


if __name__ == '__main__':
    start_time = time.time()

    # 单品爬取测试：
    url = 'https://www.mobimiu.com/products/fashion-round-neck-long-sleeve-printed-t-shirt'
    source = 1
    goods = 1
    result = Shoplazza().main(url=url, source=source, goods=goods)
    print(json.dumps(result, indent=2, ensure_ascii=False))

    # 列表爬取测试：
    # url = 'https://www.swimsuitfor.com/collections/%F0%9F%8E%83halloween'  # 类型一:点击翻页
    # url = 'https://www.dgloya.com/collections/dog-wind-spinners'  # 类型二：Ajax翻页
    # products = 1
    # result = Shoplazza().main(url=url, products=products)
    # print(result, '\n', "商品共计：{}个".format(len(result)))

    print("耗时：", time.time() - start_time)
