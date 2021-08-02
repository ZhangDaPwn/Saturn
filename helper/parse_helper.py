#!/usr/bin/evn python
# -*- coding: utf-8 -*-
# @Time     : 2021/7/16 17:23
# @Author   : dapwn
# @File     : parse_helper.py
# @Software : PyCharm
"""
-------------------------------------------------
   Description :   数据处理助手
   date：          2021/07/28
-------------------------------------------------
针对不同平台进行数据解析处理
-------------------------------------------------
"""
__author__ = 'dapwn'

import json
import re
import random
import time

import demjson
from html import unescape
from lxml import etree
from urllib.parse import urljoin
from urllib import request

from handler.log_handler import LogHandler
from settings import *


class ParseEtsy(object):
    def __init__(self, text: str):
        self.name = "ParseEtsy"
        self.platform = 'etsy'
        self.log = LogHandler(self.name)
        self.ps = ParseString()
        self.dh = DateHandler()
        self.regions = [
            "AU",
            "CA",
            "FR",
            "DE",
            "GR",
            "IE",
            "IT",
            "JP",
            "NZ",
            "PL",
            "PT",
            "RU",
            "ES",
            "NL",
            "GB",
            "US", ]
        self.languages = [
            "de",
            "en-GB",
            "en-US",
            "es",
            "fr",
            "it",
            "ja",
            "nl",
            "pl",
            "pt",
            "ru",
        ]
        self.currencies = [
            "USD",
            "CAD",
            "EUR",
            "GBP",
            "AUD",
            "JPY",
            "CNY",
            "CZK",
            "DKK",
            "HKD",
            "HUF",
            "INR",
            "IDR",
            "ILS",
            "MYR",
            "MXN",
            "MAD",
            "NZD",
            "NOK",
            "PHP",
            "SGD",
            "VND",
            "ZAR",
            "SEK",
            "CHF",
            "THB",
            "TWD",
            "TRY",
            "PLN",
            "BRL", ]
        self.symbols = ["$",
                        "€",
                        "£",
                        "¥",
                        "Kč",
                        "₹",
                        "₪",
                        "₱",
                        "₫",
                        "฿",
                        "NT$",
                        "₺",
                        "zł",
                        "R$"]
        self.text = text
        self.base_data = self.parse_base_data
        self.context = self.parse_context

    # 提取商品收藏数
    @property
    def parse_collections(self) -> int:
        collections = 0
        try:
            pattern = re.compile('collection-count">(.*?)</a>', re.DOTALL)
            collections = int(re.findall(pattern, self.text)[0].replace('favorites', '').strip())
        except Exception as e:
            self.log.error(str(e))
        finally:
            return collections

    # 提取商品销量
    @property
    def parse_sales(self) -> int:
        sales = 0
        try:
            pattern = re.compile(r'<span class="wt-text-caption">(.*?)</span>', re.DOTALL)
            sales = int(re.findall(pattern, self.text)[0].replace('sales', '').replace(',', '').strip())
        except Exception as e:
            self.log.error(str(e))
        finally:
            return sales

    # 提取商品基础数据
    @property
    def parse_base_data(self) -> dict:
        data = {}
        try:
            pattern = re.compile(r'<script type="application/ld\+json">(.*?)</script>', re.DOTALL)
            result = re.findall(pattern, self.text)[0]
            data = demjson.decode(result)
        except Exception as e:
            self.log.error(str(e))
        finally:
            return data

    # 提取上下文数据
    @property
    def parse_context(self) -> dict:
        data = {}
        try:
            pattern = re.compile(r'Etsy\.Context=(.*?);</script>', re.DOTALL)
            result = re.findall(pattern, self.text)[0]
            data = demjson.decode(result)
        except Exception as e:
            self.log.error(str(e))
        finally:
            return data

    # 按照商品池参数规格提取商品数据
    @property
    def parse_goods_info(self) -> dict:
        data = {}
        try:
            goods = {}
            product = self.context['data']['granify']['product']
            goods['id'] = product['id']  # 商品id：202185260
            goods['name'] = unescape(product['title'])  # 商品名
            goods['url'] = self.base_data['url']  # 商品链接
            goods['image'] = product['image']  # 主图链接
            goods['brief'] = ''  # 商品简介
            goods['description'] = self.base_data['description']  # 商品描述：商品池中的数据，\n等符号无需转换，传给前端时进行转换
            goods['category'] = product['category']  # 商品分类:Home & Living
            goods['categoryId'] = ''  # 商品分类id:68887416
            goods['subCategory'] = product['sub_category']  # 子分类: Home Decor > Wall Decor > Wall Stencils
            goods['commentNumber'] = self.base_data['aggregateRating'][
                'reviewCount'] if 'aggregateRating' in self.base_data else 0  # 评论数：2597
            goods['ratingNumber'] = self.base_data['aggregateRating'][
                'ratingCount'] if 'aggregateRating' in self.base_data else 0  # 评分数:2597
            goods['rating'] = round(float(self.base_data['aggregateRating']['ratingValue']),
                                    2) if 'aggregateRating' in self.base_data else 0  # 商品评分：4.81 保留两位小数
            goods['regularPrice'] = round(float(product['regular_price']), 2)  # 商品原价：72.47
            goods['price'] = round(float(product['price']), 2)  # 商品默认价格：16.95 保留两位小数
            goods['priceCurrency'] = self.context['data']['locale_settings']['currency']['code'] if 'locale_settings' in \
                                                                                                    self.context[
                                                                                                        'data'] else 'USD'  # 货币单位:USD
            goods['symbol'] = self.context['data']['locale_settings']['currency']['symbol'] if 'locale_settings' in \
                                                                                               self.context[
                                                                                                   'data'] else '$'
            goods['shelfTime'] = ''  # 上架时间
            goods['updateTime'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())  # 更新时间
            goods['purchaseMin'] = 1  # 最小购买数量
            goods['purchaseMax'] = product['in_stock']  # 最大购买数量
            goods['sales'] = self.parse_sales  # 销量
            goods['visit'] = 0  # 商品浏览量
            goods['collection'] = self.parse_collections  # 商品收藏数量

            shop = {}
            shop['brand'] = self.base_data['brand'] if 'brand' in self.base_data else ''
            shop['logo'] = self.base_data[
                'logo'] if 'logo' in self.base_data else ''  # 品牌logo:https://i.etsystatic.com/isla/7e53e6/20577076/isla_fullxfull.20577076_4uyibor2.jpg?version=0
            shop['name'] = self.context['data']['shop_name'] if 'shop_name' in self.context[
                'data'] else ''  # 品牌:RoyalStencils
            shop['id'] = self.context['data']['shop_id'] if 'shop_id' in self.context['data'] else ''
            shop['url'] = 'https://www.etsy.com/shop/{}'.format(shop['name'])

            data['goods'] = goods
            data['shop'] = shop
            data['id'] = goods['id']
            data['platform'] = self.platform
        except Exception as e:
            self.log.error(str(e))
        finally:
            # print(json.dumps(data, indent=2, ensure_ascii=False))
            return data

    # 提取评论请求参数
    @property
    def parse_comment_params(self) -> dict:
        params = {}
        try:
            params['listing_id'] = self.context['data']['listing_id'] if 'listing_id' in self.context['data'] else ''
            params['shop_id'] = self.context['data']['shop_id'] if 'shop_id' in self.context['data'] else ''
            params['listing_price'] = self.context['data']['listing_price'] if 'listing_price' in self.context[
                'data'] else 20
            params['x_csrf_token'] = self.context['data']['csrf_nonce'] if 'csrf_nonce' in self.context['data'] else ''
        except Exception as e:
            self.log.error(str(e))
        finally:
            return params

    # 商品基础数据：goodsSpu
    @property
    def parse_goods_spu(self) -> dict:
        data = {}
        try:
            info = self.parse_goods_info
            goods = info['goods']
            # 基础参数中提取数据部分
            data['goodsNum'] = goods['id']
            data['goodsName'] = goods['name']
            data['mainImg'] = goods['image']
            data['brief'] = goods['brief']
            data['description'] = goods['description'].replace('\n', '<br>')
            data['commentScore'] = goods['rating']
            data['defaultPrice'] = goods['price']
            data['shelfTime'] = goods['shelfTime']
            data['updateTime'] = goods['updateTime']
            data['purchaseMin'] = goods['purchaseMin']
            data['purchaseMax'] = goods['purchaseMax']
            data['sales'] = goods['sales']
            data['visitNum'] = goods['visit']
            data['collection'] = goods['collection']
        except Exception as e:
            self.log.error(str(e))
        finally:
            return data

    # 商品图片数据：goodsResources：从html中解析
    @property
    def parse_goods_resources(self) -> list:
        data = []
        try:
            html = etree.HTML(self.text)
            lis = html.xpath('//ul[contains(@class, "wt-list-unstyled") and contains(@class, "carousel-pane-list")]')[0]

            # 提取image数据
            try:
                for img in lis.xpath('./li/img'):
                    item = {
                        'type': 1,
                        'url': img.attrib.get('data-src-zoom-image')
                    }
                    data.append(item)
            except:
                self.log.error('提取商品图片数据异常...')

            # 提取video数据
            try:
                videos = []
                for video in lis.xpath('.//video/source'):
                    url = video.attrib.get('src')
                    videos.append(url)
                video_images = []
                for video_img in html.xpath(
                        '//ul[@data-carousel-pagination-list]/li[@data-carousel-thumbnail-video]//img'):
                    cover = video_img.attrib.get('data-src-delay')
                    video_images.append(cover)
                for index, url in enumerate(videos):
                    item = {
                        'type': 2,
                        'url': url,
                        'cover': video_images[index]
                    }
                    data.append(item)
            except:
                self.log.error('提取商品视频数据异常...')
        except Exception as e:
            self.log.error(e)
        finally:
            return data

    # 商品定制化参数：goodsOptions: 从context中筛选出数据
    @property
    def parse_options(self) -> list:
        data = []
        try:
            # 是否存在规格参数选项
            try:
                options = self.context['data']['buyBoxAppData']['variations']['apiResourcePublicUISelects']
                for option in options:
                    item = {}
                    values = []
                    for value in option['options']:
                        item_value = {}
                        display_value = value['display_value']  # 显示字段
                        raw_display_value = value['raw_display_value']  # 未加工字段，不含（说明)
                        item_value['value'] = raw_display_value
                        item_value['price'] = 0
                        item_value['type'] = 1  # 参数类型 1文本选项 2图片选项 3文本输入 4图片上传
                        item_value['tips'] = ''
                        values.append(item_value)
                    item['main'] = 1  # 是否为主规格, 0：子规格 1：主规格
                    item['field'] = option['label']  # 规格名称
                    item['type'] = 1  # 规格类型 1文本选项 2图片选项 3文本输入 4图片上传
                    item['values'] = values
                    data.append(item)
            except:
                pass

            try:
                # 是否存在personalization选项，是必选还是可选
                personalization = self.context['data']['personalization']
                char_count_max = personalization['validation']['char_count_max']
                if personalization['is_required']:
                    item = {}
                    item['main'] = 1  # 是否为主规格, 0：子规格 1：主规格
                    item['field'] = 'Add your personalization'  # 规格名称
                    item['type'] = 3  # 规格类型 1文本选项 2图片选项 3文本输入 4图片上传
                    item['values'] = []
                    item['maxLength'] = int(char_count_max) if int(char_count_max) <= 100 else 100
                    data.append(item)
                else:
                    item = {}
                    item['main'] = 1  # 是否为主规格, 0：子规格 1：主规格
                    item['field'] = 'Add your personalization (optional)'  # 规格名称
                    item['type'] = 3  # 规格类型 1文本选项 2图片选项 3文本输入 4图片上传
                    item['values'] = []
                    item['maxLength'] = int(char_count_max) if int(char_count_max) <= 100 else 100
                    data.append(item)
            except:
                pass
        except Exception as e:
            self.log.error(str(e))
        finally:
            return data

    # 商品多规格参数: skuList
    @property
    def parse_sku_list(self) -> list:
        data = []
        try:
            options = self.parse_options
            for option in options:
                item = {}
                name = option['field']
                values = []
                if option['type'] == 1:
                    for value in option['values']:
                        item_value = {}
                        item_value['propertyValueDisplayName'] = value['value']
                        values.append(item_value)
                    item['skuPropertyName'] = name
                    item['skuPropertyValues'] = values
                    data.append(item)
                elif option['type'] == 2:
                    for value in option['values']:
                        item_value = {}
                        item_value['propertyValueDisplayName'] = value['tips']
                        item_value['skuPropertyImagePath'] = value['value']
                        values.append(item_value)
                    item['skuPropertyName'] = name
                    item['skuPropertyValues'] = values
                    data.append(item)
                elif option['type'] == 3:
                    pass

                elif option['type'] == 4:
                    pass
                else:
                    pass
        except Exception as e:
            self.log.error(e)
        finally:
            return data

    # 判断是否存在商品评论
    @property
    def has_item_comment(self) -> bool:
        result = False
        try:
            if 'Reviews for this item' in self.text:
                result = True
        except Exception as e:
            self.log.error(str(e))
        finally:
            return result

    # 判断是否存在店铺评论
    @property
    def has_shop_comment(self) -> bool:
        result = False
        try:
            if 'Reviews for this shop' in self.text:
                result = True
        except Exception as e:
            self.log.error(str(e))
        finally:
            return result

    # 解析出评论总页数
    @property
    def parse_comment_pages(self) -> int:
        pages = 1
        try:
            html_tree = etree.HTML(self.text)
            lis = html_tree.xpath('//div[@class="wt-flex-xl-5 wt-flex-wrap"]/nav/ul/li')
            if len(lis) >= 4:
                pages = int(lis[-2].xpath('./a/@data-page')[0])
        except Exception as e:
            self.log.error(str(e))
        finally:
            print("评论总页数：", pages)
            return pages

    # 解析单页评论数据
    def parse_comment(self, data: dict) -> list:
        comments = []
        try:
            # 提取reviews
            reviews = data['output']['reviews']
            html_reviews = etree.HTML(reviews)
            # print(html_reviews, '\n', type(html_reviews))
            # 评论列表
            divs = html_reviews.xpath('//div[@class="wt-grid wt-grid--block wt-mb-xs-0"]/div')
            for index, div in enumerate(divs):
                # 单个评论数据
                item = {}

                try:
                    item['name'] = self.ps.delete_useless_string(
                        div.xpath('.//p[@class="wt-text-caption wt-text-gray"]/a/text()')[0])
                    if len(item['name']) > NICK_WORD_MAX:
                        item['name'] = ''
                except:
                    item['name'] = ''

                try:
                    item['comment'] = self.ps.delete_useless_string(
                        div.xpath('.//p[@id="review-preview-toggle-{}"]/text()'.format(index))[0])
                    if len(item['comment']) > COMMENT_WORD_MAX:
                        item['comment'] = ''
                except:
                    item['comment'] = ''

                try:
                    item['reply'] = self.ps.delete_useless_string(
                        div.xpath('.//p[@id="review-preview-toggle-{}_response"]/text()'.format(index))[0])
                    if len(item['reply']) > REPLY_WORD_MAX:
                        item['reply'] = None
                except:
                    item['reply'] = None

                try:
                    img_url = self.ps.delete_useless_string(div.xpath('./div[@class="wt-pl-xs-8"]//img/@src')[0])
                    if 'iusa_75x75' in img_url:
                        print("该图片为回复用户的头像，不可计入回复图片中")
                    else:
                        item['commentResourceList'] = [{
                            'type': 1,  # 资源类型 1图片  2视频
                            'url': img_url
                        }]
                except:
                    item['commentResourceList'] = []

                try:
                    item['star'] = self.ps.delete_useless_string(div.xpath('.//input[@name="rating"]/@value')[0])
                except:
                    item['star'] = '5'

                try:
                    item['commentTime'] = self.dh.bdY_to_YmdHMS(
                        self.ps.delete_useless_string(
                            div.xpath('.//p[@class="wt-text-caption wt-text-gray"]/text()')[1]))
                except:
                    item['commentTime'] = ''

                item['country'] = None
                item['status'] = 0  # 状态 0失效  1有效
                item['type'] = 1  # 评论类型 0 自评  1用户评论
                if item['name'] != '' and item['comment'] != '':
                    comments.append(item)
        except Exception as e:
            self.log.error(str(e))
        finally:
            return comments


