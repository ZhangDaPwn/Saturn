#!/usr/bin/evn python
# -*- coding: utf-8 -*-
# @Time     : 2021/7/16 14:36
# @Author   : dapwn
# @File     : log_handler.py
# @Software : PyCharm
"""
-------------------------------------------------
   Description :  日志操作模块
   date：          2021/7/16
-------------------------------------------------
屏幕输出/文件输出 可选(默认屏幕和文件均输出)
 Windows下TimedRotatingFileHandler线程不安全
 开发环境时，使用，正式环境时，Windows下不使用

-------------------------------------------------
"""
__author__ = 'dapwn'

import os
import logging
import platform
from logging.handlers import TimedRotatingFileHandler

# 日志级别
CRITICAL = 50  # 危险的
FATAL = CRITICAL  # 致命的
ERROR = 40  # 错误
WARNING = 30  # 警告
WARN = WARNING  # 警告
INFO = 20  # 信息级别
DEBUG = 10  # 调试
NOTSET = 0  # 不设置

CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))
ROOT_PATH = os.path.join(CURRENT_PATH, os.pardir)
LOG_PATH = os.path.join(ROOT_PATH, 'log')

# print(CURRENT_PATH, '\n', ROOT_PATH, '\n', LOG_PATH)

if not os.path.exists(LOG_PATH):
    try:
        os.mkdir(LOG_PATH)
    except FileExistsError:
        pass


class LogHandler(logging.Logger):
    """
    LogHandler
    """

    def __init__(self, name, level=DEBUG, stream=True, file=True):
        self.name = name
        self.level = level
        logging.Logger.__init__(self, self.name, level=level)
        if stream:
            self.__set_stream_handler__()
        if file:
            # if platform.system() != "Windows":  # 禁止Windows下使用TimedRotatingFileHandler定时模块
            self.__set_file_handler__()

    # logging模块自带的三个handler之一。继承自StreamHandler。将日志信息输出到磁盘文件上。
    def __set_file_handler__(self, level=None):
        """
        set file handler
        :param level:
        :return:
        """
        file_name = os.path.join(LOG_PATH, '{name}.log'.format(name=self.name))
        # 设置日志回滚，保存在log目录，一天保存一个文件，保留15天
        file_handler = TimedRotatingFileHandler(filename=file_name, when='D', interval=1, backupCount=15)
        file_handler.suffix = '%Y%m%d.log'
        if not level:
            file_handler.setLevel(self.level)
        else:
            file_handler.setLevel(level)
        # 日志格式化:2021-07-16 15:30:44,963 log_handler.py[line:105] INFO this is a test msg
        formatter = logging.Formatter('%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s')

        file_handler.setFormatter(formatter)
        self.file_handler = file_handler
        self.addHandler(file_handler)  # 动态增加logger handler

    # 设置流handler，logging三个自带handler之一：能够将日志信息输入到sys.stdout,sys.stderr 或者类文件对象（更确切点，就是能够支持write()和flush()方法的对象）。
    def __set_stream_handler__(self, level=None):
        """
        set stream handler
        :param level:
        :return:
        """
        stream_handler = logging.StreamHandler()
        # 日志格式化:2021-07-16 15:30:44,963 log_handler.py[line:105] INFO this is a test msg
        formatter = logging.Formatter('%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s')
        stream_handler.setFormatter(formatter)
        if not level:
            stream_handler.setLevel(self.level)
        else:
            stream_handler.setLevel(level)
        self.addHandler(stream_handler)


if __name__ == '__main__':
    log = LogHandler('test')
    log.info('this is a test msg')
