# -*- coding: utf-8 -*- 
# Time:2020/4/2
import time
from aioscrapy_redis.core.spider import Spider
from aioscrapy_redis.https.request import Request
import re
from urllib.parse import unquote


class Async_Spider(Spider):
    name = 'aioscrapy_spider'
    redis_key = 'aioscrapy_spider:url'
    start_urls = ['https://hanyu.baidu.com/zici/s?wd=王&query=王']

    def parse(self, response):
        if not response:
            return
        img_url = response.xpath('//img[@id="word_bishun"]/@data-gif').get()
        chinese_character = re.search('wd=(.*?)&', response.url).group(1)
        item = {
            'img_url': img_url,
            'response_url': response.url,
            'chinese_character': unquote(chinese_character)
        }
        yield item
        new_character = response.xpath('//a[@class="img-link"]/@href').getall()
        for character in new_character:
            new_url = 'https://hanyu.baidu.com/zici' + character
            yield Request(url=new_url,
                          callback=self.parse,
                          meta={'items': item}
                          )


if __name__ == '__main__':
    baiduspider = Async_Spider()
    baiduspider.start()




