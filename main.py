#!/usr/bin/evn python
# -*- coding: utf-8 -*-
# @Time     : 2021/7/31 10:27
# @Author   : dapwn
# @File     : main.py
# @Software : PyCharm
import time
import uvicorn
from fastapi import FastAPI
from typing import Optional
from pydantic import BaseModel, Field

from fetcher.etsy import Etsy
from fetcher.amazon import Amazon
from fetcher.wayfair import Wayfair
from settings import BANNER, slogan, PORT
from handler.log_handler import LogHandler

app = FastAPI()
name = 'main'
log = LogHandler(name=name)


class Product(BaseModel):
    platform: str = Field(..., description="The platform is e-commerce platform")
    url: str = Field(..., description="Product's url")
    source: int = Field(..., description="Product's type")
    goods: Optional[int] = 1
    comment: Optional[int] = 0


class Comment(BaseModel):
    platform: str = Field(..., description="The platform is e-commerce platform")
    url: str = Field(..., description="Product's url")
    goods: Optional[int] = 0
    comment: Optional[int] = 1


@app.get("/")
async def root():
    return {"message": "Welcome to use saturn!"}


@app.post("/product/")
async def product(item: Product):
    start_time = time.time()
    log.info(item)
    data = {}
    try:
        if item.platform == 'etsy':
            data = Etsy().main(url=item.url, source=item.source, goods=item.goods)
        elif item.platform == 'amazon':
            data = Amazon().main(url=item.url, source=item.source, goods=item.goods)
        elif item.platform == 'wayfair':
            data = Wayfair().main(url=item.url, source=item.source, goods=item.goods)
    except Exception as e:
        log.error(str(e))
    finally:
        print("耗时：{}".format(time.time() - start_time))
        return data


@app.post("/comment/")
async def comment(item: Comment):
    start_time = time.time()
    log.info(item)
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
        print("耗时：{}".format(time.time() - start_time))
        return data


if __name__ == '__main__':
    print(BANNER)
    print(slogan, '\n')
    uvicorn.run(
        app='main:app',
        host='localhost',
        port=PORT,
        reload=True,
        debug=True
    )