class ParseAmazon(object):
    def __init__(self, text: str):
        self.name = "ParseAmazon"
        self.platform = 'amazon'
        self.domain = 'https://www.amazon.com'
        self.log = LogHandler(self.name)
        self.ps = ParseString()
        self.dh = DateHandler()
        self.text = text
        self.tree = etree.HTML(self.text)
        self.btf = self.parse_btf
        self.symbols = ["$", "€", "£", "¥", "Kč", "₹", "₪", "₱", "₫", "฿", "NT$", "₺", "zł", "R$"]

    # 亚马逊评论数据中的\ \n \t \r删除
    def delete_backslash(self, string: str) -> str:
        return string.replace('\\n', '').replace('\\r', '').replace('\\t', '').replace('\\', '')

    # 处理商品评分
    def extract_star(self, string: str) -> str:
        return string.replace('\r', '').replace('\n', '').replace('\t', '').replace('out of 5 stars', '').strip()

    # 提取asin
    @property
    def parse_asin(self) -> str:
        return self.btf['mediaAsin']

    @property
    def parse_parent_asin(self) -> str:
        return self.btf['parentAsin']

    # 提取商品基础数据
    @property
    def parse_btf(self) -> dict:
        data = {}
        try:
            pattern = re.compile(r'jQuery.parseJSON\(\'(.*?)\'\);', re.DOTALL)
            result = re.findall(pattern, self.text)[0]
            data = demjson.decode(result)
        except Exception as e:
            self.log.error(str(e))
        finally:
            # print("BTF data_json:", data)
            return data

    # 提取商品图片等资源
    @property
    def parse_images_1(self) -> list:
        data = []
        try:
            try:
                pattern = re.compile(r'\'colorImages\': \{ \'initial\': (.*?)\}\]\},', re.DOTALL)
                result = re.findall(pattern, self.text)[0]
                result = result + '}]'
                data = demjson.decode(result)
            except:
                pass
        except Exception as e:
            self.log.error(str(e))
        finally:
            # print("ATF data_json:", data)
            return data

    # 提取商品图片等资源
    @property
    def parse_images_2(self) -> list:
        data = []
        try:
            try:
                pattern = re.compile(r'\'imageGalleryData\' : \[\{(.*?)}]', re.DOTALL)
                result = re.findall(pattern, self.text)[0]
                result = '[{' + result + '}]'
                data = demjson.decode(result)
            except:
                pass
        except Exception as e:
            self.log.error(str(e))
        finally:
            return data

    @property
    def parse_category(self) -> list:
        data = []
        try:
            elements = self.tree.xpath(
                '//ul[@class="a-unordered-list a-horizontal a-size-small"]/li/span[@class="a-list-item"]/a')
            for index, element in enumerate(elements):
                item = {}
                name = element.xpath('./text()')[0]
                href = element.attrib.get('href')
                url = urljoin(self.domain, href)
                pattern = re.compile(r'node=(.*)', re.DOTALL)
                id = re.findall(pattern, href)[0]
                item['category'] = index
                item['id'] = id
                item['name'] = ParseString().delete_useless_string(str(name))
                item['url'] = url
                data.append(item)
        except Exception as e:
            self.log.error(str(e))
        finally:
            return data

    # 提取评论数
    @property
    def parse_comment_number(self) -> int:
        number = 0
        try:
            try:
                pattern = re.compile(r'<span id="acrCustomerReviewText" class="a-size-base">(.*?)ratings</span>',
                                     re.DOTALL)
                result = re.findall(pattern, self.text)[0]
                number = int(result.replace(',', '').replace(' ', ''))
            except:
                pass

            try:
                if number == 0:
                    pattern = re.compile(r'\(ShopperExp-5143\)-->(.*?)global ratings</span>', re.DOTALL)
                    result = re.findall(pattern, self.text)[0]
                    number = int(result.replace(',', '').replace(' ', ''))
            except:
                pass
        except Exception as e:
            self.log.error(str(e))
        finally:
            # print(json.dumps(data, indent=2, ensure_ascii=False))
            return number

    # 提取评分
    @property
    def parse_ranting(self) -> float:
        rating = 0
        try:
            try:
                pattern = re.compile(r'noUnderline" title="(.*?) out of 5 stars">', re.DOTALL)
                result = re.findall(pattern, self.text)[0]
                rating = float(result.replace(' ', ''))
            except:
                pass

            try:
                if rating == 0:
                    pattern = re.compile(r'<span class="a-icon-alt">(.*?) out of 5 stars</span>', re.DOTALL)
                    result = re.findall(pattern, self.text)[0]
                    rating = float(result.replace(' ', ''))
            except:
                pass

            try:
                if rating == 0:
                    pattern = re.compile(r'class="a-size-medium a-color-base">(.*?) out of 5</span>', re.DOTALL)
                    result = re.findall(pattern, self.text)[0]
                    rating = float(result.replace(' ', ''))
            except:
                pass
        except Exception as e:
            self.log.error(str(e))
        finally:
            # print(json.dumps(data, indent=2, ensure_ascii=False))
            return rating

    # 处理商品价格，删除货币符号、价格区间
    def extract_price(self, string: str) -> float:
        for currency in self.symbols:
            if currency in string:
                string = string.replace(currency, '').replace(',', '')
        if ' - ' in string:
            string = string.split(' - ')[0]
        return float(string.strip())

    # 提取商品价格
    @property
    def parse_price(self) -> float:
        price = 0
        try:
            try:
                price_str = self.tree.xpath('//span[@id="priceblock_ourprice"]/text()')[0]
                price = self.extract_price(price_str)
            except:
                pass

            try:
                if price == 0:
                    price_str = self.tree.xpath('//span[@id="priceblock_saleprice"]/text()')[0]
                    price = self.extract_price(price_str)
            except:
                pass

            try:
                if price == 0:
                    price_str = self.tree.xpath('//span[@id="priceblock_dealprice"]/text()')[0]
                    price = self.extract_price(price_str)
            except:
                pass

            try:
                if price == 0:
                    price_str = \
                        self.tree.xpath(
                            '//div[@id="tmm-grid-swatch-PAPERBACK"]//span[@class="slot-price"]/span/text()')[0]
                    price = self.extract_price(price_str)
            except:
                pass
        except Exception as e:
            self.log.error(str(e))
        finally:
            # print(json.dumps(data, indent=2, ensure_ascii=False))
            return price

    # 解析商品详情描述信息，包括一些图片、表格、视频等信息
    @property
    def parse_description(self) -> str:
        description = ''
        # 商品描述
        try:
            description_html = \
                self.tree.xpath(
                    '//div[@id="productDescription_feature_div" and @data-template-name="productDescription"]')[
                    0]
            try:
                # 删除script节点
                script_html = description_html.xpath('.//script')[0]
                description_html.remove(script_html)
            except:
                pass
            description = etree.tostring(description_html).decode('utf-8')
        except Exception as e:
            self.log.error(str(e))
        finally:
            # print('description:', description)
            return description

    # 提取一些商品规格所需数据
    @property
    def parse_atf_critical_features_data_container(self):
        initializer_json = {}
        image_json = {}
        try:
            initializer_str = self.tree.xpath('//div[@id="twisterJsInitializer_feature_div"]/script/text()')[0]
            pattern = re.compile(r'var dataToReturn = \{(.*?)};', re.DOTALL)
            initializer_data = re.findall(pattern, initializer_str)[0]
            initializer_json = demjson.decode('{' + initializer_data + '}')
            # print("initializer_json:", initializer_json)

            image_str = self.tree.xpath('//div[@id="imageBlockVariations_feature_div"]/script/text()')[0]
            pattern = re.compile(r'jQuery.parseJSON\(\'(.*?)\'\);', re.DOTALL)
            image_data = re.findall(pattern, image_str)[0]
            image_json = demjson.decode(image_data)
            # print("imageBlockVariations_json:", imageBlockVariations_json)
        except Exception as e:
            self.log.error(str(e))
        finally:
            return initializer_json, image_json

    # 按照商品池参数规格提取商品数据
    @property
    def parse_goods_info(self) -> dict:
        data = {}
        try:
            goods = {}
            goods['id'] = self.btf['mediaAsin']
            goods['name'] = self.btf['title']
            goods['url'] = self.domain + '/dp/' + goods['id']
            goods['image'] = self.parse_goods_resources[0]['url']  # 从resource中取第一张图片
            goods['brief'] = ''
            goods['description'] = self.parse_description
            categories = self.parse_category
            goods['category'] = categories[-1]['name'] if len(categories) > 0 else ''
            goods['categoryId'] = categories[-1]['id'] if len(categories) > 0 else ''
            goods['commentNumber'] = self.parse_comment_number
            goods['ratingNumber'] = goods['commentNumber']
            goods['rating'] = self.parse_ranting
            goods['regularPrice'] = round(self.parse_price, 2)
            goods['price'] = goods['regularPrice']
            goods['shelfTime'] = ''  # 上架时间
            goods['updateTime'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())  # 更新时间
            goods['purchaseMin'] = 1
            goods['purchaseMax'] = 999
            goods['sales'] = random.randint(200, 800)
            goods['visit'] = random.randint(1000, 5000)
            goods['collection'] = random.randint(800, 1000)

            data['goods'] = goods
            data['id'] = goods['id']
            data['platform'] = self.platform
        except Exception as e:
            self.log.error(str(e))
        finally:
            # print(json.dumps(data, indent=2, ensure_ascii=False))
            return data

    # 商品基础数据：goodsSpu
    @property
    def parse_goods_spu(self) -> dict:
        data = {}
        try:
            info = self.parse_goods_info
            goods = info['goods']
            # 基础参数中提取数据部分
            data['goodsNum'] = goods['id']
            data['goodsName'] = goods['name']
            data['mainImg'] = goods['image']
            data['brief'] = goods['brief']
            data['description'] = goods['description'].replace('\n', '<br>')
            data['commentScore'] = goods['rating']
            data['defaultPrice'] = goods['price']
            data['shelfTime'] = goods['shelfTime']
            data['updateTime'] = goods['updateTime']
            data['purchaseMin'] = goods['purchaseMin']
            data['purchaseMax'] = goods['purchaseMax']
            data['sales'] = goods['sales']
            data['visitNum'] = goods['visit']
            data['collection'] = goods['collection']
        except Exception as e:
            self.log.error(str(e))
        finally:
            return data

    # 商品图片数据：goodsResources：从html中解析
    @property
    def parse_goods_resources(self) -> list:
        resource = []
        try:
            if len(self.parse_images_1) > 0:
                for data in self.parse_images_1:
                    item = {}
                    if data['hiRes']:
                        item['url'] = data['hiRes']
                    else:
                        item['url'] = data['large']
                    item['type'] = 1
                    resource.append(item)
            else:
                data_atf = self.parse_images_2
                for data in data_atf:
                    item = {}
                    item['url'] = data['mainUrl']
                    item['type'] = 1
                    resource.append(item)
            # 提取视频资源
            # if 'videos' in self.btf:
            #     # print("该产品存在视频介绍")
            #     for item in self.btf['videos']:
            #         video = {}
            #         # title = item['title']
            #         video['url'] = item['url']
            #         video['cover'] = item['slateUrl']
            #         video['type'] = 2
            #         resource.append(video)
        except Exception as e:
            self.log.error(e)
        finally:
            return resource

    # 商品定制化参数：goodsOptions
    @property
    def parse_options(self) -> list:
        data = []
        try:
            initializer_json, image_json = self.parse_atf_critical_features_data_container
            dimensions = initializer_json['dimensions']  # ['fit_type', 'size_name', 'color_name']
            dimensionsDisplay = initializer_json['dimensionsDisplay']  # ['Fit Type', 'Size', 'Color']
            dimensionsDisplaySubType = initializer_json['dimensionsDisplaySubType']  # ['TEXT', 'TEXT', 'IMAGE']
            dimensionValuesData = initializer_json['dimensionValuesData']
            dimensionValuesDisplayData = initializer_json['dimensionValuesDisplayData']

            visualDimensions = image_json['visualDimensions']  # ['fit_type', 'color_name']
            colorImages = image_json['colorImages']
            images = {}
            for key, value in colorImages.items():
                images[self.delete_backslash(key)] = value
            # print("images:", images)

            for index, key in enumerate(dimensions):
                item_attribute = {}
                item_attribute['main'] = 1  # 是否为主规格, 0：子规格 1：主规格
                item_attribute['field'] = dimensionsDisplay[index]  # 定制规格名称

                if dimensionsDisplaySubType[index] == 'TEXT':
                    print("规格类型 1文本选项")
                    item_attribute['type'] = 1
                    item_attribute['values'] = [{'value': value, 'price': 0, 'type': 1, 'tips': ''} for value in
                                                dimensionValuesData[index]]
                elif dimensionsDisplaySubType[index] == 'IMAGE':
                    print("规格类型 2图片选项")
                    item_attribute['type'] = 2
                    item_values = []
                    # 循环获取data-defaultasin
                    tips = dimensionValuesData[index]
                    # print("tips:", tips)
                    # data_asins = html.xpath('//div[@id="variation_{}"]/ul/li/@data-defaultasin'.format(key))
                    lis = self.tree.xpath('//div[@id="variation_{}"]/ul/li'.format(key))
                    # print("data_asins:", data_asins)
                    for i_li, li in enumerate(lis):
                        try:
                            item_value = {}
                            item_value['price'] = 0
                            item_value['type'] = 2
                            item_value['tips'] = tips[i_li]

                            data_asin = li.xpath('./@data-defaultasin')[0]
                            # print("data_asin1:", data_asin, len(data_asin))
                            if len(data_asin) != 10:
                                data_dp_url = li.xpath('./@data-dp-url')[0]
                                pattern = re.compile(r'/dp/(.*?)/', re.DOTALL)
                                data_asin = re.findall(pattern, data_dp_url)[0]
                                # print("data_asin2:", data_asin, len(data_asin))

                            titles = dimensionValuesDisplayData[data_asin]

                            title_dict = {}
                            for i_title, value in enumerate(titles):
                                title_dict[dimensions[i_title]] = value

                            title = ' '.join([title_dict[id_type] for id_type in visualDimensions])  # 此处可能需要处理\\字符
                            # print("title:", title)

                            try:
                                img_url = images[title][0]['hiRes']
                                item_value['value'] = img_url
                            except:
                                img_url = images[title][0]['large']
                                item_value['value'] = img_url

                            item_values.append(item_value)
                        except:
                            pass

                    item_attribute['values'] = item_values
                elif dimensionsDisplaySubType[index] == '':
                    print("规格类型 单属性")
                    item_attribute['type'] = 1
                    item_attribute['values'] = [{'value': value, 'price': 0, 'type': 1, 'tips': ''} for value in
                                                dimensionValuesData[index]]

                data.append(item_attribute)
        except Exception as e:
            self.log.error(str(e))
        finally:
            return data

    # 商品多规格参数: skuList
    @property
    def parse_sku_list(self) -> list:
        data = []
        try:
            options = self.parse_options
            for option in options:
                item = {}
                name = option['field']
                values = []
                if option['type'] == 1:
                    for value in option['values']:
                        item_value = {}
                        item_value['propertyValueDisplayName'] = value['value']
                        values.append(item_value)
                    item['skuPropertyName'] = name
                    item['skuPropertyValues'] = values
                    data.append(item)
                elif option['type'] == 2:
                    for value in option['values']:
                        item_value = {}
                        item_value['propertyValueDisplayName'] = value['tips']
                        item_value['skuPropertyImagePath'] = value['value']
                        values.append(item_value)
                    item['skuPropertyName'] = name
                    item['skuPropertyValues'] = values
                    data.append(item)
                elif option['type'] == 3:
                    pass

                elif option['type'] == 4:
                    pass
                else:
                    pass
        except Exception as e:
            self.log.error(e)
        finally:
            return data

    # 解析单页评论数据
    def parse_comment(self, text: str) -> list:
        comments = []
        try:
            tree = etree.HTML(text)
            divs = tree.xpath('//div[@data-hook="review"]')
            for div in divs:
                comment = {}

                try:
                    comment['name'] = div.xpath('.//span[@class="a-profile-name"]/text()')[0]
                    # print("nick:", comment['name'])
                    if len(comment['name']) > NICK_WORD_MAX:
                        comment['name'] = ''
                except:
                    comment['name'] = ''

                try:
                    # 评论内容
                    contexts = div.xpath('.//span[@data-hook="review-body"]//span/text()')
                    comment['comment'] = '<br>'.join(contexts).strip()
                    if len(comment['comment']) > COMMENT_WORD_MAX:
                        comment['comment'] = ''
                except:
                    comment['comment'] = ''

                try:
                    # 包含地理位置和评论时间
                    review_data = div.xpath('.//span[@data-hook="review-date"]/text()')[0]
                    pattern = re.compile(r'Reviewed in (.*?) on (.*)', re.DOTALL)
                    country, comment_time = re.findall(pattern, review_data)[0]
                    # 去除the United States 和 the united kingdom 中的the，与公司系统保持统一
                    comment['country'] = country.replace('the ', '')
                    timestamp = int(time.mktime(time.strptime(comment_time, '%B %d, %Y')))
                    comment['commentTime'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))
                    # print("country:{} commentTime:{}", comment['country'], comment['commentTime'])
                except:
                    comment['country'] = ''
                    comment['commentTime'] = '2021-01-01 00:00:00'

                try:
                    resource = []
                    text = div.xpath('.//script/text()')[0]
                    pattern_pic = re.compile(r', "\[(.*?)]", data\);', re.DOTALL)
                    pics = re.findall(pattern_pic, text)[0].split(',')
                    # print("pics:", pics)
                    for pic in pics:
                        item = {}
                        item['url'] = pic
                        item['type'] = 1
                        resource.append(item)
                    comment['commentResourceList'] = resource
                    # print("commentResourceList:", resource)
                except:
                    comment['commentResourceList'] = []

                try:
                    star = div.xpath('.//i[@data-hook="review-star-rating"]/span/text()')[0]
                    comment['star'] = self.extract_star(star)
                    # print("star:", comment['star'])
                except:
                    comment['star'] = '5'

                # try:
                #     # 可能是评论的概括，暂时不需要
                #     review = div_html.xpath('//a[@data-hook="review-title"]/span/text()')[0]
                #     print("review:", review)
                # except:
                #     comment['name'] = ''

                comment['reply'] = None
                comment['status'] = 0  # 状态 0失效  1有效
                comment['type'] = 1  # 评论类型 0 自评  1用户评论
                if comment['name'] != '' and comment['comment'] != '':
                    comments.append(comment)
        except Exception as e:
            self.log.error(str(e))
        finally:
            return comments


