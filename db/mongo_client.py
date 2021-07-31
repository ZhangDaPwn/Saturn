#!/usr/bin/evn python
# -*- coding: utf-8 -*-
# @Time     : 2021/7/27 17:07
# @Author   : dapwn
# @File     : mongo_client.py
# @Software : PyCharm
import pymongo


class MongoDBClient(object):
    def __init__(self):
        self.db_name = "wayfair"
        self.col_name = "goods"
        self.uri = "mongodb://localhost:27017/"
        self.client = pymongo.MongoClient(self.uri)
        self.db = self.client[self.db_name]
        self.col = self.db[self.col_name]

    def conn(self):
        pass

    def insert_one(self, data: dict):
        result = self.col.insert_one(data)
        print(result, type(result))

    def insert_many(self, data: list):
        self.col.insert_many(data)

    def find_one(self, query: dict):
        return self.col.find_one(query)

    def find_many(self, query: dict):
        return self.col.find(query)

    def update_one(self, query: dict, data: dict):
        self.col.update_one(query, data)

    def update_many(self, query: dict, data: dict):
        self.col.update_many(query, data)

    def delete_one(self, query: dict):
        self.col.delete_one(query)

    def delete_many(self, query: dict):
        self.col.delete_many(query)

    def delete_collection(self):
        self.col.drop()

    def sort(self, key_or_list, direction: int = 1):
        return self.col.find().sort(key_or_list, direction)


if __name__ == '__main__':
    mc = MongoDBClient()

    doc = {"name": "RUNOOB", "alexa": "10000", "url": "https://www.runoob.com"}

    mc.insert_one(data=doc)
