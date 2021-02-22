# -*-coding:utf-8-*-
from aioscrapy_redis.utils.misc import load_object
from aioscrapy_redis.utils.serialize import ScrapyJSONEncoder
from twisted.internet.threads import deferToThread

from . import connection, defaults


default_serialize = ScrapyJSONEncoder().encode


class RedisPipeline(object):
    """Pushes serialized item into a redis list/queue
    REDIS_ITEMS_KEY : str
        Redis key where to store items.
    REDIS_ITEMS_SERIALIZER : str
        Object path to serializer function.
    将item序列化后存入redis
    """

    def __init__(self, server,key=defaults.PIPELINE_KEY,serialize_func=default_serialize):
        self.server = server
        self.key = key
        self.serialize = serialize_func

    def process_item(self, item, spider):
        return deferToThread(self._process_item, item, spider)

    def _process_item(self, item, spider):
        key = self.item_key(item, spider)
        data = self.serialize(item)
        self.server.rpush(key, data)
        return item

    def item_key(self, item, spider):
        """Returns redis key based on given spider.
        """
        return self.key % {'spider': spider.name}
