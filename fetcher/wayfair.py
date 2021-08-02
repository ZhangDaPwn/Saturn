#!/usr/bin/evn python
# -*- coding: utf-8 -*-
# @Time     : 2021/8/2 11:39
# @Author   : dapwn
# @File     : wayfair.py
# @Software : PyCharm

import random
import json
from helper.http_helper import HttpHelper
from handler.log_handler import LogHandler
from utils.ua import ua_pc, ua_android
from helper.parse_helper import ParseWayfair
from settings import COMMENT_PAGE_MAX, COMMENT_NUMBER_MAX


class Wayfair(object):
    def __init__(self):
        self.name = 'Wayfair'
        self.log = LogHandler(self.name)
        self.pw = ParseWayfair(text='')
        self.review_url = 'https://www.wayfair.com/graphql'
        self.hash = {'hash': 'a636f23a2ad15b342db756fb5e0ea093'}
        self.sku = ''
        self.url = ''
        self.ua = random.choice(ua_pc + ua_android)

    def fetch_comments(self, page: int, sort_type: str = 'Most relevant') -> dict:
        comments_info = {}
        try:
            sort_order_dict = {
                'Most relevant': 'RELEVANCE',
                'Includes customer photos': 'IMAGE',
                'Latest': 'DATE_DESCENDING',
                'Most helpful': 'HELPFUL',
                'Highest rating': 'RATING_DESCENDING',
                'Lowest rating': 'RATING_ASCENDING',
            }

            data = {"variables": {"sku": self.sku.upper(),
                                  "sort_order": sort_order_dict[sort_type],
                                  "page_number": page,
                                  "filter_rating": "",
                                  "reviews_per_page": 0,
                                  "search_query": "",
                                  "language_code": "en"}}

            header = {
                'authority': 'www.wayfair.com',
                'path': '/graphql?hash=a636f23a2ad15b342db756fb5e0ea093',
                'accept': 'application/json',
                'accept-encoding': 'gzip, deflate, br',
                'accept-language': 'zh-CN,zh;q=0.9',
                'content-type': 'application/json',
                'origin': 'https://www.wayfair.com',
                'referer': self.url,
                'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
                'sec-ch-ua-mobile': '?0',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-origin',
                'use-web-hash': 'true',
                'user-agent': self.ua,
            }

            comments_info = HttpHelper().post(url=self.review_url, header=header, params=self.hash,
                                              data=json.dumps(data)).json()
        except Exception as e:
            self.log.error(e)
        finally:
            return comments_info

    # 获取商品数据
    def get_goods_info(self, source: int) -> dict:
        goods = {}
        try:
            goods['goodsResources'] = self.pw.parse_goods_resources
            goods['goodsSpu'] = self.pw.parse_goods_spu
            # 定制化
            if source == 1:
                goods['goodsOptions'] = self.pw.parse_options
            # 多规格
            elif source == 2:
                goods['skuList'] = self.pw.parse_sku_list
        except Exception as e:
            self.log.error(str(e))
        finally:
            return goods

            # 评论信息：goodsComments

    @property
    def get_comment_info(self) -> list:
        """
        更换商品评论爬取策略，爬取一页解析一页，直到成功爬取满足条件的200个评论为止，商品总评论数小于200的，爬取全部评论信息
        """
        comments = []
        try:
            for page in range(1, COMMENT_PAGE_MAX + 1):
                print("正在获取第{page}页评论数据".format(page=page))
                try:
                    data = self.fetch_comments(page=page)
                    comment = self.pw.parse_comment(data=data)
                    if comment == []:
                        break
                    else:
                        comments.extend(comment)
                except:
                    pass
                if len(comments) >= COMMENT_NUMBER_MAX:
                    comments = comments[:COMMENT_NUMBER_MAX]
                    break
        except Exception as e:
            self.log.error(e)
        finally:
            return comments

    def main(self, url: str, source: int = 1, goods: int = 0, comment: int = 0) -> dict:
        data = {}
        self.url = url
        try:
            # 只爬去商品信息
            if goods == 1 and comment == 0:
                text = HttpHelper().get(url=url, header={'User-Agent': self.ua}).text
                self.pw = ParseWayfair(text=text)
                data = self.get_goods_info(source=source)

            # 只爬去评论数据
            elif goods == 0 and comment == 1:
                self.sku = self.pw.parse_sku(url=url)
                print("sku:", self.sku)
                data['goodsComments'] = self.get_comment_info

            # 爬取商品数据和评论数据
            elif goods == 1 and comment == 1:
                text = HttpHelper().get(url=url, header={'User-Agent': self.ua}).text
                self.pw = ParseWayfair(text=text)
                data = self.get_goods_info(source=source)

                self.sku = self.pw.parse_sku(url=url)
                data['goodsComments'] = self.get_comment_info
        except Exception as e:
            self.log.error(str(e))
        finally:
            data['source'] = self.name.lower()
            return data


if __name__ == '__main__':
    # url = 'https://www.wayfair.com/furniture/pdp/andover-mills-duquette-2-piece-configurable-living-room-set-w003241867.html'  # 单属性
    # url = 'https://www.wayfair.com/baby-kids/pdp/viv-rae-griffin-glider-and-ottoman-vvre4889.html'  # 一种图片属性
    # url = 'https://www.wayfair.com/baby-kids/pdp/abdiel-platform-standard-bed-w004763304.html'  # 两种属性，全是图片
    url = 'https://www.wayfair.com/furniture/pdp/hashtag-home-askerby-2675-wide-manual-club-recliner-w001468363.html'  # 一种图片属性,部分商品无货
    # url = 'https://www.wayfair.com/furniture/pdp/greyleigh-aadvik-tufted-upholstered-low-profile-standard-bed-w003221177.html'  # 两种属性，一种图片，一种文字
    # url = 'https://www.wayfair.com/furniture/pdp/andover-mills-drusilla-tufted-upholstered-low-profile-standard-bed-w000221542.html'  # 两种属性，一种图片，一种文字
    # url = 'https://www.wayfair.com/bed-bath/pdp/trent-austin-design-oliver-comforter-set-w005483620.html'  # 两种属性，一种图片，一种文字
    # url = 'https://www.wayfair.com/bed-bath/pdp/yamazaki-home-flow-self-draining-soap-dish-w003042106.html'  # 一种图片属性，展开
    # url = 'https://www.wayfair.com/bed-bath/pdp/millwood-pines-drew-genuine-teak-wood-soap-dish-w004604002.html'  # 无属性
    # url = 'https://www.wayfair.com/bed-bath/pdp/mercury-row-eidson-soap-lotion-dispenser-w001590477.html'  # 单图片
    # url = 'https://www.wayfair.com/appliances/pdp/unique-appliances-classic-retro-24-29-cu-ft-freestanding-gas-range-unqe1026.html'
    # url = 'https://www.wayfair.com/kitchen-tabletop/pdp/cuisinart-11-piece-aluminum-non-stick-cookware-set-cui3602.html?piid=23542782'
    url = 'https://www.wayfair.com/furniture/pdp/sand-stable-bridget-hall-tree-with-shoe-storage-w003044752.html'

    source = 1
    goods = 1
    comment = 1
    data = Wayfair().main(url=url, source=source, goods=goods, comment=comment)
    # print(data)
    print(json.dumps(data, indent=2, ensure_ascii=False))
