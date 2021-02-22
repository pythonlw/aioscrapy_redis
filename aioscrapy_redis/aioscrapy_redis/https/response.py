# _*_ coding: utf-8 _*_

from parsel import Selector
from six.moves.urllib.parse import urljoin
from w3lib import html
import os
import json
import weakref
from aioscrapy_redis.https.request import Request

_baseurl_cache = weakref.WeakKeyDictionary()
def get_base_url(response):
    """Return the base url of the given response, joined with the response url"""
    if response not in _baseurl_cache:
        text = response.text[0:4096]
        _baseurl_cache[response] = html.get_base_url(text, response.url,
            response.encoding)
    return _baseurl_cache[response]

def obsolete_setter(setter, attrname):
    def newsetter(self, value):
        c = self.__class__.__name__
        msg = "%s.%s is not modifiable, use %s.replace() instead" % (c, attrname, c)
        raise AttributeError(msg)
    return newsetter

_NONE=object()

class Response(object):
    _cached_decoded_json = _NONE
    def __init__(self, url, status=200, headers=None, body=b'',text='',request=None, flags=None,exceptions=None):
        self.url = url
        self.status = status
        self.headers = headers or {}
        self.request = request
        self._cached_selector = None
        self.flags = [] if flags is None else list(flags)
        self.body=body
        self.text=text
        self.exceptions=exceptions

    @property
    def meta(self):
        try:
            if self.request:
                return self.request.meta
            else:
                print('This request parameter is required')
        except AttributeError:
            raise AttributeError(
                "Response.meta not available, this response "
                "is not tied to any request"
            )

    @property
    def selector(self):
        if self._cached_selector is None:
            encoding=self.request.encoding if self.request.encoding else 'utf-8'
            self._cached_selector = Selector(self.body.decode(encoding))
        return self._cached_selector

    def xpath(self, query, **kwargs):
        return self.selector.xpath(query, **kwargs)

    def css(self, query):
        return self.selector.css(query)

    def urljoin(self, url):
        """Join this Response's url with a possible relative url to form an
        absolute interpretation of the latter."""
        return urljoin(self.url, url)
    def json(self):
        """
        .. versionadded:: 2.2
        Deserialize a JSON document to a Python object.
        """
        if self._cached_decoded_json is _NONE:
            self._cached_decoded_json = json.loads(self.text)
        return self._cached_decoded_json
    def follow(self, url, callback=None, method='GET', headers=None, body=None,
               cookies=None, meta=None, encoding='utf-8', priority=0,
               dont_filter=False, errback=None, cb_kwargs=None):
        #Return a Request object, which can be re-yield to the queue in the spider crawler
        url = self.urljoin(url)
        return Request(url, callback,
                       method=method,
                       headers=headers,
                       body=body,
                       cookies=cookies,
                       meta=meta,
                       encoding=encoding,
                       priority=priority,
                       dont_filter=dont_filter,
                       errback=errback,
                       cb_kwargs=cb_kwargs)










