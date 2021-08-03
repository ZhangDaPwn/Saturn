#!/usr/bin/evn python
# -*- coding: utf-8 -*-
# @Time     : 2021/7/31 11:16
# @Author   : dapwn
# @File     : test_api.py
# @Software : PyCharm
import json
import time
import requests
from settings import COMMENT_PAGE_MAX

ip = '184.169.198.167'
port = 9696


def post_product(data):
    resp = requests.post(url='http://{ip}:{port}/product/'.format(ip=ip, port=port), data=json.dumps(data))
    return resp.json()


def post_comment(data):
    resp = requests.post(url='http://{ip}:{port}/comment/'.format(ip=ip, port=port), data=json.dumps(data))
    return resp.json()


if __name__ == '__main__':
    start_time = time.time()
    # etsy
    total_comment = 499
    platform = 'etsy'
    # url = 'https://www.etsy.com/listing/929635861/set-of-fully-dry-wood-slices-wood-slices'
    url = 'https://www.etsy.com/listing/748928449/bear-necklace-black-or-brown-grizzle'
    # # amazon
    # total_comment = 4201
    # platform = 'amazon'
    # url = 'https://www.amazon.com/PajamaJeans-Womens-Bootcut-Stretch-Bluestone/dp/B079K37FH1'
    # # wayfair
    # total_comment = 15566
    # platform = 'wayfair'
    # url = 'https://www.wayfair.com/furniture/pdp/andover-mills-leni-335-wide-manual-standard-recliner-w005759070.html'
    # total_comment = 7881
    # url = 'https://www.wayfair.com/baby-kids/pdp/viv-rae-griffin-glider-and-ottoman-vvre4889.html'

    comment = {
        'platform': platform,
        'url': url
    }
    result = post_comment(data=comment)
    print(result)
    pic_num = 0
    for item in result['goodsComments']:
        pic_num += len(item['commentResourceList'])
    print("爬取平台：{}，商品总评论数：{}，爬取页数：{}， 有效评论数量：{}，图片数量：{}，耗时：{}".format(platform, total_comment, COMMENT_PAGE_MAX, len(result['goodsComments']), pic_num, time.time() - start_time))




