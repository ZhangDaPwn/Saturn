#!/usr/bin/evn python
# -*- coding: utf-8 -*-
# @Time     : 2021/7/31 11:16
# @Author   : dapwn
# @File     : test_api.py
# @Software : PyCharm
import json

import requests


def post_product(data):
    resp = requests.post(url='http://127.0.0.1:9696/product/', data=json.dumps(data))
    print(resp.json())


def post_comment(data):
    resp = requests.post(url='http://127.0.0.1:9696/comment/', data=json.dumps(data))
    print(json.dumps(resp.json(), indent=2, ensure_ascii=False))


if __name__ == '__main__':
    product = {
        'platform': 'etsy',
        'url': 'https://www.etsy.com/listing/748928449/bear-necklace-black-or-brown-grizzle',
        'source': 1
    }
    comment = {
        'platform': 'etsy',
        'url': 'https://www.etsy.com/listing/748928449/bear-necklace-black-or-brown-grizzle',
    }
    post_product(product)
    post_comment(comment)
