# -*-coding:utf-8-*-
# Time:2020-02-12-17:55
# Author:lw
import copy

import json
import six
from importlib import import_module
from pprint import pformat
from collections import MutableMapping

SETTINGS_PRIORITIES = {
    'default': 0,
    'command': 10,
    'project': 20,
    'spider': 30,
    'cmdline': 40,
}

def get_settings_priority(priority):
    if isinstance(priority, six.string_types):
        return SETTINGS_PRIORITIES[priority]
    else:
        return priority

class SettingsAttribute(object):
    def __init__(self, value, priority):
        self.value = value
        if isinstance(self.value, BaseSettings):
            self.priority = max(self.value.maxpriority(), priority)
        else:
            self.priority = priority

    def set(self, value, priority):
        """Sets value if priority is higher or equal than current priority."""
        if priority >= self.priority:
            if isinstance(self.value, BaseSettings):
                value = BaseSettings(value, priority=priority)
            self.value = value
            self.priority = priority

    def __str__(self):
        return "<SettingsAttribute value={self.value!r} " \
               "priority={self.priority}>".format(self=self)

    __repr__ = __str__

class BaseSettings(MutableMapping):
    def __init__(self, values=None, priority='project'):
        self.frozen = False
        self.attributes = {}
        self.update(values, priority)

    def __getitem__(self, opt_name):
        if opt_name not in self:
            return None
        return self.attributes[opt_name].value

    def __contains__(self, name):
        return name in self.attributes

    def get(self, name, default=None):
        return self[name] if self[name] is not None else default

    def getbool(self, name, default=False):
        got = self.get(name, default)
        try:
            return bool(int(got))
        except ValueError:
            if got in ("True", "true"):
                return True
            if got in ("False", "false"):
                return False
            raise ValueError("Supported values for boolean settings "
                             "are 0/1, True/False, '0'/'1', "
                             "'True'/'False' and 'true'/'false'")

    def getint(self, name, default=0):
        return int(self.get(name, default))

    def getfloat(self, name, default=0.0):
        return float(self.get(name, default))

    def getlist(self, name, default=None):
        value = self.get(name, default or [])
        if isinstance(value, six.string_types):
            value = value.split(',')
        return list(value)

    def getdict(self, name, default=None):
        value = self.get(name, default or {})
        if isinstance(value, six.string_types):
            value = json.loads(value)
        return dict(value)

    def getwithbase(self, name):
        compbs = BaseSettings()
        compbs.update(self[name + '_BASE'])
        compbs.update(self[name])
        return compbs

    def getpriority(self, name):
        if name not in self:
            return None
        return self.attributes[name].priority

    def maxpriority(self):
        if len(self) > 0:
            return max(self.getpriority(name) for name in self)
        else:
            return get_settings_priority('default')

    def __setitem__(self, name, value):
        self.set(name, value)

    def set(self, name, value, priority='project'):
        self._assert_mutability()
        priority = get_settings_priority(priority)
        if name not in self:
            if isinstance(value, SettingsAttribute):
                self.attributes[name] = value
            else:
                self.attributes[name] = SettingsAttribute(value, priority)
        else:
            self.attributes[name].set(value, priority)

    def setdict(self, values, priority='project'):
        self.update(values, priority)

    def setmodule(self, module, priority='project'):
        self._assert_mutability()
        if isinstance(module, six.string_types):
            module = import_module(module)
        for key in dir(module):
            if key.isupper():
                self.set(key, getattr(module, key), priority)

    def update(self, values, priority='project'):
        self._assert_mutability()
        if isinstance(values, six.string_types):
            values = json.loads(values)
        if values is not None:
            if isinstance(values, BaseSettings):
                for name, value in six.iteritems(values):
                    self.set(name, value, values.getpriority(name))
            else:
                for name, value in six.iteritems(values):
                    self.set(name, value, priority)

    def delete(self, name, priority='project'):
        self._assert_mutability()
        priority = get_settings_priority(priority)
        if priority >= self.getpriority(name):
            del self.attributes[name]

    def __delitem__(self, name):
        self._assert_mutability()
        del self.attributes[name]

    def _assert_mutability(self):
        if self.frozen:
            raise TypeError("Trying to modify an immutable Settings object")

    def copy(self):
        return copy.deepcopy(self)

    def freeze(self):
        self.frozen = True

    def frozencopy(self):
        copy = self.copy()
        copy.freeze()
        return copy

    def __iter__(self):
        return iter(self.attributes)

    def __len__(self):
        return len(self.attributes)

    def _to_dict(self):
        return {k: (v._to_dict() if isinstance(v, BaseSettings) else v)
                for k, v in six.iteritems(self)}

    def copy_to_dict(self):
        settings = self.copy()
        return settings._to_dict()

    def _repr_pretty_(self, p, cycle):
        if cycle:
            p.text(repr(self))
        else:
            p.text(pformat(self.copy_to_dict()))

    @property
    def overrides(self):
        try:
            o = self._overrides
        except AttributeError:
            self._overrides = o = _DictProxy(self, 'cmdline')
        return o

    @property
    def defaults(self):
        try:
            o = self._defaults
        except AttributeError:
            self._defaults = o = _DictProxy(self, 'default')
        return o


class _DictProxy(MutableMapping):
    def __init__(self, settings, priority):
        self.o = {}
        self.settings = settings
        self.priority = priority

    def __len__(self):
        return len(self.o)

    def __getitem__(self, k):
        return self.o[k]

    def __setitem__(self, k, v):
        self.settings.set(k, v, priority=self.priority)
        self.o[k] = v

    def __delitem__(self, k):
        del self.o[k]

    def __iter__(self, k, v):
        return iter(self.o)


class Settings(BaseSettings):
    def __init__(self, values=None, priority='project'):
        super(Settings, self).__init__()
        for name, val in six.iteritems(self):
            if isinstance(val, dict):
                self.set(name, BaseSettings(val, 'default'), 'default')
        self.update(values, priority)



