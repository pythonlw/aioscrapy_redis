# -*- coding: utf-8 -*- 
# Time:2020/4/3

from aioscrapy_redis.utils.log import log_count
import time

class StatsCollector(object):
    def __init__(self,spider):
        self._stats = {}
        self.pagesprev = 0
        self.itemsprev = 0
        self.log_count=log_count(spider)

    def get_value(self, key, default=None, spider=None):
        return self._stats.get(key, default)

    def get_stats(self, spider=None):
        return self._stats

    def set_value(self, key, value, spider=None):
        self._stats[key] = value

    def set_stats(self, stats, spider=None):
        self._stats = stats

    def inc_value(self, key, count=1, start=0, spider=None):
        d = self._stats
        d[key] = d.setdefault(key, start) + count

    def max_value(self, key, value, spider=None):
        self._stats[key] = max(self._stats.setdefault(key, value), value)

    def min_value(self, key, value, spider=None):
        self._stats[key] = min(self._stats.setdefault(key, value), value)

    def clear_stats(self, spider=None):
        self._stats.clear()


    def log(self,starttime,endtime, spider):
        items = self.get_value('item_scraped_count', 0)
        pages = self.get_value('response_received_count', 0)
        irate = items - self.itemsprev
        prate = pages - self.pagesprev
        self.pagesprev, self.itemsprev = pages, items
        msg = ("Crawled %(pages)d pages (at %(pagerate)d pages/min), "
               "scraped %(items)d items (at %(itemrate)d items/min),(starttime:%(start_time)s--endtime:%(end_time)s)")
        log_args = {'pages': pages, 'pagerate': prate,
                    'items': items, 'itemrate': irate,
                    'start_time':starttime.strftime('%Y-%m-%d %H-%M-%S'),
                    'end_time':endtime.strftime('%Y-%m-%d %H-%M-%S')}
        # logger.info(msg, log_args, extra={'spider': spider})
        self.log_count.info(msg, log_args, extra={'spider': spider})

# if __name__ == '__main__':
#     stats=StatsCollector()
#     start_time = time.time()
#     print(start_time)
#     while True:
#         stats.inc_value('key')
#         end_time = time.time()
#         if end_time-start_time >= 6:
#             break
#     print(stats.get_value('key'))






