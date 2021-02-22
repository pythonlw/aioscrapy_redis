# -*- coding: utf-8 -*- 
# Time:2020/4/2
TASK_NUM = 1 #Number of requests sent each time

TASK_LIMIT=2 #Limit number of tasks

DOWNLOAD_DELAY = 10

DOWNLOADER_MIDDLEWARES = {
   'aioSscrpy_spider.middlewares.UserAgentMiddleware': 200,
}

ITEM_PIPELINES = {
   'aioSscrpy_spider.pipelines.Async_Pipeline': 300,
}

SSL=False

REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB=0
REDIS_PASSWORD = None


TIMEOUT = 50


MYSQL_HOST='127.0.0.1'
MYSQL_PORT=3306
MYSQL_PASSWORD = None
MYSQL_DB = 0



