# _*_ coding: utf-8 _*_
""" Engine """

import asyncio
from datetime import datetime,timedelta
import logging

from aioscrapy_redis.core.scheduler import Scheduler
from aioscrapy_redis.core.downloader.downloader import Downloader
from aioscrapy_redis.utils.tools import result2list
from aioscrapy_redis.https.request import Request
from aioscrapy_redis.utils.get_settings import get_middlewares
from aioscrapy_redis.utils.get_settings import get_pipelines
from aioscrapy_redis.utils.logstats import StatsCollector
from aioscrapy_redis.utils.item import Item
import concurrent

class Engine(object):
    '''
        Engine: used to process crawler files, scheduler, downloader, start and other events
    '''
    def __init__(self, spider):
        self.spider = spider
        self.scheduler = Scheduler(spider)
        self.downloader = Downloader(spider)
        self.middlewares=get_middlewares()
        self.settings = spider.setting
        self.aioScrapy_pipeline=get_pipelines()
        self.loop = asyncio.get_event_loop()
        self.stats = StatsCollector(spider)

    def start(self):
        self.start_time = datetime.now()
        start_requests = iter(self.spider.start_requests())
        self.stats.log(self.start_time, self.start_time, self.spider)
        self.execute(self.spider, start_requests)

    def execute(self, spider, start_requests):
        print('{} {}: spider starttime {}'.format(">"*25,self.spider.name,">"*25) )
        self._init_start_requests(start_requests,spider)
        try:
            #Register the coroutine into the event loop
            self.loop.run_until_complete(self._next_request(spider)) #
        finally:
            executor = concurrent.futures.ThreadPoolExecutor(self.task_limit)
            self.loop.set_default_executor(executor)
            self.loop.run_until_complete(self.loop.shutdown_asyncgens())
            executor.shutdown(wait=True)
            self.loop.close()
            print('{} {}: spider endtime {}'.format(">"*25,self.spider.name,">"*25))
            print('{} total time: {} {}'.format(">" * 25,datetime.now() - self.start_time,"<" * 25))
            self.end_time=datetime.now()
            self.stats.log(self.start_time,self.end_time,spider)

    def _init_start_requests(self, start_requests,spider):
        for req in start_requests:
            self.crawl(req,spider)

    async def _next_request(self, spider):
        self.task_limit = self.settings.get("TASK_LIMIT", 5)
        semaphore = asyncio.Semaphore(value=self.task_limit)
        DOWNLOAD_DELAY = self.settings.get('DOWNLOAD_DELAY',5)
        while True:
            while True:
                for i in range(spider.redis_batch_size):
                    request = self.scheduler.next_request()
                    if not request:
                        continue
                    await semaphore.acquire()
                    self.loop.create_task(self._process_request(request, spider, semaphore))
                if not self.scheduler.has_pending_requests():  #再次判断目前队列的长度
                    break
                await asyncio.sleep(DOWNLOAD_DELAY)

            reqs = spider.schedule_next_requests()
            for req in reqs:
                await semaphore.acquire()
                concurrent_request = self.loop.create_task(self._process_request(req, spider, semaphore))
            await asyncio.sleep(DOWNLOAD_DELAY)

    #Downloader
    async def _process_request(self, request, spider, semaphore):
        '''
        Coroutine method This method takes each request from the scheduler to the downloader for processing
        '''
        try:
            # self.download() The method is re-encapsulated in the engine. The main method to encapsulate the download request in the downloader is the fetch() method
            response = await self.download(request, spider)
            self.end_time = datetime.now()
            inter_val=(self.end_time- self.start_time).seconds
            print('inter_val:',inter_val)
            if  inter_val >= 60:
                self.stats.log(self.start_time,self.end_time,spider)
                self.start_time = self.end_time
        except Exception as exc:
            print('Download error: {}'.format(exc))
        else:
            #Processing the response Passing response (response) request (request) spider (crawler object)
            self._handle_downloader_output(response, request, spider)
        # Release the lock resource. The value of value will increase by one when it is released (+1)
        semaphore.release()

    async def download(self, request, spider):
        '''
        Coroutine method This method is used to encapsulate the request response method in the downloader fetch()
        '''
        #Add download middleware
        for process_request in self.middlewares['process_request']:
            process_request(request,spider)
        self.stats.inc_value('response_received_count', spider=spider)
        response = await self.downloader.fetch(request)
        response.request = request
        if response.exceptions:
            for process_exception in self.middlewares['process_exception']:
                response = process_exception(request,response.exceptions,spider)
            if response:
                return response
        for process_response in self.middlewares['process_response']:
            response = process_response(request,response,spider)
        return response

    def _handle_downloader_output(self, response, request, spider):
        '''
        This method is used to process the response received by the downloader
        '''
        # if isinstance(response, Request):
        #     self.crawl(response)
        #     return
        #If it’s not a request, it’s the data, and the downloaded data is processed for multiple return values
        self.process_response(response, request, spider)

    def process_response(self, response, request, spider):
        '''
        Processing response
        '''
        callback = request.callback or spider.parse
        result = callback(response)
        ret = result2list(result)
        # Process the result returned by the callback function --> handle_spider_output()
        self.handle_spider_output(ret, spider)

    def handle_spider_output(self, result, spider):
        '''
        Centrally process the data returned by the callback function
        :param result: What is the data returned by the callback function from-->result2list()
        '''
        #What is returned in result2list is either a list (two cases) or an iterable request object
        for item in result:
            if item is None:
                continue
            elif isinstance(item, Request):
                self.crawl(item,spider)
            #If the result is a dictionary type, then it is handed over to the pipeline function for processing
            elif isinstance(item, dict) or isinstance(item,Item):
                self.process_item(item, spider)
            else:
                print("The callback function in the crawler file must return the requested data")

    def process_item(self, item, spider):
        '''
        Encapsulate the pipeline function in the crawler. The pipeline function is used to save data and process data
        '''
        spider.process_item(item,spider)
        self.stats.inc_value('item_scraped_count', spider=spider)
        for process_item1 in self.aioScrapy_pipeline['process_item']:
            process_item1(item,spider)

    def crawl(self, request,spider): #
        '''
        Add URL request to queue
        '''
        self.scheduler.enqueue_request(request)









