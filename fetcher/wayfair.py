#!/usr/bin/evn python
# -*- coding: utf-8 -*-
# @Time     : 2021/7/16 17:48
# @Author   : dapwn
# @File     : wayfair.py
# @Software : PyCharm

"""
-------------------------------------------------
   Description :
   date：          2021/07/16
-------------------------------------------------
-------------------------------------------------
"""
__author__ = 'dapwn'

import random
import re
import json
import demjson
from urllib.parse import urljoin
from urllib import request
from retrying import retry

from helper.spider_helper import SpiderHandler
from handler.log_handler import LogHandler
from utils.ua_wayfair import ua_list
from utils.tools import create_8_digit


class Wayfair(object):
    def __init__(self):
        self.name = 'Wayfair'
        self.log = LogHandler(self.name)
        self.limit = 200

    def parse_sf_ui_header(self, text: str) -> dict:
        data = {}
        try:
            pattern = re.compile(
                r'<script type="text/javascript">window\["sf-ui-header::WEBPACK_ENTRY_DATA"]=(.*?);</script>')
            WEBPACK_ENTRY_DATA = re.findall(pattern, text)[0]
            data = demjson.decode(WEBPACK_ENTRY_DATA)
        except Exception as e:
            self.log.error(e)
        finally:
            return data

    def parse_entry_data(self, text: str) -> dict:
        data = {}
        try:
            pattern = re.compile(r'<script type="text/javascript">window\["WEBPACK_ENTRY_DATA"]=(.*?);</script>')
            WEBPACK_ENTRY_DATA = re.findall(pattern, text)[0]
            data = demjson.decode(WEBPACK_ENTRY_DATA)
        except Exception as e:
            self.log.error(e)
        finally:
            # print("entry_data:", json.dumps(data, indent=2, ensure_ascii=False))
            return data

    # 商品基础数据：goodsSpu
    def parse_goods_spu(self, data: dict, img: str) -> dict:
        goodsSpu = {}
        try:
            data = data['application']
            title = data['props']['title']
            goodsSpu['brief'] = ''
            goodsSpu['commentScore'] = title['customerReviews']['averageRatingValue']
            goodsSpu['defaultPrice'] = data['props']['price']['salePrice']
            # 商品描述等信息
            productOverviewInformation = data['props']['productOverviewInformation']
            description = productOverviewInformation['description']
            extraDetails = productOverviewInformation['extraDetails']
            goodsSpu['description'] = description
            goodsSpu['goodsName'] = title['name']
            goodsSpu['goodsNum'] = title['manufacturerPartNumber']['partNumber']
            goodsSpu['mainImg'] = img
            quantity = data['props']['quantity']
            goodsSpu['purchaseMax'] = quantity['available_quantity']
            goodsSpu['purchaseMin'] = quantity['minimum_order_quantity']
            # 暂未找到的数据
            goodsSpu['sales'] = random.randint(200, 800)
            goodsSpu['shelfTime'] = ''
            goodsSpu['updateTime'] = ''
            goodsSpu['visitNum'] = random.randint(1000, 5000)
            goodsSpu['collection'] = random.randint(800, 1000)
        except Exception as error:
            self.log.error(error)
        finally:
            return goodsSpu

    # 商品图片及视频数据：goodsResources
    def parse_goods_resources(self, data: dict) -> list:
        goodsResources = []
        try:
            # 提取图片资源
            # url = https://secure.img1-fg.wfcdn.com/im/66478205/resize-h2000-w2000%5Ecompr-r85/6647/66478205/Griffin+Glider+and+Ottoman.jpg
            cdn_url = data['application']['props']['applicationContext']['CDN_URL']
            image_items = data['application']['props']['mainCarousel']['items']

            for image_item in image_items:
                item = {}
                image_id = image_item['imageId']
                # width = image_item['width']  # 根据json数据图片宽高，然后拼接可能部分图片有点问题
                # height = image_item['height']
                width = 800
                height = 800
                product_name = data['application']['props']['title']['name']
                image_id_4_digit = str(image_id)[:4]
                words = []
                for word in product_name.split(' '):
                    words.append(request.quote(word))
                image_name = '+'.join(words)
                image_url = urljoin(cdn_url,
                                    'im/{digit_8}/resize-h{height}-w{width}%5Ecompr-r85/{image_id_4_digit}/{image_id}/{image_name}.jpg'.format(
                                        digit_8=create_8_digit(), height=height, width=width,
                                        image_id_4_digit=image_id_4_digit, image_id=image_id, image_name=image_name))
                # print("image_url:", image_url)

                item['url'] = image_url
                item['type'] = 1
                goodsResources.append(item)

        except Exception as e:
            self.log.error(e)
        finally:
            return goodsResources

    # 类型一：展示数据放在props里面
    def parse_options_props(self, data: dict) -> list:
        item_options = []
        try:
            standard_options = data['application']['props']['options']['standardOptions']

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
                                digit_8=create_8_digit(), image_id_4_digit=image_id_4_digit, image_id=thumbnail_id)

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
    def parse_options_apollo(self, data: dict) -> list:
        item_options = []
        try:
            # 显示数据
            apollo_state = data['application']['__APOLLO_STATE__']
            sku = data['application']['props']['sku']  # W003221177
            product_name = "Product:{}".format(sku)  # Product:W003221177

            options = apollo_state[product_name]['options']["optionCategories({\"sort\":\"SELECTION\"})"]

            for option in options:
                print("option:", option)

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
                        print("文本value：", item_value)

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
                            digit_8=create_8_digit(), image_id_4_digit=image_id_4_digit, image_id=image_id,
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

    def parse_options(self, data: dict) -> list:
        options = []
        parse_type = 1  # 解析类型1：从props中提取数据
        try:
            # 显示数据
            apollo_state = data['application']['__APOLLO_STATE__']
            sku = data['application']['props']['sku']  # W003221177
            product_name = "Product:{}".format(sku)  # Product:W003221177

            try:
                if apollo_state[product_name]['sku'] == sku:
                    parse_type = 2  # 解析类型2：从apollo中提取数据
            except:
                pass

            # 解析类型1：从props中提取数据
            if parse_type == 1:
                options = self.parse_options_props(data=data)
            # 解析类型2：从apollo中提取数据
            elif parse_type == 2:
                options = self.parse_options_apollo(data=data)
            else:
                print("暂时未遇到该种类型数据，请联系爬虫工程师添加新的解析规则!")

        except Exception as e:
            self.log.error(e)
        finally:
            return options

    def parse_goods_cust_options(self, data: dict) -> list:
        goodsOptions = []
        try:
            goodsOptions = self.parse_options(data=data)
        except Exception as error:
            self.log.error(error)
        finally:
            return goodsOptions

    def parse_sku_list(self, data: dict) -> list:
        skuList = []
        try:
            options = self.parse_options(data=data)

            for option in options:
                sku_item = {}
                skuPropertyName = option['field']
                type = option['type']
                values = option['values']
                skuPropertyValues = []
                if type == 1:
                    for value in values:
                        item = {}
                        item['propertyValueDisplayName'] = value['value']
                        skuPropertyValues.append(item)
                elif type == 2:
                    for value in values:
                        item = {}
                        item['propertyValueDisplayName'] = value['tips']
                        item['skuPropertyImagePath'] = value['value']
                        skuPropertyValues.append(item)
                else:
                    pass
                sku_item['skuPropertyName'] = skuPropertyName
                sku_item['skuPropertyValues'] = skuPropertyValues
                skuList.append(sku_item)

        except Exception as error:
            self.log.error(error)
        finally:
            return skuList

    # 获取商品全部信息: goodsInfo
    @retry(stop_max_attempt_number=5)
    def get_goods_info(self, text: str, html, source: int) -> dict:
        goodsInfo = {}
        try:
            entry_data = self.parse_entry_data(text=text)
            goodsInfo['goodsResources'] = self.parse_goods_resources(data=entry_data)
            goodsInfo['goodsSpu'] = self.parse_goods_spu(data=entry_data, img=goodsInfo['goodsResources'][0]['url'])

            # 定制化
            if source == 1:
                goodsInfo['goodsOptions'] = self.parse_goods_cust_options(data=entry_data)
                if len(goodsInfo['goodsOptions']) > 0:
                    if len(goodsInfo['goodsOptions'][0]['values']) == 0:
                        raise Exception('goodsOptions value is empty!')
            # 多规格
            elif source == 2:
                goodsInfo['skuList'] = self.parse_sku_list(data=entry_data)
                if len(goodsInfo['skuList']) > 0:
                    if len(goodsInfo['skuList'][0]['skuPropertyValues']) == 0:
                        raise Exception('skuPropertyValues is empty!')

        except Exception as error:
            self.log.error(error)
        finally:
            return goodsInfo

    def main(self, url: str, source: int, goods=1, comment=0) -> dict:
        data = {}
        self.log.info('Fetching Url:{0}, Source:{1}'.format(url, source))
        header = {
            'User-Agent': random.choice(ua_list)
        }

        text = SpiderHandler().get(url=url, header=header).text

        data = self.get_goods_info(text=text, html='', source=source)

        return data


