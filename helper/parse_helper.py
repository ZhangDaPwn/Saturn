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
from datetime import datetime
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
                    date = self.ps.delete_useless_string(
                        div.xpath('.//p[@class="wt-text-caption wt-text-gray"]/text()')[1])
                    timestamp = int(time.mktime(time.strptime(date, '%b %d, %Y')))
                    item['commentTime'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))
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
            data['description'] = goods['description']
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
                    comment['commentResourceList'] = resource[:COMMENT_PAGE_MAX]
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
                    comment['commentResourceList'] = resource[:COMMENT_PAGE_MAX]
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


class ParseShoplazza(object):
    def __init__(self, text, url):
        self.name = 'ParseShoplazza'
        self.platform = 'shoplazza'
        self.log = LogHandler(self.name)
        self.ps = ParseString()
        self.text = text
        self.url = url
        self.tree = etree.HTML(self.text)
        self.base_data = self.parse_data
        self.cdn = 'https://cdn.shoplazza.com'

    @property
    def parse_domain(self) -> str:
        domain = ''
        try:
            # 从商品url中提取domain
            try:
                pattern = re.compile(r'(.*?)/products/', re.DOTALL)
                domain = re.findall(pattern, self.url)[0]
            except:
                pass
            # 从商品列表url中提取domain
            if domain == '':
                try:
                    pattern = re.compile(r'(.*?)/collections', re.DOTALL)
                    domain = re.findall(pattern, self.url)[0]
                except:
                    pass
        except Exception as e:
            self.log.error(str(e))
        finally:
            return domain

    # 解析商品详情数据
    @property
    def parse_data(self) -> dict:
        data = {}
        try:
            pattern = re.compile(r'product_detail\((.*?)}\);', re.DOTALL)
            data = str(re.findall(pattern, self.text)[0]) + '}'
            data = demjson.decode(data)
        except Exception as e:
            self.log.error(str(e))
        finally:
            return data

    # 拼装img中的data-srcset值和srcset值
    def make_data_srcset(self, data_src: str, width: str) -> str:
        data_srcset = ''
        try:
            nums = [
                48, 180, 360, 540, 720, 900, 1024,
                1280, 1366, 1440, 1536, 1600, 1920,
                2056, 2560, 2732, 2880, 3072, 3200, 3840
            ]
            nums.sort(reverse=False)
            for num in nums:
                if num > int(width):
                    width = str(num)
                    break
            pic_url = data_src.replace('{width}', width)
            for size in nums:
                data_srcset += pic_url + ' ' + str(size) + 'w, '
        except:
            pass
        finally:
            return data_srcset

    def make_description_html(self, html):
        try:
            imgs = html.xpath('.//img')
            for img in imgs:
                try:
                    width = img.attrib.get('width')
                    data_src = img.attrib.get('data-src')
                    # print("data_src: ", data_src, type(data_src))
                    if '.gif' in data_src:
                        img.attrib['src'] = data_src
                    else:
                        data_srcset = self.make_data_srcset(data_src=data_src, width=width)
                        # print("data_srcset: ", data_srcset)
                        img.attrib['data-srcset'] = data_srcset
                        img.attrib['srcset'] = data_srcset
                        img.attrib.pop('data-src')
                except:
                    pass
        except Exception as e:
            self.log.error(str(e))
        finally:
            return html

    @property
    def parse_description(self) -> str:
        description = ''
        try:
            description_html = self.tree.xpath('//div[contains(@class, "product-info__desc-tab product-info__desc")]')[
                0]
            # 选择出label节点，并删除
            try:
                label_html = description_html.xpath('./div[@class="product-info__label_tabs"]')[0]
                description_html.remove(label_html)
            except:
                pass

            # 增添一个img_url加密部分，修改时间2021/6/17，如需关闭，注释这行就行
            description_html = self.make_description_html(description_html)
            description = self.ps.delete_useless_string(etree.tostring(description_html).decode('utf-8'))
            # print("description:", description)
        except Exception as e:
            self.log.error(str(e))
        finally:
            return description

    # 按照商品池参数规格提取商品数据
    @property
    def parse_goods_info(self) -> dict:
        data = {}
        try:
            goods = {}
            product = self.base_data['product']

            goods['id'] = product['id']
            goods['name'] = product['title']
            goods['url'] = urljoin(self.parse_domain, product['url'])
            goods['image'] = urljoin('https', product['image']['src'])
            goods['brief'] = ''
            goods['description'] = self.parse_description
            goods['rating'] = random.randint(3, 5)
            goods['regularPrice'] = product['price_max']
            goods['price'] = product['price']
            goods['shelfTime'] = str(datetime.strptime(product['created_at'], "%Y-%m-%dT%H:%M:%SZ"))
            goods['updateTime'] = str(datetime.strptime(product['updated_at'], "%Y-%m-%dT%H:%M:%SZ"))
            goods['purchaseMin'] = 1
            goods['purchaseMax'] = product['inventory_quantity']
            goods['sales'] = product['sales']
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
            data['description'] = goods['description']
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

    # 商品图片及视频数据：goodsResources
    @property
    def parse_goods_resources(self) -> list:
        data = []
        try:
            images = self.base_data['product']['images']
            for image in images:
                item = {
                    'type': 1,
                    'url': urljoin(self.cdn, image['src']) if 'src' in image else ''
                }
                data.append(item)
        except Exception as e:
            self.log.error(e)
        finally:
            return data

    # 商品定制化参数：goodsOptions
    @property
    def parse_options(self) -> list:
        data = []
        try:
            options = self.base_data['product']['options']
            for option in options:
                item = {}
                item['main'] = 1
                item['field'] = option['name']
                item['type'] = 1
                item['values'] = [{'value': value, 'price': 0, 'type': 1, 'tips': ''} for value in option['values']]
                data.append(item)
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

    # 提取商品列表翻页请求参数：类型一
    @property
    def parse_collection_attribute(self):
        attribute = {}
        try:
            # 提取首页collectionData
            try:
                pattern = re.compile(r'collectionDetail\((.*?)\);', re.DOTALL)
                data = demjson.decode(re.findall(pattern, self.text)[0])
                attribute['collection_id'] = data['collection_id']
                attribute['pages'] = int(data['pages'])
                attribute['limit'] = int(data['limit'])
            except:
                pass
            if attribute == {}:
                try:
                    pass
                except:
                    pass
        except Exception as e:
            self.log.error(str(e))
        finally:
            return attribute

    # 提取商品列表翻页请求参数：类型二
    @property
    def parse_limit(self):
        limit = 1
        try:
            try:
                pattern = re.compile(r'params,extraParams,\{limit:(.*?),sort_by:sort_by,', re.DOTALL)
                limit = int(re.findall(pattern, self.text)[0])
            except:
                pass
        except Exception as e:
            self.log.error(str(e))
        finally:
            return limit

    @property
    def parse_products_first_page(self) -> list:
        products = []
        try:
            domain = self.parse_domain
            # 提取首页所有商品url
            pattern = re.compile(r'data-product-url="(.*?)"', re.DOTALL)
            products_url = re.findall(pattern, self.text)
            products_url.pop()
            for product_url in products_url:
                url = urljoin(domain, product_url)
                products.append(url)
        except Exception as e:
            self.log.error(str(e))
        finally:
            return products

    # 提取商品链接：类型一
    def parse_products(self, data: dict) -> list:
        products = []
        try:
            domain = self.parse_domain
            for product in data['data']['products']:
                product_url = product['url']
                product_url = urljoin(domain, product_url)
                products.append(product_url)
        except Exception as e:
            self.log.error(str(e))
        finally:
            return products

    # 提取商品链接：类型二
    def parse_products_2(self, text: str) -> list:
        products = []
        try:
            domain = self.parse_domain
            tree = etree.HTML(text)
            products_url = tree.xpath('//div[@id="collection_products"]/div/a/@href')
            for product_url in products_url:
                product_url = urljoin(domain, product_url)
                products.append(product_url)
        except Exception as e:
            self.log.error(str(e))
        finally:
            return products


