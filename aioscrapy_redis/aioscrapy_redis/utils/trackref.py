# -*- coding: utf-8 -*- 
# Time:2020/8/4
# Author:lw
import weakref
from time import time
from operator import itemgetter
from collections import defaultdict
NoneType = type(None)
live_refs = defaultdict(weakref.WeakKeyDictionary)


class object_ref:
    """Inherit from this class to a keep a record of live instances"""

    __slots__ = ()

    def __new__(cls, *args, **kwargs):
        obj = object.__new__(cls)
        live_refs[cls][obj] = time()
        return obj





















