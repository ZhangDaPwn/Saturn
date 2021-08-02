#!/usr/bin/evn python
# -*- coding: utf-8 -*-
# @Time     : 2021/7/31 11:16
# @Author   : dapwn
# @File     : test_api.py
# @Software : PyCharm
import json

import requests

ip = '184.169.198.167'
port = 9696


def post_product(data):
    resp = requests.post(url='http://{ip}:{port}/product/'.format(ip=ip, port=port), data=json.dumps(data))
    print(resp.json())


def post_comment(data):
    resp = requests.post(url='http://{ip}:{port}/comment/'.format(ip=ip, port=port), data=json.dumps(data))
    print(resp)
    # print(json.dumps(resp.json(), indent=2, ensure_ascii=False))


if __name__ == '__main__':
    # product = {
    #     'platform': 'etsy',
    #     'url': 'https://www.etsy.com/listing/748928449/bear-necklace-black-or-brown-grizzle',
    #     'source': 1
    # }
    # post_product(product)

    # comment = {
    #     'platform': 'amazon',
    #     'url': 'https://www.amazon.com/Leggings-Depot-JGA2-HCHARCOAL-L-Heather-Charcoal/dp/B0846BZ8RX?th=1',
    # }
    # post_comment(comment)

    comment = {
        'platform': 'wayfair',
        'url': 'https://www.wayfair.com/furniture/pdp/sand-stable-bridget-hall-tree-with-shoe-storage-w003044752.html',
    }
    post_comment(comment)
