# -*- coding: utf-8 -*- 
# Time:2020/4/2

import random
uas=['Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36',
    ]

from aioscrapy_redis.aioscrapyredis.dupefilter import RFPDupeFilter
from aioscrapy_redis.utils.get_settings import get_project_settings
import redis
from aioscrapy_redis.https.html import HtmlResponse
class DupeFilter(RFPDupeFilter): #Delete fingerprint
    def request_seen(self, request):
        fp = self.request_fingerprint(request)
        self.server.srem(self.dupefilter_key, fp)

class UserAgentMiddleware():
    def process_request(self, request, spider):
        request.headers['user-agent'] = random.choice(uas)
    def process_response(self, request, response, spider):
        if response.status not in [200]:
            server = redis.Redis(host=get_project_settings().get('REDIS_HOST'), port=get_project_settings().get('REDIS_PORT'), db=0)
            key = '%(spider)s:dupefilter' % ({'spider': spider.name})
            DupeFilter(server, key).request_seen(request)
            server.rpush(spider.redis_key, request.url)
            response = HtmlResponse(url='exception')
            return response
        else:
            return response

    def process_exception(self, request, exception, spider):
        if exception:
            print('exception::',exception)
            print('request.url:',request.url)



proxy_list=[
'http://127.0.0.1:1080',
'http://127.0.0.1:1080',
]

class ProxyMiddleware():
    def process_request(self, request, spider):
        request.headers['proxy'] = random.choice(proxy_list)
        request.headers['Proxy-Authorization'] = 'username:password'
        request.cookies={}
        request.headers['verify_ssl']=True

    def process_response(self, request, response, spider):
        return response