class ParseShopify(object):
    def __init__(self, data, url):
        self.name = 'ParseShopify'
        self.platform = 'shopify'
        self.log = LogHandler(self.name)
        self.ps = ParseString()
        self.data = data
        self.url = url

    # 按照商品池参数规格提取商品数据
    @property
    def parse_goods_info(self) -> dict:
        data = {}
        try:
            goods = {}
            product = self.data['product']

            goods['id'] = product['id']
            goods['name'] = product['title']
            goods['url'] = self.url
            goods['image'] = product['image']['src']
            goods['brief'] = ''
            goods['description'] = product['body_html']
            goods['rating'] = random.randint(3, 5)
            variant = product['variants'][0]
            goods['regularPrice'] = round(float(variant['price']), 2)
            goods['price'] = goods['regularPrice']
            # 需要转化时区
            goods['shelfTime'] = str(datetime.strptime(variant['created_at'], "%Y-%m-%dT%H:%M:%S-04:00"))
            goods['updateTime'] = str(datetime.strptime(variant['updated_at'], "%Y-%m-%dT%H:%M:%S-04:00"))
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
            data['description'] = goods['description']
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
            for image in self.data['product']['images']:
                item = {
                    'type': 1,
                    'url': image['src']
                }
                data.append(item)
        except Exception as e:
            self.log.error(str(e))
        finally:
            return data

    # 商品定制化参数：goodsOptions: 从context中筛选出数据
    @property
    def parse_options(self) -> list:
        data = []
        try:
            options = self.data['product']['options']
            for option in options:
                item = {}
                item['main'] = 1  # 是否为主规格, 0：子规格 1：主规格
                item['field'] = option['name']  # 规格名称
                item['type'] = 1  # 规格类型 1文本选项 2图片选项 3文本输入 4图片上传
                item['values'] = [{'value': value, 'price': 0, 'type': 1, 'tips': ''} for value in option['values']]
                data.append(item)
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

    # 获取商品列表链接
    @property
    def parse_products(self):
        products = []
        try:
            for product in self.data['products']:
                path = ''
                if 'product_id' in product:
                    path = product['product_id']
                elif 'handle' in product:
                    path = product['handle']
                product_url = self.url + '/products/' + path
                products.append(product_url)
        except Exception as e:
            self.log.error(str(e))
        finally:
            return products


