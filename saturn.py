#!/usr/bin/evn python
# -*- coding: utf-8 -*-
# @Time     : 2021/7/31 10:27
# @Author   : dapwn
# @File     : saturn.py
# @Software : PyCharm
import time
import uvicorn
from fastapi import FastAPI
from typing import Optional
from pydantic import BaseModel, Field
from fetcher.etsy import Etsy
from fetcher.amazon import Amazon
from fetcher.wayfair import Wayfair
from fetcher.shoplazza import Shoplazza
from fetcher.shopify import Shopify
from fetcher.aliexpress import Aliexpress
from settings import BANNER, slogan, PORT
from handler.log_handler import LogHandler

app = FastAPI()
name = 'saturn'
log = LogHandler(name=name)


class Product(BaseModel):
    # platform：目前支持平台：etsy、amazon、wayfair、shoplazza、shopify、aliexpress
    platform: str = Field(..., description="The platform is e-commerce platform")
    # url：商品链接/商品列表链接
    url: str = Field(..., description="Product's url")
    source: Optional[int] = 1    # 1：定制化 2：多规格
    goods: Optional[int] = 1     # 1：抓取 0：不抓取


class Products(BaseModel):
    # platform：目前支持平台：shoplazza、shopify
    platform: str = Field(..., description="The platform is e-commerce platform")
    # url：商品列表链接
    url: str = Field(..., description="Products list url")
    products: Optional[int] = 1  # 1：抓取 0：不抓取


class Comment(BaseModel):
    # platform：目前支持平台：etsy、amazon、wayfair
    platform: str = Field(..., description="The platform is e-commerce platform")
    # url：商品链接
    url: str = Field(..., description="Product's url")
    comment: Optional[int] = 1  # 1：抓取 0：不抓取


@app.get("/")
async def root():
    return {"message": "Welcome to use saturn!"}


@app.post("/product/")
async def product(item: Product):
    start_time = time.time()
    log.info("本次抓取的入参为：", str(item))
    data = {}
    try:
        if item.platform == 'etsy':
            data = Etsy().main(url=item.url, source=item.source, goods=item.goods)
        elif item.platform == 'amazon':
            data = Amazon().main(url=item.url, source=item.source, goods=item.goods)
        elif item.platform == 'wayfair':
            data = Wayfair().main(url=item.url, source=item.source, goods=item.goods)
        elif item.platform == "shoplazza":
            data = Shoplazza().main(url=item.url, source=item.source, goods=item.goods)
        elif item.platform == "shopify":
            data = Shopify().main(url=item.url, source=item.source, goods=item.goods)
        elif item.platform == "aliexpress":
            data = Aliexpress().main(url=item.url, source=item.source, goods=item.goods)
    except Exception as e:
        log.error(str(e))
    finally:
        log.info("抓取成功！抓取平台：{}，数据类型：{}， 抓取耗时：{}".format(item.platform, 'Product', time.time() - start_time))
        return data


@app.post("/products/")
async def products(item: Products):
    start_time = time.time()
    log.info("本次抓取的入参为：", str(item))
    data = {}
    try:
        if item.platform == 'shoplazza':
            data = Shoplazza().main(url=item.url, products=item.products)
        elif item.platform == 'shopify':
            data = Shopify().main(url=item.url, products=item.products)
    except Exception as e:
        log.error(str(e))
    finally:
        log.info("抓取成功！抓取平台：{}，数据类型：{}， 抓取耗时：{}".format(item.platform, 'Product', time.time() - start_time))
        return data


@app.post("/comment/")
async def comment(item: Comment):
    start_time = time.time()
    log.info("本次抓取的入参为：", str(item))
    data = {}
    try:
        if item.platform == 'etsy':
            data = Etsy().main(url=item.url, comment=item.comment)
        if item.platform == 'amazon':
            data = Amazon().main(url=item.url, comment=item.comment)
        elif item.platform == 'wayfair':
            data = Wayfair().main(url=item.url, comment=item.comment)
    except Exception as e:
        log.error(str(e))
    finally:
        log.info("抓取成功！抓取平台：{}，数据类型：{}， 抓取耗时：{}".format(item.platform, 'Comment', time.time() - start_time))
        return data


if __name__ == '__main__':
    print(BANNER)
    print(slogan, '\n')
    uvicorn.run(
        app='saturn:app',
        host='0.0.0.0',  # 配置成0.0.0.0，外网可以进行访问
        port=PORT,
        reload=True,
        debug=True
    )