class ParseWayfair(object):
    def __init__(self, text: str):
        self.name = 'ParseWayfair'
        self.platform = 'Wayfair'
        self.log = LogHandler(self.name)
        self.text = text
        self.entry_data = self.parse_entry_data
        self.image = ''

    def api2hash(self):
        data = [
            {"api": "getinitialWaymoreModulesQuery", "hash": "b6bd2aee3912f70b28a6ad18d4a9fca4"},
            {"api": "fragment Video on Video_Type", "hash": "59effa6f1e60e3fb4275a0ef55f43565"},
            {"api": "relatedProducts", "hash": "d4cfd225b6d3fc7efc5e8d1a331fb096"},
            {"api": "product", "hash": "261fdfa45958be68b9a40c6399c9ca4e"},
            {"api": "fragment messages on Shipping_Message", "hash": "a45397d1cae55d3f96887335dcc48b4a"},
            {"api": "reviewQuery", "hash": "a636f23a2ad15b342db756fb5e0ea093"},  # 评论接口
            {"api": "getTranslatedReviewPage", "hash": "464afbabb5ed765ed9f8cff28d20f7ab"},
            {"api": "fragment shopTheLookPhotoFragment on STLPhoto", "hash": "983b83cbeb3fae256079d9db2cedeb51"},
            {"api": "productImagesAndMetadataV2", "hash": "f637a726bf8fafed3e11579d64cedc15"},
            {"api": "fragment getDimensionalImageId_options on ProductOption",
             "hash": "cced6104f635a0cd7cd0a125972e0ae7"},
            {"api": "fragment DimensionalOptionCard_options on ProductOption",
             "hash": "bdb92f44734a4959d7e3d1efe4cd2384"},
            {"api": "fragment DimensionalOptionGroup_optionCategories on ProductOptionCategory",
             "hash": "3fd49697ab3fe4bbdac102f3ac66dd6f"},
            {"api": "fragment NonVisualOptionGroup_optionCategories on ProductOptionCategory",
             "hash": "adcea05f454f26c29093a82a1b1cb5be"},
            {"api": "fragment VisualOptionGroup_optionCategories on ProductOptionCategory",
             "hash": "c452e1ba3993ac8dcf942e8ec811eef2"},
            {"api": "standardOptions", "hash": "e7f94d4a233e6bd961f0f6890c54f52f"},
            {"api": "customOptions", "hash": "23e9ca7ba4bd1333f7555b764e0efbd2"},
            {"api": "selectedOptionThumbnails", "hash": "6d2f134ff59f5586e04340fc5e94871a"},
            {"api": "fetchTitleBlockQuery", "hash": "3eb0bb1cf4502b66cbd9f027f2a61cd0"},
            {"api": "fragment MaterialFilterUtils_material on Fabric_Type", "hash": "ec97cd4f65988a1709533978f3762e79"},
            {"api": "fragment materialMetadataFragment on Product_Material_Interface_Type",
             "hash": "83eb43793d47e9d57ead7f8545f11362"},
            {"api": "fragment sampleFragment on Sample_Product_Type", "hash": "57b6bbc53ee136e9166f88375c4e835c"},
            {"api": "samplesQuery", "hash": "5e88bfd259fe51cb9b3f73326dd2348d"},
            {"api": "fragment orderedSamplesFragment on me", "hash": "3e399634694fb2720547901386261a51"},
            {"api": "samplesAvailability", "hash": "401185e7f89f183fc94d80fff26878aa"},
            {"api": "standardKitsQuery", "hash": "052be282b00345413f1feb6d9eb1ac55"},
            {"api": "whatsIncludedSchemaQuery", "hash": "e833228dc09174c182e97e32474c6a4d"},
            {"api": "weightsAndDimensions", "hash": "85f8ba545fe309999686c353eecba095"},
        ]

    def parse_sku(self, url: str) -> str:
        sku = ''
        try:
            sku = url.split('.html')[0].split('-')[-1]
        except Exception as e:
            self.log.error(str(e))
        finally:
            return sku

    @property
    def parse_sf_ui_header(self) -> dict:
        data = {}
        try:
            pattern = re.compile(
                r'<script type="text/javascript">window\["sf-ui-header::WEBPACK_ENTRY_DATA"]=(.*?);</script>')
            WEBPACK_ENTRY_DATA = re.findall(pattern, self.text)[0]
            data = demjson.decode(WEBPACK_ENTRY_DATA)
        except Exception as e:
            self.log.error(e)
        finally:
            return data

    @property
    def parse_entry_data(self) -> dict:
        data = {}
        try:
            pattern = re.compile(r'<script type="text/javascript">window\["WEBPACK_ENTRY_DATA"]=(.*?);</script>')
            WEBPACK_ENTRY_DATA = re.findall(pattern, self.text)[0]
            data = demjson.decode(WEBPACK_ENTRY_DATA)
        except Exception as e:
            self.log.error(e)
        finally:
            return data

    # 按照商品池参数规格提取商品数据
    @property
    def parse_goods_info(self) -> dict:
        data = {}
        try:
            goods = {}
            props = self.entry_data['application']['props']
            title = props['title']
            goods['id'] = props['sku']
            goods['name'] = title['name']
            goods['url'] = props['url']
            goods['image'] = self.image
            goods['brief'] = ''
            goods['description'] = props['productOverviewInformation']['description']
            goods['category'] = props['breadcrumbs']['breadcrumbs'][-1]['title'] if 'breadcrumbs' in props else ''
            goods['categoryId'] = ''
            goods['commentNumber'] = title['customerReviews']['ratingCount']
            goods['ratingNumber'] = goods['commentNumber']
            goods['rating'] = round(float(title['customerReviews']['averageRatingValue']), 2)
            goods['regularPrice'] = props['price']['listPrice'] if 'price' in props else 0
            goods['price'] = props['price']['salePrice']
            goods['shelfTime'] = ''
            goods['updateTime'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())  # 更新时间
            goods['purchaseMin'] = props['quantity']['minimum_order_quantity']
            goods['purchaseMax'] = props['quantity']['available_quantity']
            goods['sales'] = random.randint(200, 800)
            goods['visit'] = random.randint(1000, 5000)
            goods['collection'] = random.randint(800, 1000)

            data['goods'] = goods
            data['id'] = goods['id']
            data['platform'] = self.platform
        except Exception as e:
            self.log.error(str(e))
        finally:
            # print(json.dumps(data, indent=2, ensure_ascii=False))
            return data

    # 商品基础数据：goodsSpu
    @property
    def parse_goods_spu(self) -> dict:
        data = {}
        try:
            goods = self.parse_goods_info['goods']
            # 基础参数中提取数据部分
            data['goodsNum'] = goods['id']
            data['goodsName'] = goods['name']
            data['mainImg'] = goods['image']
            data['brief'] = goods['brief']
            data['description'] = goods['description'].replace('\n', '<br>')
            data['commentScore'] = goods['rating']
            data['defaultPrice'] = goods['price']
            data['shelfTime'] = goods['shelfTime']
            data['updateTime'] = goods['updateTime']
            data['purchaseMin'] = goods['purchaseMin']
            data['purchaseMax'] = goods['purchaseMax']
            data['sales'] = goods['sales']
            data['visitNum'] = goods['visit']
            data['collection'] = goods['collection']
        except Exception as error:
            self.log.error(error)
        finally:
            return data

    # 商品图片及视频数据：goodsResources
    @property
    def parse_goods_resources(self) -> list:
        data = []
        try:
            # 提取图片资源
            # url = https://secure.img1-fg.wfcdn.com/im/66478205/resize-h755-w755%5Ecompr-r85/6647/66478205/Griffin+Glider+and+Ottoman.jpg
            cdn_url = self.entry_data['application']['props']['applicationContext']['CDN_URL']
            image_items = self.entry_data['application']['props']['mainCarousel']['items']

            for image_item in image_items:
                item = {}
                image_id = image_item['imageId']
                # width = image_item['width']  # 根据json数据图片宽高，然后拼接可能部分图片有点问题
                # height = image_item['height']
                width = 800
                height = 800
                product_name = self.entry_data['application']['props']['title']['name']
                image_id_4_digit = str(image_id)[:4]
                words = []
                for word in product_name.split(' '):
                    words.append(request.quote(word))
                image_name = '+'.join(words)
                image_url = urljoin(cdn_url,
                                    'im/{digit_8}/resize-h{height}-w{width}%5Ecompr-r85/{image_id_4_digit}/{image_id}/{image_name}.jpg'.format(
                                        digit_8=NumberHandler().create_8_digit(), height=height, width=width,
                                        image_id_4_digit=image_id_4_digit, image_id=image_id, image_name=image_name))
                # print("image_url:", image_url)

                item['url'] = image_url
                item['type'] = 1
                data.append(item)

        except Exception as e:
            self.log.error(e)
        finally:
            self.image = data[0]['url']
            return data

    # 类型一：展示数据放在props里面
    @property
    def parse_options_props(self) -> list:
        item_options = []
        try:
            standard_options = self.entry_data['application']['props']['options']['standardOptions']

            if len(standard_options) > 0:
                for standard_option in standard_options:
                    item_option = {}
                    item_values = []
                    category_id = 2

                    options = standard_option['options']  # 参数值
                    for option in options:
                        name = option['name']  # 参数名
                        thumbnail_id = option['thumbnail_id']  # 相册id
                        # 图片选项
                        if thumbnail_id != "":
                            # 组装image_name
                            # image_name = '+'.join(name.split(' '))
                            # 拼装image_url
                            image_id_4_digit = str(thumbnail_id)[:4]
                            image_url = 'https://secure.img1-fg.wfcdn.com/im/{digit_8}/resize-h800-w800%5Ecompr-r85/{image_id_4_digit}/{image_id}/default_name.jpg'.format(
                                digit_8=NumberHandler().create_8_digit(), image_id_4_digit=image_id_4_digit,
                                image_id=thumbnail_id)

                            item_value = {}
                            item_value['value'] = image_url
                            item_value['price'] = 0
                            item_value['type'] = 2
                            item_value['tips'] = name
                            item_values.append(item_value)
                        # 文本选项
                        else:
                            category_id = 1
                            item_value = {}
                            item_value['value'] = name
                            item_value['price'] = 0
                            item_value['type'] = 1
                            item_value['tips'] = ''
                            item_values.append(item_value)

                    item_option['main'] = 1  # 是否为主规格, 0：子规格 1：主规格
                    item_option['field'] = standard_option['category_name']  # 规格名称
                    item_option['type'] = category_id
                    item_option['values'] = item_values
                    item_options.append(item_option)
            else:
                print("该商品无规格选项")

        except Exception as e:
            self.log.error(e)
        finally:
            return item_options

    # 类型二：展示数据放在apollo里面
    @property
    def parse_options_apollo(self) -> list:
        item_options = []
        try:
            # 显示数据
            apollo_state = self.entry_data['application']['__APOLLO_STATE__']
            sku = self.entry_data['application']['props']['sku']  # W003221177
            product_name = "Product:{}".format(sku)  # Product:W003221177

            options = apollo_state[product_name]['options']["optionCategories({\"sort\":\"SELECTION\"})"]

            for option in options:
                item_option = {}
                item_values = []

                __typename = option['__typename']  # ProductOptionCategory
                category_id = option['id']  # 2  规格类型：图片类型
                name = option['name']  # # 规格名称:Color

                option_values = option["options({\"sort\":\"DEFAULT_MATERIAL_ONLY\"})"]

                # 1: 文本选项
                if category_id == 1:
                    for option_value in option_values:
                        __ref = option_value['__ref']  # ProductOption:11166112
                        product_option = apollo_state[__ref]
                        value_name = product_option['name']

                        item_value = {}
                        item_value['value'] = value_name
                        item_value['price'] = 0
                        item_value['type'] = 1
                        item_value['tips'] = ''
                        item_values.append(item_value)
                        # print("文本value：", item_value)

                # 2: 图片选项
                elif category_id == 2:
                    for option_value in option_values:
                        __ref = option_value['__ref']  # ProductOption:59162099
                        product_option = apollo_state[__ref]
                        value_name = product_option['name']  # Gray
                        try:
                            material = product_option['material']  # {"__ref": "Fabric_Type:190043"}
                            __ref_meterial = material['__ref']  # Fabric_Type:190043
                            fabric_type = apollo_state[__ref_meterial]
                            __ref_image = fabric_type['image']['__ref']  # Image:85553994
                            # 获取属性image_id
                            image_id = apollo_state[__ref_image]['id']  # 85553994
                        except:
                            thumbnail_image = product_option['thumbnailImage']  # {"__ref": "Image:97076697"}
                            __ref_thumbnail = thumbnail_image['__ref']
                            # 获取属性image_id
                            image_id = apollo_state[__ref_thumbnail]['id']  # 85553994

                        # 组装image_name
                        image_name = '+'.join(value_name.split(' '))
                        # 拼装image_url
                        image_id_4_digit = str(image_id)[:4]
                        image_url = 'https://secure.img1-fg.wfcdn.com/im/{digit_8}/scale-w88%5Ecompr-r85/{image_id_4_digit}/{image_id}/{image_name}.jpg'.format(
                            digit_8=NumberHandler().create_8_digit(), image_id_4_digit=image_id_4_digit,
                            image_id=image_id,
                            image_name=image_name)

                        item_value = {}
                        item_value['value'] = image_url
                        item_value['price'] = 0
                        item_value['type'] = 2
                        item_value['tips'] = value_name
                        item_values.append(item_value)

                item_option['main'] = 1  # 是否为主规格, 0：子规格 1：主规格
                item_option['field'] = name  # 规格名称
                item_option['type'] = category_id
                item_option['values'] = item_values
                item_options.append(item_option)

        except Exception as error:
            self.log.error(error)
        finally:
            return item_options

    # 商品定制化参数：goodsOptions
    @property
    def parse_options(self) -> list:
        options = []
        parse_type = 1  # 解析类型1：从props中提取数据
        try:
            # 显示数据
            apollo_state = self.entry_data['application']['__APOLLO_STATE__']
            sku = self.entry_data['application']['props']['sku']  # W003221177
            product_name = "Product:{}".format(sku)  # Product:W003221177

            try:
                if apollo_state[product_name]['sku'] == sku:
                    parse_type = 2  # 解析类型2：从apollo中提取数据
            except:
                pass

            # 解析类型1：从props中提取数据
            if parse_type == 1:
                options = self.parse_options_props
            # 解析类型2：从apollo中提取数据
            elif parse_type == 2:
                options = self.parse_options_apollo
            else:
                print("暂时未遇到该种类型数据，请联系爬虫工程师添加新的解析规则!")

        except Exception as e:
            self.log.error(e)
        finally:
            return options

    # 商品多规格参数: skuList
    @property
    def parse_sku_list(self) -> list:
        data = []
        try:
            options = self.parse_options
            for option in options:
                item = {}
                name = option['field']
                values = []
                if option['type'] == 1:
                    for value in option['values']:
                        item_value = {}
                        item_value['propertyValueDisplayName'] = value['value']
                        values.append(item_value)
                    item['skuPropertyName'] = name
                    item['skuPropertyValues'] = values
                    data.append(item)
                elif option['type'] == 2:
                    for value in option['values']:
                        item_value = {}
                        item_value['propertyValueDisplayName'] = value['tips']
                        item_value['skuPropertyImagePath'] = value['value']
                        values.append(item_value)
                    item['skuPropertyName'] = name
                    item['skuPropertyValues'] = values
                    data.append(item)
                elif option['type'] == 3:
                    pass

                elif option['type'] == 4:
                    pass
                else:
                    pass
        except Exception as e:
            self.log.error(e)
        finally:
            return data

    def parse_comment(self, data: dict) -> list:
        comments = []
        try:
            reviews = data['data']['product']['customerReviews']['reviews']

            for review in reviews:
                comment = {}
                try:
                    comment['name'] = review['reviewerName']
                    if len(comment['name']) > NICK_WORD_MAX:
                        comment['name'] = ''
                except:
                    comment['name'] = ''

                try:
                    comment['comment'] = review['productComments']
                    if len(comment['comment']) > COMMENT_WORD_MAX:
                        comment['comment'] = ''
                except:
                    comment['comment'] = ''

                try:
                    comment['country'] = review['reviewerLocation']
                    date = time.strptime(review['date'], '%m/%d/%Y')
                    timestamp = int(time.mktime(date))
                    comment['commentTime'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))
                except:
                    comment['country'] = ''
                    comment['commentTime'] = '2021-01-01 00:00:00'

                try:
                    resource = []
                    customer_photos = review['customerPhotos']
                    for customer_photo in customer_photos:
                        item = {}
                        item['url'] = customer_photo['src']
                        item['type'] = 1
                        resource.append(item)
                    comment['commentResourceList'] = resource
                except:
                    comment['commentResourceList'] = []

                try:
                    comment['star'] = str(int(int(review['ratingStars']) / 2))
                except:
                    comment['star'] = '5'

                comment['reply'] = None
                comment['status'] = 0  # 状态 0失效  1有效
                comment['type'] = 1  # 评论类型 0 自评  1用户评论
                if comment['name'] != '' and comment['comment'] != '':
                    comments.append(comment)
        except Exception as e:
            self.log.error(e)
        finally:
            # print("comments:", comments)
            return comments


