# -*- coding: utf-8 -*- 
# Time:2020/4/2
from aioSscrpy_spider.items import NoxUserSpider_Item

class Async_Pipeline():
    def process_item(self,item,spider):
        if isinstance(item,NoxUserSpider_Item):
            print('item:',item)










