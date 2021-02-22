# _*_ coding: utf-8 _*_

from urllib.parse import urlencode


def result2list(result):
    '''
    Process the result returned by the callback function
    '''
    if result is None:
        return []
    if isinstance(result, (dict, str)):
        return [result]
    if hasattr(result, "__iter__"):
        return result

# Used in FormRequest
def url_encode(seq, enc):
    values = [(to_bytes(k, enc), to_bytes(v, enc)) for k, vs in seq for v in (vs if is_listlike(vs) else [vs])]
    return urlencode(values, doseq=1)

# Used in FormRequest
def is_listlike(x):
    """
    >>> is_listlike("foo")
    False
    >>> is_listlike(5)
    False
    >>> is_listlike(b"foo")
    False
    >>> is_listlike([b"foo"])
    True
    >>> is_listlike((b"foo",))
    True
    >>> is_listlike({})
    True
    >>> is_listlike(set())
    True
    >>> is_listlike((x for x in range(3)))
    True
    >>> is_listlike(six.moves.xrange(5))
    True
    """
    return hasattr(x, "__iter__") and not isinstance(x, (str, bytes))


def to_bytes(data, encoding=None, errors='strict'):
    if isinstance(data, bytes):
        return data
    if not isinstance(data, str):
        raise TypeError('to_bytes must accept parameter type is: unicode, str or bytes, got {}'.format(type(data).__name__))
    if encoding is None:
        encoding = 'utf-8'
    return data.encode(encoding, errors)

def obsolete_setter(setter, attrname):
    def newsetter(self, value):
        c = self.__class__.__name__
        msg = "%s.%s is not modifiable, use %s.replace() instead" % (c, attrname, c)
        raise AttributeError(msg)
    return newsetter