class ParseAliexpress(object):
    def __init__(self, text):
        self.name = 'ParseAliexpress'
        self.platform = 'aliexpress'
        self.log = LogHandler(self.name)
        self.text = text
        self.data = self.parse_base_data

    # 提取商品基础数据
    @property
    def parse_base_data(self) -> dict:
        data = {}
        try:
            pattern = re.compile(r'window\.runParams = \{(.*?)\};', re.DOTALL)
            run_params_str = re.findall(pattern, self.text)[0]
            data = demjson.decode('{' + run_params_str + '}')
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
            data = self.data['data']
            action_module = data['actionModule']
            title_module = data['titleModule']
            page_module = data['pageModule']
            price_module = data['priceModule']
            quantity_module = data['quantityModule']

            goods['id'] = page_module['productId']
            goods['name'] = page_module['title']
            goods['url'] = page_module['itemDetailUrl']
            goods['image'] = page_module['imagePath']
            goods['brief'] = ''
            goods['description'] = page_module['description']
            rating = title_module['feedbackRating']
            goods['rating'] = round(float(rating['averageStar']), 2)
            goods['regularPrice'] = round(float(price_module['minAmount']['value']),
                                          2) if 'minAmount' in price_module else 0
            goods['price'] = round(float(price_module['maxActivityAmount']['value']),
                                   2) if 'maxActivityAmount' in price_module else 0
            goods['shelfTime'] = ''
            goods['updateTime'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())  # 更新时间
            goods['purchaseMin'] = 1
            goods['purchaseMax'] = quantity_module['totalAvailQuantity']
            goods['sales'] = title_module['tradeCount']
            goods['visit'] = random.randint(1000, 5000)
            goods['collection'] = action_module[
                'itemWishedCount'] if 'itemWishedCount' in action_module else random.randint(800, 1000)

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
            data['description'] = goods['description']
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
            data = [{'url': url, 'type': 1} for url in self.data['data']['imageModule']['imagePathList']]
        except Exception as e:
            self.log.error(e)
        finally:
            return data

    # 商品多规格参数: skuList
    @property
    def parse_sku_list(self) -> list:
        data = []
        try:
            data = self.data['data']['skuModule']['productSKUPropertyList']
        except Exception as e:
            self.log.error(e)
        finally:
            return data