class ParseString(object):
    def __init__(self):
        pass

    def delete_useless_string(self, content: str) -> str:
        return content.replace('\r', '').replace('\n', ' ').replace('\t', '').strip(' ')


class NumberHandler(object):
    def __init__(self):
        pass

    # 生成8位数字
    def create_8_digit(self) -> str:
        return str(random.randint(0, 99999999)).zfill(8)
        # return "".join(map(lambda x:random.choice(string.digits), range(8)))
        # return "".join(random.sample(["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"], 8))


class DateHandler(object):
    def __init__(self):
        pass

    def bdY_to_YmdHMS(self, date: str) -> str:
        newdate = time.strptime(date, '%b %d, %Y')
        timestamp = int(time.mktime(newdate))
        time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))
        return time_str


class FileHandler(object):
    def __init__(self):
        self.country = {'Australia': '61', 'Canada': '79', 'France': '103', 'Germany': '91', 'Greece': '112',
                        'Ireland': '123', 'Italy': '128', 'Japan': '131', 'New Zealand': '167', 'Poland': '174',
                        'Portugal': '177', 'Russia': '181', 'Spain': '99', 'The Netherlands': '164',
                        'United Kingdom': '105', 'United States': '209', 'Afghanistan': '55', 'Albania': '57',
                        'Algeria': '95', 'American Samoa': '250', 'Andorra': '228', 'Angola': '56', 'Anguilla': '251',
                        'Antigua and Barbuda': '252', 'Argentina': '59', 'Armenia': '60', 'Aruba': '253',
                        'Austria': '62', 'Azerbaijan': '63', 'Bahamas': '229', 'Bahrain': '232', 'Bangladesh': '68',
                        'Barbados': '237', 'Belarus': '71', 'Belgium': '65', 'Belize': '72', 'Benin': '66',
                        'Bermuda': '225', 'Bhutan': '76', 'Bolivia': '73', 'Bosnia and Herzegovina': '70',
                        'Botswana': '77', 'Bouvet Island': '254', 'Brazil': '74',
                        'British Indian Ocean Territory': '255', 'British Virgin Islands': '231', 'Brunei': '75',
                        'Bulgaria': '69', 'Burkina Faso': '67', 'Burundi': '64', 'Cambodia': '135', 'Cameroon': '84',
                        'Cape Verde': '222', 'Cayman Islands': '247', 'Central African Republic': '78', 'Chad': '196',
                        'Chile': '81', 'China': '82', 'Christmas Island': '257', 'Cocos (Keeling) Islands': '258',
                        'Colombia': '86', 'Comoros': '259', 'Congo, Republic of': '85', 'Cook Islands': '260',
                        'Costa Rica': '87', 'Croatia': '118', 'Curaçao': '338', 'Cyprus': '89', 'Czech Republic': '90',
                        'Denmark': '93', 'Djibouti': '92', 'Dominica': '261', 'Dominican Republic': '94',
                        'Ecuador': '96', 'Egypt': '97', 'El Salvador': '187', 'Equatorial Guinea': '111',
                        'Eritrea': '98', 'Estonia': '100', 'Ethiopia': '101', 'Falkland Islands (Malvinas)': '262',
                        'Faroe Islands': '241', 'Fiji': '234', 'Finland': '102', 'French Guiana': '115',
                        'French Polynesia': '263', 'French Southern Territories': '264', 'Gabon': '104',
                        'Gambia': '109', 'Georgia': '106', 'Ghana': '107', 'Gibraltar': '226', 'Greenland': '113',
                        'Grenada': '245', 'Guadeloupe': '265', 'Guam': '266', 'Guatemala': '114', 'Guinea': '108',
                        'Guinea-Bissau': '110', 'Guyana': '116', 'Haiti': '119',
                        'Heard Island and McDonald Islands': '267', 'Holy See (Vatican City State)': '268',
                        'Honduras': '117', 'Hong Kong': '219', 'Hungary': '120', 'Iceland': '126', 'India': '122',
                        'Indonesia': '121', 'Iraq': '125', 'Isle of Man': '269', 'Israel': '127', 'Ivory Coast': '83',
                        'Jamaica': '129', 'Jordan': '130', 'Kazakhstan': '132', 'Kenya': '133', 'Kiribati': '270',
                        'Kosovo': '271', 'Kuwait': '137', 'Kyrgyzstan': '134', 'Laos': '138', 'Latvia': '146',
                        'Lebanon': '139', 'Lesotho': '143', 'Liberia': '140', 'Libya': '141', 'Liechtenstein': '272',
                        'Lithuania': '144', 'Luxembourg': '145', 'Macao': '273', 'Macedonia': '151',
                        'Madagascar': '149', 'Malawi': '158', 'Malaysia': '159', 'Maldives': '238', 'Mali': '152',
                        'Malta': '227', 'Marshall Islands': '274', 'Martinique': '275', 'Mauritania': '157',
                        'Mauritius': '239', 'Mayotte': '276', 'Mexico': '150', 'Micronesia, Federated States of': '277',
                        'Moldova': '148', 'Monaco': '278', 'Mongolia': '154', 'Montenegro': '155', 'Montserrat': '279',
                        'Morocco': '147', 'Mozambique': '156', 'Myanmar (Burma)': '153', 'Namibia': '160',
                        'Nauru': '280', 'Nepal': '166', 'Netherlands Antilles': '243', 'New Caledonia': '233',
                        'Nicaragua': '163', 'Niger': '161', 'Nigeria': '162', 'Niue': '281', 'Norfolk Island': '282',
                        'Northern Mariana Islands': '283', 'Norway': '165', 'Oman': '168', 'Pakistan': '169',
                        'Palau': '284', 'Palestinian Territory, Occupied': '285', 'Panama': '170',
                        'Papua New Guinea': '173', 'Paraguay': '178', 'Peru': '171', 'Philippines': '172',
                        'Puerto Rico': '175', 'Qatar': '179', 'Reunion': '304', 'Romania': '180', 'Rwanda': '182',
                        'Saint Helena': '286', 'Saint Kitts and Nevis': '287', 'Saint Lucia': '244',
                        'Saint Martin (French part)': '288', 'Saint Pierre and Miquelon': '289',
                        'Saint Vincent and the Grenadines': '249', 'Samoa': '290', 'San Marino': '291',
                        'Sao Tome and Principe': '292', 'Saudi Arabia': '183', 'Senegal': '185', 'Serbia': '189',
                        'Seychelles': '293', 'Sierra Leone': '186', 'Singapore': '220',
                        'Sint Maarten (Dutch part)': '337', 'Slovakia': '191', 'Slovenia': '192',
                        'Solomon Islands': '242', 'Somalia': '188', 'South Africa': '215',
                        'South Georgia and the South Sandwich Islands': '294', 'South Korea': '136',
                        'South Sudan': '339', 'Sri Lanka': '142', 'Sudan': '184', 'Suriname': '190',
                        'Svalbard and Jan Mayen': '295', 'Swaziland': '194', 'Sweden': '193', 'Switzerland': '80',
                        'Taiwan': '204', 'Tajikistan': '199', 'Tanzania': '205', 'Thailand': '198',
                        'Timor-Leste': '296', 'Togo': '197', 'Tokelau': '297', 'Tonga': '298', 'Trinidad': '201',
                        'Tunisia': '202', 'Turkey': '203', 'Turkmenistan': '200', 'Turks and Caicos Islands': '299',
                        'Tuvalu': '300', 'Uganda': '206', 'Ukraine': '207', 'United Arab Emirates': '58',
                        'United States Minor Outlying Islands': '302', 'Uruguay': '208', 'U.S. Virgin Islands': '248',
                        'Uzbekistan': '210', 'Vanuatu': '221', 'Venezuela': '211', 'Vietnam': '212',
                        'Wallis and Futuna': '224', 'Western Sahara': '213', 'Yemen': '214',
                        'Zaire (Democratic Republic of Congo)': '216', 'Zambia': '217', 'Zimbabwe': '218'}
        self.region = {'Afghanistan': 'AF', 'Albania': 'AL', 'Algeria': 'DZ', 'American Samoa': 'AS', 'Andorra': 'AD',
                       'Angola': 'AO', 'Anguilla': 'AI', 'Antigua and Barbuda': 'AG', 'Argentina': 'AR',
                       'Armenia': 'AM', 'Aruba': 'AW', 'Australia': 'AU', 'Austria': 'AT', 'Azerbaijan': 'AZ',
                       'Bahamas': 'BS', 'Bahrain': 'BH', 'Bangladesh': 'BD', 'Barbados': 'BB', 'Belarus': 'BY',
                       'Belgium': 'BE', 'Belize': 'BZ', 'Benin': 'BJ', 'Bermuda': 'BM', 'Bhutan': 'BT', 'Bolivia': 'BO',
                       'Bosnia and Herzegovina': 'BA', 'Botswana': 'BW', 'Bouvet Island': 'BV', 'Brazil': 'BR',
                       'British Indian Ocean Territory': 'IO', 'British Virgin Islands': 'VG', 'Brunei': 'BN',
                       'Bulgaria': 'BG', 'Burkina Faso': 'BF', 'Burundi': 'BI', 'Cambodia': 'KH', 'Cameroon': 'CM',
                       'Canada': 'CA', 'Cape Verde': 'CV', 'Cayman Islands': 'KY', 'Central African Republic': 'CF',
                       'Chad': 'TD', 'Chile': 'CL', 'China': 'CN', 'Christmas Island': 'CX',
                       'Cocos (Keeling) Islands': 'CC', 'Colombia': 'CO', 'Comoros': 'KM', 'Congo, Republic of': 'CG',
                       'Cook Islands': 'CK', 'Costa Rica': 'CR', 'Croatia': 'HR', 'Curaçao': 'CW', 'Cyprus': 'CY',
                       'Czech Republic': 'CZ', 'Denmark': 'DK', 'Djibouti': 'DJ', 'Dominica': 'DM',
                       'Dominican Republic': 'DO', 'Ecuador': 'EC', 'Egypt': 'EG', 'El Salvador': 'SV',
                       'Equatorial Guinea': 'GQ', 'Eritrea': 'ER', 'Estonia': 'EE', 'Ethiopia': 'ET',
                       'Falkland Islands (Malvinas)': 'FK', 'Faroe Islands': 'FO', 'Fiji': 'FJ', 'Finland': 'FI',
                       'France': 'FR', 'French Guiana': 'GF', 'French Polynesia': 'PF',
                       'French Southern Territories': 'TF', 'Gabon': 'GA', 'Gambia': 'GM', 'Georgia': 'GE',
                       'x': 'DE', 'Ghana': 'GH', 'Gibraltar': 'GI', 'Greece': 'GR', 'Greenland': 'GL',
                       'Grenada': 'GD', 'Guadeloupe': 'GP', 'Guam': 'GU', 'Guatemala': 'GT', 'Guinea': 'GN',
                       'Guinea-Bissau': 'GW', 'Guyana': 'GY', 'Haiti': 'HT', 'Heard Island and McDonald Islands': 'HM',
                       'Holy See (Vatican City State)': 'VA', 'Honduras': 'HN', 'Hong Kong': 'HK', 'Hungary': 'HU',
                       'Iceland': 'IS', 'India': 'IN', 'Indonesia': 'ID', 'Iraq': 'IQ', 'Ireland': 'IE',
                       'Isle of Man': 'IM', 'Israel': 'IL', 'Italy': 'IT', 'Ivory Coast': 'IC', 'Jamaica': 'JM',
                       'Japan': 'JP', 'Jordan': 'JO', 'Kazakhstan': 'KZ', 'Kenya': 'KE', 'Kiribati': 'KI',
                       'Kosovo': 'KV', 'Kuwait': 'KW', 'Kyrgyzstan': 'KG', 'Laos': 'LA', 'Latvia': 'LV',
                       'Lebanon': 'LB', 'Lesotho': 'LS', 'Liberia': 'LR', 'Libya': 'LY', 'Liechtenstein': 'LI',
                       'Lithuania': 'LT', 'Luxembourg': 'LU', 'Macao': 'MO', 'Macedonia': 'MK', 'Madagascar': 'MG',
                       'Malawi': 'MW', 'Malaysia': 'MY', 'Maldives': 'MV', 'Mali': 'ML', 'Malta': 'MT',
                       'Marshall Islands': 'MH', 'Martinique': 'MQ', 'Mauritania': 'MR', 'Mauritius': 'MU',
                       'Mayotte': 'YT', 'Mexico': 'MX', 'Micronesia, Federated States of': 'FM', 'Moldova': 'MD',
                       'Monaco': 'MC', 'Mongolia': 'MN', 'Montenegro': 'ME', 'Montserrat': 'MS', 'Morocco': 'MA',
                       'Mozambique': 'MZ', 'Myanmar (Burma)': 'MM', 'Namibia': 'NA', 'Nauru': 'NR', 'Nepal': 'NP',
                       'Netherlands Antilles': 'AN', 'New Caledonia': 'NC', 'New Zealand': 'NZ', 'Nicaragua': 'NI',
                       'Niger': 'NE', 'Nigeria': 'NG', 'Niue': 'NU', 'Norfolk Island': 'NF',
                       'Northern Mariana Islands': 'MP', 'Norway': 'NO', 'Oman': 'OM', 'Pakistan': 'PK', 'Palau': 'PW',
                       'Palestinian Territory, Occupied': 'PS', 'Panama': 'PA', 'Papua New Guinea': 'PG',
                       'Paraguay': 'PY', 'Peru': 'PE', 'Philippines': 'PH', 'Poland': 'PL', 'Portugal': 'PT',
                       'Puerto Rico': 'PR', 'Qatar': 'QA', 'Reunion': 'RE', 'Romania': 'RO', 'Russia': 'RU',
                       'Rwanda': 'RW', 'Saint Helena': 'SH', 'Saint Kitts and Nevis': 'KN', 'Saint Lucia': 'LC',
                       'Saint Martin (French part)': 'MF', 'Saint Pierre and Miquelon': 'PM',
                       'Saint Vincent and the Grenadines': 'VC', 'Samoa': 'WS', 'San Marino': 'SM',
                       'Sao Tome and Principe': 'ST', 'Saudi Arabia': 'SA', 'Senegal': 'SN', 'Serbia': 'RS',
                       'Seychelles': 'SC', 'Sierra Leone': 'SL', 'Singapore': 'SG', 'Sint Maarten (Dutch part)': 'SX',
                       'Slovakia': 'SK', 'Slovenia': 'SI', 'Solomon Islands': 'SB', 'Somalia': 'SO',
                       'South Africa': 'ZA', 'South Georgia and the South Sandwich Islands': 'GS', 'South Korea': 'KR',
                       'South Sudan': 'SS', 'Spain': 'ES', 'Sri Lanka': 'LK', 'Sudan': 'SD', 'Suriname': 'SR',
                       'Svalbard and Jan Mayen': 'SJ', 'Swaziland': 'SZ', 'Sweden': 'SE', 'Switzerland': 'CH',
                       'Taiwan': 'TW', 'Tajikistan': 'TJ', 'Tanzania': 'TZ', 'Thailand': 'TH', 'The Netherlands': 'NL',
                       'Timor-Leste': 'TL', 'Togo': 'TG', 'Tokelau': 'TK', 'Tonga': 'TO', 'Trinidad': 'TT',
                       'Tunisia': 'TN', 'Turkey': 'TR', 'Turkmenistan': 'TM', 'Turks and Caicos Islands': 'TC',
                       'Tuvalu': 'TV', 'Uganda': 'UG', 'Ukraine': 'UA', 'United Arab Emirates': 'AE',
                       'United Kingdom': 'GB', 'United States': 'US', 'United States Minor Outlying Islands': 'UM',
                       'Uruguay': 'UY', 'U.S. Virgin Islands': 'VI', 'Uzbekistan': 'UZ', 'Vanuatu': 'VU',
                       'Venezuela': 'VE', 'Vietnam': 'VN', 'Wallis and Futuna': 'WF', 'Western Sahara': 'EH',
                       'Yemen': 'YE', 'Zaire (Democratic Republic of Congo)': 'CD', 'Zambia': 'ZM', 'Zimbabwe': 'ZW'}
        self.language = {'Deutsch': 'de', 'English (UK)': 'en-GB', 'English (US)': 'en-US', 'Español': 'es',
                         'Français': 'fr', 'Italiano': 'it', '日本語': 'ja', 'Nederlands': 'nl', 'Polski': 'pl',
                         'Português': 'pt', 'Русский': 'ru'}
        self.currency = {'USD': {'abbr': 'USD', 'symbol': '$', 'currency': 'United States Dollar'},
                         'CAD': {'abbr': 'CAD', 'symbol': '$', 'currency': 'Canadian Dollar'},
                         'EUR': {'abbr': 'EUR', 'symbol': '€', 'currency': 'Euro'},
                         'GBP': {'abbr': 'GBP', 'symbol': '£', 'currency': 'British Pound'},
                         'AUD': {'abbr': 'AUD', 'symbol': '$', 'currency': 'Australian Dollar'},
                         'JPY': {'abbr': 'JPY', 'symbol': '¥', 'currency': 'Japanese Yen'},
                         'CNY': {'abbr': 'CNY', 'symbol': '¥', 'currency': 'Chinese Yuan'},
                         'CZK': {'abbr': 'CZK', 'symbol': 'Kč', 'currency': 'Czech Koruna'},
                         'DKK': {'abbr': 'DKK', 'symbol': 'kr', 'currency': 'Danish Krone'},
                         'HKD': {'abbr': 'HKD', 'symbol': '$', 'currency': 'Hong Kong Dollar'},
                         'HUF': {'abbr': 'HUF', 'symbol': 'Ft', 'currency': 'Hungarian Forint'},
                         'INR': {'abbr': 'INR', 'symbol': '₹', 'currency': 'Indian Rupee'},
                         'IDR': {'abbr': 'IDR', 'symbol': 'Rp', 'currency': 'Indonesian Rupiah'},
                         'ILS': {'abbr': 'ILS', 'symbol': '₪', 'currency': 'Israeli Shekel'},
                         'MYR': {'abbr': 'MYR', 'symbol': 'RM', 'currency': 'Malaysian Ringgit'},
                         'MXN': {'abbr': 'MXN', 'symbol': '$', 'currency': 'Mexican Peso'},
                         'MAD': {'abbr': 'MAD', 'symbol': 'DH', 'currency': 'Moroccan Dirham'},
                         'NZD': {'abbr': 'NZD', 'symbol': '$', 'currency': 'New Zealand Dollar'},
                         'NOK': {'abbr': 'NOK', 'symbol': 'kr', 'currency': 'Norwegian Krone'},
                         'PHP': {'abbr': 'PHP', 'symbol': '₱', 'currency': 'Philippine Peso'},
                         'SGD': {'abbr': 'SGD', 'symbol': '$', 'currency': 'Singapore Dollar'},
                         'VND': {'abbr': 'VND', 'symbol': '₫', 'currency': 'Vietnamese Dong'},
                         'ZAR': {'abbr': 'ZAR', 'symbol': 'R', 'currency': 'South African and'},
                         'SEK': {'abbr': 'SEK', 'symbol': 'kr', 'currency': 'Swedish Krona'},
                         'CHF': {'abbr': 'CHF', 'symbol': '', 'currency': 'Swiss Franc'},
                         'THB': {'abbr': 'THB', 'symbol': '฿', 'currency': 'Thai Baht'},
                         'TWD': {'abbr': 'TWD', 'symbol': 'NT$', 'currency': 'Taiwan New Dollar'},
                         'TRY': {'abbr': 'TRY', 'symbol': '₺', 'currency': 'Turkish Lira'},
                         'PLN': {'abbr': 'PLN', 'symbol': 'zł', 'currency': 'Polish Zloty'},
                         'BRL': {'abbr': 'BRL', 'symbol': 'R$', 'currency': 'Brazilian Real'}}

    # 两个一一对应的txt，按行对应组合成字典
    def two_file_to_dict(self, file1, file2):
        with open(file1, 'r', encoding='utf-8') as f:
            items = f.readlines()
            list1 = []
            for item in items:
                list1.append(item.replace('\n', ''))
        with open(file2, 'r', encoding='utf-8') as f:
            items = f.readlines()
            list2 = []
            for item in items:
                list2.append(item.replace('\n', ''))

        data = dict(zip(list1, list2))
        print(data)

    # 对一个txt文件，按行筛选组合成字典
    def file_to_dict(self, file):
        data = {}
        with open(file, 'r', encoding='utf-8') as f:
            items = f.readlines()
            list1 = []
            for item in items:
                list1.append(item.replace('\n', ''))
            for item in list1:
                pattern_abbr = re.compile('\((.*?)\)', re.DOTALL)
                abbr = re.findall(pattern_abbr, item)[0]  # 缩写
                symbol = item.split(' ')[0]
                currency = item.replace(abbr, '').replace(symbol, '').replace('()', '').strip()
                data[abbr] = {'abbr': abbr, 'symbol': symbol, 'currency': currency}
        print(data)


class CovertData(object):
    def __init__(self):
        pass

    # dict形式cookie转化成str形式的cookie
    def cookies_to_cookie(self, cookie_dict: dict) -> str:
        return ';'.join([str(i) + '=' + str(j) for i, j in cookie_dict.items()])

    # str形式的cookie转化成dict形式cookie
    def cookie_to_cookies(self, cookie_str: str) -> dict:
        return {cookie.split('=')[0]: cookie.split('=')[-1] for cookie in cookie_str.split(';')}
