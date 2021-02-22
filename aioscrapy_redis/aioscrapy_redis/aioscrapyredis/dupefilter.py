# -*-coding:utf-8-*-
import logging

import hashlib
import weakref
from aioscrapy_redis.aioscrapyredis.utils.python import to_bytes
from w3lib.url import canonicalize_url

logger = logging.getLogger(__name__)

_fingerprint_cache = weakref.WeakKeyDictionary()

class BaseDupeFilter(object):
    @classmethod
    def from_settings(cls, settings):
        return cls()
    def request_seen(self, request):
        return False
    def open(self):  # can return deferred
        pass
    def close(self, reason):  # can return a deferred
        pass
    def log(self, request, spider):  # log that a request has been filtered
        pass


class RFPDupeFilter(BaseDupeFilter):
    logger = logger
    def __init__(self, server,key, debug=False):
        self.server = server
        self.dupefilter_key = key
        self.debug = debug
        self.logdupes = True

    def request_seen(self, request):
        fp = self.request_fingerprint(request)
        added = self.server.sadd(self.dupefilter_key, fp)
        return added == 0

    def request_fingerprint(self, request,include_headers=None):
        if include_headers:
            include_headers = tuple(to_bytes(h.lower())
                                 for h in sorted(include_headers))
        cache = _fingerprint_cache.setdefault(request, {})
        if include_headers not in cache:
            fp = hashlib.sha1()
            fp.update(to_bytes(request.method))
            fp.update(to_bytes(canonicalize_url(request.url)))
            fp.update(request.body or b'')
            if include_headers:
                for hdr in include_headers:
                    if hdr in request.headers:
                        fp.update(hdr)
                        for v in request.headers.getlist(hdr):
                            fp.update(v)
            cache[include_headers] = fp.hexdigest()
            # print('include_headers:',cache[include_headers])
        return cache[include_headers]

    def close(self, reason=''):
        #Delete data on close. Called by Scrapy's scheduler.
        self.clear()

    def clear(self):
        """Clears fingerprints data."""
        self.server.delete(self.dupefilter_key)

    def log(self, request, spider):
        if self.debug:
            msg = "Filtered duplicate request: %(request)s"
            self.logger.debug(msg, {'request': request}, extra={'spider': spider})
        elif self.logdupes:
            msg = ("Filtered duplicate request %(request)s"
                   " - no more duplicates will be shown"
                   " (see DUPEFILTER_DEBUG to show all duplicates)")
            self.logger.debug(msg, {'request': request}, extra={'spider': spider})
            self.logdupes = False