class ParseVShop(object):
    def __init__(self, url):
        self.name = 'ParseVShop'
        self.platform = 'vhsop'
        self.log = LogHandler(self.name)
        self.url = url

    @property
    def parse_product_id(self):
        product_id = ''
        try:
            pattern = re.compile(r'prodId=(.*)', re.DOTALL)
            product_id = re.findall(pattern, self.url)[0]
        except Exception as e:
            self.log.error(str(e))
        finally:
            return product_id

    @property
    def parse_domain(self):
        domain = ''
        try:
            pattern = re.compile(r'(.*?)product\?', re.DOTALL)
            domain = re.findall(pattern, self.url)[0]
        except Exception as e:
            self.log.error(str(e))
        finally:
            return domain

    def getnerate_option(self, main, field, type):
        goods_option = {}
        goods_option['main'] = main
        goods_option['field'] = field
        goods_option['type'] = type
        return goods_option

    def new_options_map(self, old_sub_opts):
        new_sub_opts = []
        for old_sub_opt in old_sub_opts:
            new_sub_opt = {}
            new_sub_opt['value'] = old_sub_opt['key']
            new_sub_opt['price'] = old_sub_opt['value']
            new_sub_opts.append(new_sub_opt)
        return new_sub_opts

    def get_chain_length(self):
        chain_length = [
            {
                "value": '14'' (35cm)  - Child',
                "price": 0
            },
            {
                "value": '16'' (40cm)  - Young Adult',
                "price": 0
            },
            {
                "value": '18'' (45cm)  - Adult',
                "price": 0
            },
            {
                "value": '20'' (50cm)',
                "price": 0
            },
            {
                "value": '22'' (55cm)',
                "price": 0
            },
            {
                "value": '24'' (60cm) ',
                "price": 0
            }
        ]
        return chain_length

    def generate_new_values(self, values, sub_opt_seeds):
        new_values = []
        for value in values:
            new_value = {}
            key = value['key']
            new_value['value'] = value['key']
            new_value['price'] = value['value']
            num = key.split(' ')[0]
            new_value['suboptions'] = self.sub_opts(num, sub_opt_seeds)
            new_values.append(new_value)
        return new_values

    def sub_opts(self, num, sub_opt_seeds):
        result = []
        for i in range(1, int(num) + 1):
            seq = self.number_seq_map(str(i))
            for sub_opt_seed in sub_opt_seeds:
                field = seq + ' ' + sub_opt_seed['field']
                type = self.opt_type_map(sub_opt_seed['type'])
                new_sub_option = self.getnerate_option(0, field, type)
                if type == 1 or type == 2:
                    # new_sub_option['values'] = sub_opt_seed['values']
                    new_sub_option['values'] = self.new_options_map(sub_opt_seed['values'])
                result.append(new_sub_option)
        return result

    def number_seq_map(self, index):
        num_seq = {
            '1': '1st',
            '2': '2nd',
            '3': '3rd',
            '4': '4th',
            '5': '5th',
            '6': '6th',
            '7': '7th',
            '8': '8th',
            '9': '9th',
            '10': '10th',
            '11': '11th',
            '12': '12th',
            '13': '13th',
            '14': '14th',
            '15': '15th',
            '16': '16th',
            '17': '17th',
            '18': '18th',
            '19': '19th',
            '20': '20th'
        }
        if index in num_seq:
            return num_seq[index]
        else:
            return '0th'

    def opt_type_map(self, opt_type):
        types = {
            'text_options': 1,
            'img_options': 2,
            'upload_img': 4,
            'text': 3
        }
        if opt_type in types:
            return types[opt_type]
        else:
            return 0

    # 商品基础数据：goodsSpu
    def parse_goods_spu(self, data: dict) -> dict:
        goodsSpu = {}
        try:
            goodsSpu['goodsNum'] = data['sku']
            goodsSpu['goodsName'] = data['title']
            goodsSpu['mainImg'] = data['mainImg']
            goodsSpu['brief'] = ''
            goodsSpu['description'] = data['description']
            goodsSpu['commentScore'] = random.randint(3, 5)
            goodsSpu['defaultPrice'] = data['discountPrice']
            goodsSpu['shelfTime'] = ''
            goodsSpu['updateTime'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())  # 更新时间
            goodsSpu['purchaseMin'] = 1
            goodsSpu['purchaseMax'] = 999
            goodsSpu['sales'] = random.randint(300, 500)
            goodsSpu['visitNum'] = random.randint(1000, 5000)
            goodsSpu['collection'] = random.randint(200, 600)
            goodsSpu['defaultWeight'] = random.randint(10, 25)
        except Exception as e:
            self.log.error(str(e))
        finally:
            return goodsSpu

    # 商品图片及视频数据：goodsResources
    def parse_goods_resources(self, data: dict) -> list:
        resource = []
        try:
            resource = [{'type': 1, 'url': url} for url in data['images'].split(',')]
        except Exception as e:
            self.log.error(str(e))
        finally:
            return resource

    # 商品定制化参数: goodsOptions
    def parse_options(self, data: dict) -> list:
        options = data['options']
        json_opts = json.loads(options)
        goods_options = []
        for opt in json_opts:
            goods_option = {}
            opt_type = opt['type']
            field = opt['field']
            if 'text_options' == opt_type:
                goods_option = self.getnerate_option(1, field, 1)
                goods_option['values'] = self.new_options_map(opt['values'])
                if "chain length" == field.lower():
                    goods_option['values'] = self.get_chain_length()
            elif 'img_options' == opt_type:
                goods_option = self.getnerate_option(1, field, 2)
                goods_option['values'] = self.new_options_map(opt['values'])
            elif 'upload_img' == opt_type:
                goods_option = self.getnerate_option(1, field, 4)
            elif 'text' == opt_type:
                goods_option = self.getnerate_option(1, field, 3)
            elif 'sub_options' == opt_type:
                goods_option = self.getnerate_option(1, field, 1)
                values = opt['values']
                sub_opt_seeds = opt['subOptions']
                goods_option['values'] = self.generate_new_values(values, sub_opt_seeds)
            goods_options.append(goods_option)
        return goods_options


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


class FileHandler(object):
    def __init__(self):
        pass

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
