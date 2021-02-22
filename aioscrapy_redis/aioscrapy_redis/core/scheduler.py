# _*_ coding: utf-8 _*_

from aioscrapy_redis.aioscrapyredis.utils.reqser import request_to_dict, request_from_dict

from aioscrapy_redis.aioscrapyredis import picklecompat
from aioscrapy_redis.aioscrapyredis.dupefilter import RFPDupeFilter
from aioscrapy_redis.utils.get_settings import get_project_settings,Base_Settings
default_setting=Base_Settings()

import redis

class Scheduler(object):
    """
     The implementation of the scheduler is mainly the enqueue and dequeue of the request
    """
    def __init__(self, spider):
        self.queue_key = '%(spider)s:requests'% {'spider': spider.name}
        self.dupefilter_key= '%(spider)s:dupefilter'%({'spider': spider.name})
        self.serializer=picklecompat
        self.spider = spider
        self.settings=get_project_settings()
        self.server=redis.Redis(host=self.settings.get('REDIS_HOST',default_setting.get('REDIS_HOST')),
                               port=self.settings.get('REDIS_PORT',default_setting.get('REDIS_PORT')),
                                password=self.settings.get('REDIS_PASSWORD',default_setting.get('REDIS_PASSWORD')),
                               db=self.settings.get('REDIS_DB',default_setting.get('REDIS_DB')))
        self.df = RFPDupeFilter(self.server,self.dupefilter_key)

    def __len__(self):
        self.server.ping()
        return self.server.llen(self.queue_key)

    def enqueue_request(self, request):
        self.server.ping()
        if not request.dont_filter and self.df.request_seen(request):
            return False
        print('Request to be added to the queue --> {}'.format(request))
        obj = request_to_dict(request, self.spider)
        result =  self.serializer.dumps(obj)
        self.server.lpush(self.queue_key,result)
        return True

    def next_request(self):
        self.server.ping()
        data = self.server.rpop(self.queue_key)
        if data:
            obj = self.serializer.loads(data)
            return request_from_dict(obj, self.spider)

    def has_pending_requests(self):
        return self.__len__() > 0



