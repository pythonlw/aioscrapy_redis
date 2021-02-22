# _*_ coding: utf-8 _*_

from w3lib.url import safe_url_string
from aioscrapy_redis.utils.tools import to_bytes,obsolete_setter


class Request(object):
    def __init__(self, url, method='GET', callback=None, priority=0,dont_filter=False,flags=None,
                headers=None, encoding='utf-8', data=None, meta=None,cookies=None,body=None,errback=None, cb_kwargs=None):

        self._encoding = encoding
        self.url = self._set_url(url)
        self.method = method.upper()
        self.callback = callback
        self.headers = headers or {}
        self.data = self._set_data(data)
        self.meta = meta if meta else {}
        self.cookies = cookies or {}
        self.dont_filter = dont_filter
        self._set_body(body)
        self.priority = priority
        self.flags = [] if flags is None else list(flags)
        self._cb_kwargs = dict(cb_kwargs) if cb_kwargs else None
        if errback is not None and not callable(errback):
            raise TypeError('errback must be a callable, got %s' % type(errback).__name__)
        assert callback or not errback, "Cannot use errback without a callback"
        self.errback = errback

    @property
    def cb_kwargs(self):
        if self._cb_kwargs is None:
            self._cb_kwargs = {}
        return self._cb_kwargs

    def _set_url(self, url):
        if not isinstance(url, str):
            raise TypeError('Request url must be str or unicode, got %s:' % type(url).__name__)
        if ':' not in url:
            raise ValueError('URL protocol is incorrect')
        self.url = safe_url_string(url, self.encoding)
        return self.url

    def _set_data(self, data):
        '''
        Form data settings are mainly used for POST forms to convert data into byte form
        :param data: POST data
        :return: Return the POST form data (byte form)
        '''
        if data is None:
           self.data = b''
        else:
            self.data = to_bytes(data, self.encoding)
        return self.data

    def _get_body(self):
        return self._body

    def _set_body(self, body):
        if body is None:
            self._body = b''
        else:
            self._body = to_bytes(body, self.encoding)

    body = property(_get_body, obsolete_setter(_set_body, 'body'))
    @property
    def encoding(self):
        return self._encoding

    def __str__(self):
        return "<%s %s>" % (self.method, self.url)

    __repr__ = __str__

    def copy(self):
        """Return a copy of this Request"""
        return self.replace()

    def replace(self, *args, **kwargs):
        """Create a new Request with the same attributes except for those
        given new values.
        """
        for x in ['url', 'method', 'headers', 'body', 'cookies', 'meta',
                  'encoding', 'priority', 'dont_filter', 'callback']:
            kwargs.setdefault(x, getattr(self, x))
        cls = kwargs.pop('cls', self.__class__)
        return cls(*args, **kwargs)




