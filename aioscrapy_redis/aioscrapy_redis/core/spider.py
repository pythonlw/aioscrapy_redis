# _*_ coding: utf-8 _*_

import logging

from aioscrapy_redis.https.request import Request
from aioscrapy_redis.core.engine import Engine
from aioscrapy_redis.utils.get_settings import get_project_settings,Base_Settings
from aioscrapy_redis.aioscrapyredis.common import bytes_to_str
default_seting=Base_Settings()
import redis

class Spider(object):
    name = 'aioscrapy'
    redis_key='aioscrapy:url'

    def __init__(self):
        self.setting=get_project_settings()
        '''
        Initialize the start_urls attribute. If the user does not define this method in the crawler file, it will default to an empty list
        '''
        if not hasattr(self, "start_urls"):
            self.start_urls = []
        self.r=redis.Redis(host=self.setting.get('REDIS_HOST',default_seting.get('REDIS_HOST')),
                           port=self.setting.get('REDIS_PORT',default_seting.get('REDIS_PORT')),
                           password=self.setting.get('REDIS_PASSWORD',default_seting.get('REDIS_PASSWORD')),
                           db=self.setting.get('REDIS_DB',default_seting.get('REDIS_DB')))

    def start_requests(self):
        # If self.start_urls is empty, get the url from the redis queue
        self.redis_batch_size = self.setting.get('TASK_NUM',5)
        if len(self.start_urls)==0:
            for i in self.redis_batch_size:
                res=self.r.lpop(self.redis_key)
                if res:
                    self.start_urls.append(res)
        for url in self.start_urls:
            yield Request(url)

    def start(self):
        '''
            * Pass the crawler to the engine to initialize the crawler object
            * engine.start()To start the crawler
        '''
        self.engine = Engine(self)
        # executeThe method encapsulates the event loop and is used to implement the initialization of the crawler
        self.engine.start() # Start crawler

    def next_requests(self):
        self.r.ping()
        fetch_one = self.r.lpop
        found = 0
        while found < self.redis_batch_size:
            data = fetch_one(self.redis_key)
            if not data:
                break
            req = self.make_request_from_data(data)
            if req:
                yield req
                found += 1
            else:
                self.engine.stats.log_count.info("Request not made from data: %r", data)

        self.engine.stats.log_count.info("Read %s requests from '%s'", found, self.redis_key)

    def make_request_from_data(self, data):
        url = bytes_to_str(data, 'utf-8')
        return self.make_requests_from_url(url)

    def make_requests_from_url(self, url):
        return Request(url, dont_filter=True)

    def schedule_next_requests(self):
        return self.next_requests()

    def parse(self, response):
        '''
            Parse the response data returned by the downloader Default parsing callback method
            There are three types of returns:
                * Request
                * dict/str
                * None
        '''
        raise NotImplementedError('{}.parse callback is not defined'.format(self.__class__.__name__))

    def process_item(self,item,spider):
        pass





