### 项目介绍

该项目为电商数据服务，整合市面上的主流电商平台数据

### 目标网站

| 目标网站 | 网站地址 | 站点 | product | products | comment|
| :----: | :----: | :----: | :----: | :----: | :----: |
| etsy | https://www.etsy.com | 美国 | √ | × | √ |
| amazon | https://www.amazon.com | 美国 | √ | × |  √|
| wayfair | https://www.wayfair.com | 美国 | √ | × | √ |
| shoplazza | https://www.mobimiu.com | 美国 | √ | √ | × |
| shopify | https://www.maniko-nails.com| 美国 | √ | √ | × |
| aliexpress | https://www.aliexpress.com | 美国 | 仅支持多规格 | × | × |
| vshop | https://www.joyyeco.com | 美国 | 仅支持定制化 | × | × |
| 1688 | https://www.1688.com | 美国 | × | × | × |
### 安装依赖

`pip install -r requirements.txt`

### 启动命令

##### Linux：

`nohup python3 saturn.py`

##### Windows:

###### 后台运行

`start /min python3 saturn.py`

###### 前台运行

`python3 saturn.py`

### 服务API列表

| METHOD | API | 参数 | 说明 |
| :----: | :---: | :---: | :---: |
| POST | /product/ | {"platform": string,"url": string,"source": int} | 获取商品数据 |
| POST | /products/ | {"platform": string,"url": string} | 获取商品列表链接 |
| POST | /comment/ | {"platform": string,"url": string} | 获取商品评论数据 |

[测试链接](http://127.0.0.1:9595/docs)

[服务API查看](http://127.0.0.1:9595/redoc)
