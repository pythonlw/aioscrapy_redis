Python async library for web scraping
PyPI version License: MIT

Build Status codecov codebeat badge Codacy Badge

Installing
pip install aioscrapy_redis
Usage
Plain text scraping


from aioscrapy_redis.core.spider import Spider

from aioscrapy_redis.https.request import Request

import re

from urllib.parse import unquote

"""
The start url can be placed in start_urls or written to the redis queue
"""

class Async_Spider(Spider):

    name = 'aioscrapy_spider'

    redis_key = 'aioscrapy_spider:url'
    
    start_urls = []

    def parse(self, response):
        pass


