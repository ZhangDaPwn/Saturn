#!/usr/bin/evn python
# -*- coding: utf-8 -*-
# @Time     : 2021/7/28 14:58
# @Author   : dapwn
# @File     : model.py
# @Software : PyCharm
from pydantic import BaseModel


class VShopData(object):
    def __init__(self):
        self.data = {
            'goodsSpu': '',  # dict
            'goodsResources': '',  # list
            'goodsOptions': '',  # list
            'skuList': '',  # list
            'goodsComments': ''  # list
        }

    def goods_spu(self):
        data = {}
        data['brief'] = ''
        data['commentScore'] = ''
        data['defaultPrice'] = ''
        data['description'] = ''
        data['goodsName'] = ''
        data['goodsNum'] = ''
        data['mainImg'] = ''
        data['purchaseMax'] = 0
        data['purchaseMin'] = 0
        data['sales'] = 0
        data['shelfTime'] = ''
        data['updateTime'] = ''
        data['visitNum'] = 0
        data['collection'] = 0

        return data

    def goods_resources(self):
        data = []
        item = {}
        item['type'] = 1  # 1.图片 2.视频
        item['url'] = ''  # 图片地址
        data.append(item)

        item = {}
        item['type'] = 2
        item['url'] = ''  # 视频地址
        item['cover'] = ''  # 视频封面
        data.append(item)

        return data

    def goods_options(self):
        data = []
        item = {}
        values = []
        item_value = {}
        item_value['value'] = ''  # 当选项为文本选项时，value值为参数名，当选项为图片选项时，value值为图片url
        item_value['price'] = 0  # 加价
        item_value['type'] = 1  # 1.选项为文本 2.选项为图片
        item_value['tips'] = ''  # 当选项为文本选项时，tips值为空，当选项为图片选项时，value值为图片参数名
        values.append(item_value)

        item['main'] = 1  # 是否为主规格, 0：子规格 1：主规格
        item['field'] = ''  # 规格名称
        item['type'] = 1  # 1.文本选项 2.图片选项
        item['values'] = values

        data.append(item)

        return data

    def sku_list(self):
        data = []
        options = self.goods_options()
        for option in options:
            item = {}
            values = []
            if option['tupe'] == 1:
                for value in option['values']:
                    item_value = {}
                    item_value['propertyValueDisplayName'] = value['value']
                    values.append(item_value)
            elif option['type'] == 2:
                for value in option['values']:
                    item_value = {}
                    item_value['propertyValueDisplayName'] = value['tips']
                    item_value['skuPropertyImagePath'] = value['value']
                    values.append(item_value)
            else:
                pass

            item['skuPropertyName'] = option['field']
            item['skuPropertyValues'] = values
            data.append(item)

        return data

    def goods_comments(self):
        data = []
        item = {}
        item['name'] = ''
        item['comment'] = ''
        item['country'] = ''
        item['commentTime'] = ''
        item['commentResourceList'] = [{'url': '', 'type': 1}]
        item['star'] = ''
        item['reply'] = None  # 是否有回复
        item['status'] = 0  # 状态 0失效  1有效
        item['type'] = 1  # 评论类型 0 自评  1用户评论
        item['name'] = ''


class Product(object):
    data = {}
    id = ''  # 商品id：202185260
    name = ''  # 商品名：Small Triangle Modern Furniture Stencil - Cute Nursery Decor & Painting Dresser Drawers and Table Tops
    url = ''  # 商品链接：https://www.etsy.com/listing/202185260/small-triangle-modern-furniture-stencil
    image = ''  # 主图链接:https://i.etsystatic.com/6104781/r/il/cf10c5/648731468/il_fullxfull.648731468_bwkj.jpg
    brief = ''  # 商品简介
    description = ''  # 商品描述：商品池中的数据，\n等符号无需转换，传给前段时进行转换
    category = ''  # 商品分类:Home & Living
    categoryId = ''  # 商品分类id:68887416
    subCategory = ''  # 子分类: Home Decor > Wall Decor > Wall Stencils
    commentNumber = 0  # 评论数：2597
    ratingNumber = 0  # 评分数：2597
    rating = 0  # 商品评分：4.81 保留两位小数
    regularPrice = 0  # 商品原价：72.47
    price = 0  # 商品默认价格：16.95 保留两位小数
    priceCurrency = 'USD'  # 货币单位
    shelfTime = ''  # 上架时间
    updateTime = ''  # 更新时间
    purchaseMin = 1  # 最小购买数量
    purchaseMax = 1  # 最大购买数量
    sales = 0  # 销量
    visit = 0  # 商品浏览量
    collection = 0  # 商品收藏数量
    brand = ''  # 品牌:RoyalStencils
    logo = ''  # 品牌logo:https://i.etsystatic.com/isla/7e53e6/20577076/isla_fullxfull.20577076_4uyibor2.jpg?version=0
    shopName = ''  # 品牌:RoyalStencils
    shopId = ''  #


class Shop(object):
    id = ''  # 店铺id：6104781
    name = ''  # 店铺名:RoyalStencils
    url = ''  # 店铺url：https://www.etsy.com/shop/RoyalStencils
    logo = ''  # 品牌logo:https://i.etsystatic.com/isla/7e53e6/20577076/isla_fullxfull.20577076_4uyibor2.jpg?version=0


if __name__ == '__main__':
    pass
