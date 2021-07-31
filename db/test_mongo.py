#!/usr/bin/evn python
# -*- coding: utf-8 -*-
# @Time     : 2021/7/27 15:46
# @Author   : dapwn
# @File     : test_mongo.py
# @Software : PyCharm
import unittest
import pymongo


class MongoDBTest(unittest.TestCase):

    def setUp(self) -> None:
        print("MongoDB测试开始...")
        self.db_name = "runoobdb"
        self.my_client = pymongo.MongoClient("mongodb://localhost:27017/")
        self.my_db = self.my_client[self.db_name]

    def test_0_create_db(self):
        db = "runoobdb"
        db_list = self.my_client.list_database_names()
        print(db_list, type(db_list))
        if db in db_list:
            print("数据库已存在！")
        else:
            my_db = self.my_client[db]

    def test_1_create_collection(self):
        db = "runoobdb"
        col = 'sites'
        my_db = self.my_client[db]
        col_list = my_db.list_collection_names()
        print(col_list, type(col_list))
        if col in col_list:
            print("集合已存在！")
        else:
            my_col = my_db[col]

    def test_2_insert(self):
        my_db = self.my_client["runoobdb"]
        # my_col = my_db["sites"]
        #
        # my_dict = {"name": "RUNOOB", "alexa": "10000", "url": "https://www.runoob.com"}
        # # 插入单个文档
        # x = my_col.insert_one(my_dict)
        # print(x)
        # print(x.inserted_id)
        #
        # # 批量插入文档
        # my_list = [
        #     {"name": "Taobao", "alexa": "100", "url": "https://www.taobao.com"},
        #     {"name": "QQ", "alexa": "101", "url": "https://www.qq.com"},
        #     {"name": "Facebook", "alexa": "10", "url": "https://www.facebook.com"},
        #     {"name": "知乎", "alexa": "103", "url": "https://www.zhihu.com"},
        #     {"name": "Github", "alexa": "109", "url": "https://www.github.com"}
        # ]
        #
        # x = my_col.insert_many(my_list)
        # # 输出插入的所有文档对应的 _id 值
        # print(x.inserted_ids)

        # 插入指定_id的多个文档
        my_col_1 = my_db['sites_1']
        my_list_1 = [
            {"_id": 1, "name": "RUNOOB", "cn_name": "菜鸟教程"},
            {"_id": 2, "name": "Google", "address": "Google 搜索"},
            {"_id": 3, "name": "Facebook", "address": "脸书"},
            {"_id": 4, "name": "Taobao", "address": "淘宝"},
            {"_id": 5, "name": "Zhihu", "address": "知乎"}
        ]
        x_1 = my_col_1.insert_many(my_list_1)

        # 输出插入的所有文档对应的 _id 值
        print(x_1.inserted_ids)

    def test_3_find(self):
        my_col_0 = self.my_db['sites']

        # find_one()查询第一条数据
        item = my_col_0.find_one()
        print("查询第一条数据结果：")
        print(item)

        # find()查询所有数据
        items = my_col_0.find()
        print("查询所有数据结果：")
        for item in items:
            print(item)

        # 查询指定字段数据，我们可以使用 find() 方法来查询指定字段的数据，将要返回的字段对应值设置为 1。
        # 除了 _id 你不能在一个对象中同时指定 0 和 1，如果你设置了一个字段为 0，则其他都为 1，反之亦然。
        items = my_col_0.find({}, {"_id": 0, "name": 1, "alexa": 1})
        print("查询指定字段数据结果：")
        for item in items:
            print(item)

        items = my_col_0.find({}, {"name": 1})
        print("只查询name字段结果：")
        for item in items:
            print(item)

        # 根据指定条件查询
        # 我们可以在 find() 中设置参数来过滤数据。
        # 以下实例查找 name 字段为 "RUNOOB" 的数据：
        my_query = {"name": "RUNOOB"}
        items = my_col_0.find(my_query)
        print("根据指定条件查询结果：")
        for item in items:
            print(item)

        # 高级查询
        # 查询的条件语句中，我们还可以使用修饰符。
        # 以下实例用于读取 name 字段中第一个字母 ASCII 值大于 "H" 的数据，大于的修饰符条件为 {"$gt": "H"} :
        my_query = {"name": {"$gt": "H"}}
        items = my_col_0.find(my_query)
        print("name字段中第一个字母ASCII值大于'H'的数据：")
        for item in items:
            print(item)

        # 使用正则表达式查询
        # 我们还可以使用正则表达式作为修饰符。
        # 正则表达式修饰符只用于搜索字符串的字段。
        # 以下实例用于读取 name 字段中第一个字母为 "R" 的数据，正则表达式修饰符条件为 {"$regex": "^R"} :
        my_query = {"name": {"$regex": "^R"}}
        items = my_col_0.find(my_query)
        print("name字段中以R开头的数据：")
        for item in items:
            print(item)

        # 返回指定条数记录
        # 如果我们要对查询结果设置指定条数的记录可以使用 limit() 方法，该方法只接受一个数字参数。
        # 以下实例返回 3 条文档记录：
        items = my_col_0.find().limit(3)
        print("返回查询结果的前3条数据：")
        for item in items:
            print(item)

    def test_4_update(self):
        my_col_0 = self.my_db['sites']

        # update_one() 修改查询的结果的第一条数据
        # 我们可以在 MongoDB 中使用 update_one() 方法修改文档中的记录。该方法第一个参数为查询的条件，第二个参数为要修改的字段。
        # 如果查找到的匹配数据多于一条，则只会修改第一条。
        # 以下实例将 alexa 字段的值 10000 改为 12345:
        my_query = {"alexa": "10000"}
        new_values = {"$set": {"alexa": "12345"}}
        my_col_0.update_one(my_query, new_values)
        # 输出修改后的  "sites"  集合
        for item in my_col_0.find():
            print(item)

        # update_one() 方法只能修匹配到的第一条记录，如果要修改所有匹配到的记录，可以使用 update_many()。
        # 以下实例将查找所有以 R 开头的 name 字段，并将匹配到所有记录的 alexa 字段修改为 123：
        my_query = {"name": {"$regex": "^R"}}
        new_values = {"$set": {"alexa": "123"}}
        items = my_col_0.update_many(my_query, new_values)
        print(items.modified_count, "文档已修改")

    def test_5_sort(self):
        my_col_0 = self.my_db['sites']

        # sort() 方法第一个参数为要排序的字段，第二个字段指定排序规则，1 为升序，-1 为降序，默认为升序。
        print("根据alexa字段升序排序...")
        items = my_col_0.find().sort("alexa")
        for item in items:
            print(item)
        print("根据alexa字段降序排序...")
        items = my_col_0.find().sort("alexa", -1)
        for item in items:
            print(item)

        pass

    def test_6_delete(self):
        my_col_0 = self.my_db['sites']

        # 我们可以使用 delete_one() 方法来删除一个文档，该方法第一个参数为查询对象，指定要删除哪些数据。
        # my_query = {"name": "RUNOOB"}
        # my_col_0.delete_one(my_query)
        # # 删除后输出
        for x in my_col_0.find():
            print(x)
        pass

        # 删除多个数据delete_many
        # my_query = {"name": {"$regex": "^R"}}
        # result = my_col_0.delete_many(my_query)
        # print(result.deleted_count, "个数据被删除")

        # 删除集合中的所有文档
        # x = my_col_0.delete_many({})
        #
        # print(x.deleted_count, "个文档已删除")

        # 删除集合
        # 我们可以使用 drop() 方法来删除一个集合。
        # 以下实例删除了 customers 集合：
        result = my_col_0.drop()
        print(result)

    def tearDown(self) -> None:
        print("MongoDB测试结束...")


if __name__ == '__main__':
    unittest.main()
