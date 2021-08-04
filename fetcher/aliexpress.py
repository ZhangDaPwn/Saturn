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
from helper.parse_helper import ParseAliexpress
from utils.ua import ua_pc


class Aliexpress(object):
    def __init__(self):
        self.name = 'Aliexpress'
        self.log = LogHandler(self.name)
        self.ua = random.choice(ua_pc)
        self.text = ''
        self.pa = ParseAliexpress(text=self.text)
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

            cookie = HttpHelper().get(url=self.set_common_cookie_url, header={'User-Agent': self.ua},
                                      params=params).cookie
        except Exception as e:
            self.log.error(str(e))
        finally:
            return cookie

    # 获取商品数据
    def get_goods_info(self, source: int) -> dict:
        goods = {}
        try:
            goods['goodsSpu'] = self.pa.parse_goods_spu
            goods['goodsResources'] = self.pa.parse_goods_resources
            # 定制化
            if source == 1:
                # goods['goodsOptions'] = self.pa.parse_options
                print("Aliexpress 平台暂时不支持定制化商品爬取")
            # 多规格
            elif source == 2:
                goods['skuList'] = self.pa.parse_sku_list
        except Exception as e:
            self.log.error(str(e))
        finally:
            return goods

    def main(self, url: str, source: int = 2, goods: int = 0, comment: int = 0, products: int = 0):
        data = {}
        url = url.replace('aliexpress.ru', 'www.aliexpress.com')
        try:
            # 只爬去商品信息
            if goods == 1 and comment == 0:
                cookie = self.get_cookie
                header = {
                    'User-Agent': self.ua,
                    'Cookie': cookie
                }
                text = HttpHelper().get(url=url, header=header).content
                self.pa = ParseAliexpress(text=text)
                data = self.get_goods_info(source=source)

            # 只爬去评论数据
            elif goods == 0 and comment == 1:
                self.log.info("目前暂时不支持评论爬取，望大人慎重，莫频繁请求，若真的有需求，请联系爬虫工程师！")

            # 爬取商品数据和评论数据
            elif goods == 1 and comment == 1:
                cookie = self.get_cookie
                header = {
                    'User-Agent': self.ua,
                    'Cookie': cookie
                }
                text = HttpHelper().get(url=url, header=header).content
                self.pa = ParseAliexpress(text=text)
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
    url = 'https://www.aliexpress.com/item/1005002324448280.html?spm=a2g0o.home.15002.13.3eb62145kLGPSk&gps-id=pcJustForYou&scm=1007.13562.225783.0&scm_id=1007.13562.225783.0&scm-url=1007.13562.225783.0&pvid=fc8f50a3-7d44-48aa-9ab8-9b3ac3616e8a&_t=gps-id:pcJustForYou,scm-url:1007.13562.225783.0,pvid:fc8f50a3-7d44-48aa-9ab8-9b3ac3616e8a,tpp_buckets:668%230%23131923%231_668%230%23131923%231_668%23888%233325%237_668%23888%233325%237_668%232846%238112%231997_668%235811%2327189%2390_668%236421%2330829%23787_668%232717%237562%23470__668%233374%2315176%23303_668%232846%238112%231997_668%235811%2327189%2390_668%236421%2330829%23787_668%232717%237562%23470_668%233164%239976%23508_668%233374%2315176%23303_22079%230%23207168%230_22079%235270%2324216%23157_22079%234871%2324466%23540_22079%235115%2323469%23372&&pdp_ext_f=%7B%22scene%22:%223562%22%7D'
    url = 'https://www.aliexpress.com/item/1005002278750230.html?spm=a2g01.12617084.fdpcl001.3.7058oBWXoBWXUb&pdp_ext_f=%7B%22sku_id%22:%2212000019885913794%22,%22ship_from%22:%22ES%22%7D&gps-id=5547572&scm=1007.19201.130907.0&scm_id=1007.19201.130907.0&scm-url=1007.19201.130907.0&pvid=a74fc4fc-94a1-45e2-bfae-ba34030f26bc'
    source = 2
    goods = 1
    result = Aliexpress().main(url=url, source=source, goods=goods)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print("耗时：", time.time() - start_time)