if __name__ == '__main__':
    # url = 'https://www.wayfair.com/furniture/pdp/andover-mills-duquette-2-piece-configurable-living-room-set-w003241867.html'  # 单属性
    # url = 'https://www.wayfair.com/baby-kids/pdp/viv-rae-griffin-glider-and-ottoman-vvre4889.html'  # 一种图片属性
    # url = 'https://www.wayfair.com/baby-kids/pdp/abdiel-platform-standard-bed-w004763304.html'  # 两种属性，全是图片
    # url = 'https://www.wayfair.com/furniture/pdp/hashtag-home-askerby-2675-wide-manual-club-recliner-w001468363.html'  # 一种图片属性,部分商品无货
    # url = 'https://www.wayfair.com/furniture/pdp/greyleigh-aadvik-tufted-upholstered-low-profile-standard-bed-w003221177.html'  # 两种属性，一种图片，一种文字
    # url = 'https://www.wayfair.com/furniture/pdp/andover-mills-drusilla-tufted-upholstered-low-profile-standard-bed-w000221542.html'  # 两种属性，一种图片，一种文字
    # url = 'https://www.wayfair.com/bed-bath/pdp/trent-austin-design-oliver-comforter-set-w005483620.html'  # 两种属性，一种图片，一种文字
    # url = 'https://www.wayfair.com/bed-bath/pdp/yamazaki-home-flow-self-draining-soap-dish-w003042106.html'  # 一种图片属性，展开
    # url = 'https://www.wayfair.com/bed-bath/pdp/millwood-pines-drew-genuine-teak-wood-soap-dish-w004604002.html'  # 无属性
    url = 'https://www.wayfair.com/bed-bath/pdp/mercury-row-eidson-soap-lotion-dispenser-w001590477.html'  # 单图片
    source = 2
    data = Wayfair().main(url=url, source=source)
    print(json.dumps(data, indent=2, ensure_ascii=False))

    # 图片资源
    # https://secure.img1-fg.wfcdn.com/im/61171812/resize-h755-w755%5Ecompr-r85/1328/132829552/Abdiel+Platform+Bed+by+Andover+Mills%E2%84%A2+Baby+%26+Kids.jpg
    # https://secure.img1-fg.wfcdn.com/im/11675153/resize-h800-w800%5Ecompr-r85/5916/59162098/Aadvik+Tufted+Upholstered+Low+Profile+Standard+Bed.jpg
    # 图片选项
    # 从apollo中解析资源，图片选择规格
    # https://secure.img1-fg.wfcdn.com/im/13897026/scale-w88%5Ecompr-r85/8555/85553994/Gray.jpg
    # https://secure.img1-fg.wfcdn.com/im/50063230/scale-w88%5Ecompr-r85/8555/85557778/Light+Gray.jpg
    # 从props中解析资源，图片选择规格
    # https://secure.img1-fg.wfcdn.com/im/27681643/resize-h800-w800%5Ecompr-r85/1278/127896072/default_name.jpg
