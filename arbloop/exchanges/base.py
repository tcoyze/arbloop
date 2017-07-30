# -*- coding: utf-8 -*-
import abc
from collections import defaultdict
import time

from arbloop import config


class Exchange(object):
    __metaclass__ = abc.ABCMeta
    poll_interval = config.EXCHANGE_POLL_INTERVAL

    @abc.abstractproperty
    def update_time(self):
        pass

    @abc.abstractproperty
    def tick(self):
        pass

    @abc.abstractproperty
    def products(self):
        pass

    @abc.abstractproperty
    def shortable(self):
        pass

    @abc.abstractproperty
    def name(self):
        pass

    @abc.abstractproperty
    def account_balances(self):
        pass

    @abc.abstractmethod
    def orderbook(self, product):
        pass

    @abc.abstractmethod
    def buy(self, price, size, product):
        pass

    @abc.abstractmethod
    def sell(self, price, size, product):
        pass

    @abc.abstractproperty
    def fee(self):
        pass

    @abc.abstractmethod
    def ticker(self):
        pass

    @abc.abstractproperty
    def bid(self, product):
        pass

    @abc.abstractproperty
    def ask(self, product):
        pass

    @abc.abstractmethod
    def order(self, id):
        pass

    @abc.abstractmethod
    def orders(self):
        pass

    @property
    def should_update(self):
        if not self.update_time:
            self.update_time = time.time()
            return True

        is_time = (time.time() - self.update_time) > self.poll_interval
        self.update_time = time.time()

        return is_time

    def _clean_orderbook(self, orderbook):
        if orderbook is None:
            return

        if not isinstance(orderbook, dict):
            raise ValueError('orderbook must be a dict')

        _orderbook = defaultdict(list)

        for side in ('bids', 'asks'):
            _orderbook[side] = [
                {'price': float(o[0]), 'volume': float(o[1])}
                for o in orderbook[side]
            ]

        return _orderbook
