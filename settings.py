#!/usr/bin/evn python
# -*- coding: utf-8 -*-
# @Time     : 2021/7/16 14:25
# @Author   : dapwn
# @File     : settings.py
# @Software : PyCharm

BANNER = r"""
      ___           ___                       ___           ___           ___ 
     /  /\         /  /\          ___        /__/\         /  /\         /__/\ 
    /  /:/        /  /::\        /  /\       \  \:\       /  /::\        \  \:\  
   /  /:/ /\     /  /:/\:\      /  /:/        \  \:\     /  /:/\:\        \  \:\  
  /  /:/ /::\   /  /:/ /::\    /  /:/     ___  \  \:\   /  /:/ /:/    _____\__\:\ 
 /__/:/ /:/\:\ /__/:/ /:/\:\  /  /::\    /__/\  \__\:\ /__/:/ /:/___ /__/::::::::\
 \  \:\/:/ /:/ \  \:\/:/__\/ /__/:/\:\   \  \:\ /  /:/ \  \:\/:::::/ \  \:\--\--\/
  \  \::/ /:/   \  \::/      \__\/  \:\   \  \:\  /:/   \  \::/       \  \:\      
   \__\/ /:/     \  \:\           \  \:\   \  \:\/:/     \  \:\        \  \:\     
     /__/:/       \  \:\           \__\/    \  \::/       \  \:\        \  \:\    
     \__\/         \__\/                     \__\/         \__\/         \__\/
"""
slogan = "Welcome to use Saturn! Saturn is a e-commerce aggregation service."
# banner 生成地址：http://www.network-science.de/ascii/  Font：isometric3
# 土星：Saturn，太阳系距离太阳第六远的行星，服务端口号设为：9696
VERSION = "1.0.0"

# ############### server config ###############
HOST = "0.0.0.0"

PORT = 9696

# 评论相关设置
COMMENT_NUMBER_MAX = 500  # 评论爬取上限
COMMENT_PAGE_MAX = 50     # 评论爬取页数上限
COMMENT_WORD_MAX = 3000   # 单条评论字数上限
NICK_WORD_MAX = 100       # 评论用户名字数上限
REPLY_WORD_MAX = 300      # 回复评论字数上限



