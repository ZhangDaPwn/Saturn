#!/usr/bin/evn python
# -*- coding: utf-8 -*-
# @Time     : 2021/7/31 11:29
# @Author   : dapwn
# @File     : amazon.py
# @Software : PyCharm
import time
import math
import json
import random
from retrying import retry
from selenium import webdriver
from selenium.webdriver import ChromeOptions
from selenium.webdriver.support.wait import WebDriverWait

from utils.ua import ua_pc
from handler.log_handler import LogHandler
from helper.parse_helper import ParseAmazon
from settings import COMMENT_NUMBER_MAX, COMMENT_PAGE_MAX


class Amazon(object):
    def __init__(self):
        self.name = 'Amazon'
        self.log = LogHandler(self.name)
        self.pa = ParseAmazon(text='')
        self.ua = random.choice(ua_pc)
        self.cookie = ''
        self.asin = ''
        self.driver_init()
        self.review = 'https://www.amazon.com/hz/reviews-render/ajax/reviews/get/ref={}'
        self.url_comment_first_page = 'https://www.amazon.com/product-reviews/{}/ref=cm_cr_dp_d_show_all_btm?ie=UTF8&reviewerType=all_reviews'
        self.url_comment_next_page = 'https://www.amazon.com/product-reviews/{}/ref=cm_cr_getr_d_paging_btm_{}?ie=UTF8&pageNumber={}&reviewerType=all_reviews&pageSize=10'
        self.symbols = ["$", "€", "£", "¥", "Kč", "₹", "₪", "₱", "₫", "฿", "NT$", "₺", "zł", "R$"]

    def driver_init(self):
        headless = False
        options = ChromeOptions()
        options.add_experimental_option('excludeSwitches', ['enable-automation'])  # 开发者选项
        options.add_argument('--no-sandbox')  # 沙盒模式
        if headless:
            options.add_argument('--headless')
        options.add_argument('user-agent={}'.format(self.ua))
        self.driver = webdriver.Chrome(chrome_options=options)  # 创建浏览器对象
        # 反反爬：利用js注入，将window.navigator.webdriver = undefined
        self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
            Object.defineProperty(navigator, 'webdriver', {
              get: () => undefined
            })
          """
        })
        self.driver.implicitly_wait(1)
        self.wait = WebDriverWait(driver=self.driver, timeout=10)
        self.driver.maximize_window()

    # ------------------------- selenium操作部分 --------------------
    # 滑动到页面底部
    def scroll_to_bottom(self):
        js1 = "return action=document.body.scrollHeight"
        js2 = "window.scrollTo(0, {})"
        # 获取当前窗口总高度
        height = self.driver.execute_script(js1)
        for i in range(0, height, 1000):
            self.driver.execute_script(js2.format(i))
            time.sleep(0.5)

    # 滑动到指定元素
    def scroll_to_element(self, element):
        # 滑动滚动条到某个指定的元素
        js_script = "arguments[0].scrollIntoView();"
        self.driver.execute_script(js_script, element)

    # 获取商品网页源码
    def get_goods_page_source(self, url):
        page_source = ''
        try:
            self.driver.get(url=url)  # 打开商品页面
            try:
                # 滑动到指定元素：Products related to this item
                element = self.driver.find_element_by_xpath('//div[@id="sponsoredProducts2_feature_div"]')
                self.scroll_to_element(element)
            except:
                self.scroll_to_bottom()
            # 获取网页源码
            page_source = self.driver.page_source
        except Exception as e:
            self.log.error(str(e))
        finally:
            return page_source

    # 获取评论网页源码
    def get_comment_page_source(self, url):
        page_source = ''
        try:
            self.driver.get(url)
            page_source = self.driver.page_source
        except Exception as e:
            self.log.error(str(e))
        finally:
            return page_source

    # 获取商品数据
    def get_goods_info(self, source: int) -> dict:
        goods = {}
        try:
            goods['goodsSpu'] = self.pa.parse_goods_spu
            goods['goodsResources'] = self.pa.parse_goods_resources
            # 定制化
            if source == 1:
                goods['goodsOptions'] = self.pa.parse_options
            # 多规格
            elif source == 2:
                goods['skuList'] = self.pa.parse_sku_list
        except Exception as e:
            self.log.error(str(e))
        finally:
            return goods

    # 获取评论数据
    @retry(stop_max_attempt_number=3)
    def get_comment_info(self, pages) -> list:
        comments = []
        try:
            for page in range(1, pages + 1):
                if page == 1:
                    url = self.url_comment_first_page.format(self.asin)
                    page_source = self.get_comment_page_source(url=url)
                else:
                    url = self.url_comment_next_page.format(self.asin, page, page)
                    page_source = self.get_comment_page_source(url=url)
                comments.extend(self.pa.parse_comment(text=page_source))
                if len(comments) >= COMMENT_NUMBER_MAX:
                    break
        except Exception as e:
            self.log.error(str(e))
        finally:
            # 判断是否需要重试
            if pages > 0 and len(comments) == 0:
                raise Exception('goodsComments is empty!')
            return comments

    def main(self, url: str, source: int = 1, goods: int = 0, comment: int = 0) -> dict:
        data = {}
        try:
            # 只爬去商品信息
            if goods == 1 and comment == 0:
                text = self.get_goods_page_source(url=url)
                self.pa = ParseAmazon(text=text)
                data = self.get_goods_info(source=source)

            # 只爬去评论数据
            elif goods == 0 and comment == 1:
                text = self.get_goods_page_source(url=url)
                self.pa = ParseAmazon(text=text)
                self.asin = self.pa.parse_asin
                comment_number = self.pa.parse_comment_number
                pages = math.ceil(comment_number / 10)
                if pages > COMMENT_PAGE_MAX:
                    pages = COMMENT_PAGE_MAX
                data['goodsComments'] = self.get_comment_info(pages=pages)

            # 爬取商品数据和评论数据
            elif goods == 1 and comment == 1:
                text = self.get_goods_page_source(url=url)
                self.pa = ParseAmazon(text=text)
                data = self.get_goods_info(source=source)

                self.asin = self.pa.parse_asin
                comment_number = self.pa.parse_comment_number
                pages = math.ceil(comment_number / 10)
                if pages > COMMENT_PAGE_MAX:
                    pages = COMMENT_PAGE_MAX
                data['goodsComments'] = self.get_comment_info(pages=pages)
        except Exception as e:
            self.log.error(str(e))
        finally:
            self.driver.close()
            data['source'] = self.name.lower()
            return data


if __name__ == '__main__':
    start_time = time.time()
    url = 'https://www.amazon.com/dp/B07ZD3N123'  # 衣服，图片不全
    url = 'https://www.amazon.com/Apple-MacBook-13-inch-256GB-Storage/dp/B08N5N6RSS/ref=lp_565108_1_8?th=1'
    url = 'https://www.amazon.com/Cruiser-Skateboards-Kids-Teens-Adults-Beginners-Canadian-Skateboard/dp/B08XV2ZNC2/ref=sr_1_1_sspa?dchild=1&keywords=skateboards+and+longboards&pf_rd_i=11051398011&pf_rd_m=ATVPDKIKX0DER&pf_rd_p=861b6c06-8668-44fe-a71e-09a0daba2ded&pf_rd_r=ABVCAYC63TN07S9NVXH4&pf_rd_s=merchandised-search-5&pf_rd_t=101&qid=1625815550&sr=8-1-spons&psc=1&spLa=ZW5jcnlwdGVkUXVhbGlmaWVyPUExUVJBVDlDS0laSjZZJmVuY3J5cHRlZElkPUEwMzc0ODYwUTM2MUFVS05GUlRBJmVuY3J5cHRlZEFkSWQ9QTA5NjYzNTcxVVRWWEpYTUFUSFdRJndpZGdld'
    url = 'https://www.amazon.com/Leggings-Depot-JGA2-HCHARCOAL-L-Heather-Charcoal/dp/B0846BZ8RX?th=1'
    source = 1
    goods = 1
    comment = 1
    data = Amazon().main(url=url, source=source, goods=goods, comment=comment)
    print(json.dumps(data, indent=2, ensure_ascii=False))

    print("耗时：", time.time() - start_time)
