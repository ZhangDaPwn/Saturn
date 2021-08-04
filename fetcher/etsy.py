#!/usr/bin/evn python
# -*- coding: utf-8 -*-
# @Time     : 2021/7/27 18:45
# @Author   : dapwn
# @File     : etsy.py
# @Software : PyCharm
"""
-------------------------------------------------
   Description :  etsy商品/评论爬虫
   date：          2021/07/28
-------------------------------------------------
  技术方案：requests
-------------------------------------------------
"""
__author__ = 'dapwn'

import json
import random
import time
import requests
from requests import Response
from handler.log_handler import LogHandler
from helper.parse_helper import ParseEtsy, CovertData
from utils.ua import ua_pc
from settings import COMMENT_NUMBER_MAX


class Etsy(object):
    def __init__(self):
        self.name = 'Etsy'
        self.log = LogHandler(self.name)
        self.ua = random.choice(ua_pc)
        self.tab_item = 'same_listing_reviews'  # 商品tab
        self.tab_shop = 'shop_reviews'  # 店铺tab
        self.set_url = 'https://www.etsy.com/api/v3/ajax/member/locale-preferences'  # 设置货币/地区/语言的链接
        self.review_url = 'https://www.etsy.com/api/v3/ajax/bespoke/member/neu/specs/reviews'  # 评论url
        self.del_label = ['Sold out']

    def get(self, url, header=None, params=None):
        try:
            headers = {'User-Agent': self.ua}
            if header != None:
                headers.update(header)
            resp = requests.get(url=url, headers=headers, params=params, timeout=15, verify=False)
            return resp
        except Exception as e:
            self.log.error(str(e))

    def post(self, url, header=None, data=None):
        try:
            headers = {'User-Agent': self.ua}
            if header != None:
                headers.update(header)
            resp = requests.post(url=url, headers=headers, data=data, verify=False)
            return resp
        except Exception as e:
            self.log.error(str(e))

    def make_cookie(self, cookies: dict) -> str:
        cookie = {}
        cookie['uaid'] = cookies['uaid']
        cookie['user_prefs'] = cookies['user_prefs']
        cookie['fve'] = cookies['fve']
        cookie['ua'] = '531227642bc86f3b5fd7103a0c0b4fd6'
        cookie_str = CovertData().cookies_to_cookie(cookie_dict=cookie)
        return cookie_str

    def get_text(self, url: str, currency: str = 'USD', language: str = 'en-US', region: str = 'US'):
        result = ''
        try:
            data = {
                'currency': currency,
                'language': language,
                'region': region
            }
            header = {
                'Host': 'www.etsy.com',
                'x-detected-locale': '{}|{}|{}'.format(currency, language, region),
            }
            # 设置货币/地区/语言
            resp = self.post(url=self.set_url, header=header, data=data)
            cookie_dict = requests.utils.dict_from_cookiejar(resp.cookies)
            header['Cookie'] = CovertData().cookies_to_cookie(cookie_dict=cookie_dict)
            del header['x-detected-locale']
            resp = self.get(url=url, header=header)
            result = resp.content.decode('utf-8')
        except Exception as e:
            self.log.error(str(e))
        finally:
            return result

    # 获取评论数据
    def get_comment_info(self, response: Response, active_tab: str = 'same_listing_reviews'):
        comments = []
        try:
            text = response.content.decode('utf-8')
            pe = ParseEtsy(text=text)
            if pe.has_item_comment:
                pages = pe.parse_comment_pages
                cookies = requests.utils.dict_from_cookiejar(response.cookies)
                cookie = self.make_cookie(cookies=cookies)
                params = pe.parse_comment_params
                header = {
                    'cookie': cookie,
                    'x-csrf-token': params['x_csrf_token']
                }
                data = {
                    'specs[reviews][]': 'Listzilla_ApiSpecs_Reviews',
                    'specs[reviews][1][listing_id]': params['listing_id'],  # listingId
                    'specs[reviews][1][shop_id]': params['shop_id'],  # shopId
                    'specs[reviews][1][active_tab]': active_tab,
                    # 这个是区分商品评论和店铺评论的参数，same_listing_reviews：商品评论 shop_reviews：店铺评论
                    # 'specs[reviews][1][listing_price]': params['listing_price'],
                    'specs[reviews][1][page]': 1,
                    # 'specs[reviews][1][category_path][]': params['category_path'],  # category_path 中任取一个，或者三个都选也行
                    'specs[reviews][1][should_show_variations]': 'true',
                    'specs[reviews][1][selected_keyword_filter]': 'all',
                    'specs[reviews][1][is_external_landing]': 'false',
                    'specs[reviews][1][is_reviews_untabbed_cached]': 'false',
                    'specs[reviews][1][search_query]': '',
                    'specs[reviews][1][sort_option]': 'Relevancy'
                }
                for page in range(1, pages + 1):
                    data['specs[reviews][1][page]'] = page
                    resp_json = self.post(url=self.review_url, header=header, data=data).json()
                    comment = pe.parse_comment(data=resp_json)
                    comments.extend(comment)
                    if len(comments) >= COMMENT_NUMBER_MAX:
                        break
        except Exception as e:
            self.log.error(str(e))
        finally:
            return comments

    # 获取商品数据
    def get_goods_info(self, text: str, source: int) -> dict:
        goods = {}
        try:
            pe = ParseEtsy(text=text)
            goods['goodsSpu'] = pe.parse_goods_spu
            goods['goodsResources'] = pe.parse_goods_resources
            # 定制化
            if source == 1:
                goods['goodsOptions'] = pe.parse_options
            # 多规格
            elif source == 2:
                goods['skuList'] = pe.parse_sku_list
        except Exception as e:
            self.log.error(str(e))
        finally:
            return goods

    def main(self, url: str, source: int = 1, goods: int = 0, comment: int = 0) -> dict:
        data = {}
        # 只爬去商品信息
        if goods == 1 and comment == 0:
            text = self.get_text(url=url)
            data = self.get_goods_info(text=text, source=source)
        # 只爬去评论数据
        elif goods == 0 and comment == 1:
            response = self.get(url=url)
            data['goodsComments'] = self.get_comment_info(response=response)
        # 爬取商品数据和评论数据
        elif goods == 1 and comment == 1:
            text = self.get_text(url=url)
            data = self.get_goods_info(text=text, source=source)
            # 评论数据,不使用第一次请求的resp
            response = self.get(url=url)
            data['goodsComments'] = self.get_comment_info(response=response)
        data['source'] = self.name.lower()
        return data


if __name__ == '__main__':
    start_time = time.time()
    url = 'https://www.etsy.com/listing/1034491487/minky-bear-lovey-woodland-bear-rug-baby'
    url = 'https://www.etsy.com/listing/748928449/bear-necklace-black-or-brown-grizzle'
    url = 'https://www.etsy.com/hk-en/listing/776377544/double-name-ring-two-name-ring-in?ref=hp_rv-1&pro=1'
    source = 1
    goods = 1
    comment = 0
    data = Etsy().main(url=url, source=source, goods=goods, comment=comment)
    print(json.dumps(data, indent=2, ensure_ascii=False))
    print("耗时：", time.time() - start_time)
