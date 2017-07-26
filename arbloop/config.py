# -*- coding: utf-8 -*-
from __future__ import absolute_import
import importlib
import os
import sys


ROOT_PATH = os.path.join(os.path.dirname(__file__), '..')


class ConfigModule(dict):
    def __init__(self):
        self['ROOT_PATH'] = ROOT_PATH

        ARBLOOP_ENV = os.environ.get('ARBLOOP_ENV', 'default')
        self['ARBLOOP_ENV'] = ARBLOOP_ENV

        envs = ('default',)
        if ARBLOOP_ENV is 'production':
            envs = ('default', 'development', 'production')
        elif ARBLOOP_ENV is 'development':
            envs = ('default', 'development')

        for name in envs:
            self.from_object('config.%s' % name)

        if os.path.exists(os.path.join(ROOT_PATH, 'instance', 'config.py')):
            self.from_object('instance.config')

    def __getattr__(self, attr):
        try:
            return self[attr]
        except KeyError:
            raise AttributeError(
                "'%s' has no attribute '%s'" % (self.__name__, attr)
            )

    def from_object(self, obj):
        if isinstance(obj, (str, unicode)):
            obj = importlib.import_module(obj)

        for attr in dir(obj):
            if not attr[0].isupper():
                continue
            self[attr] = getattr(obj, attr)


sys.modules[__name__] = ConfigModule()
