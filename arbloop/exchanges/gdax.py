# -*- coding: utf-8 -*-
from __future__ import absolute_import
from collections import defaultdict

import gdax as gdax_client

from arbloop import config
from .base import Exchange


class GDAX(Exchange):
    name = 'gdax'
    fee = config.GDAX_FEE
    api_key = config.GDAX_API_KEY
    api_secret = config.GDAX_API_SECRET
    api_passphrase = config.GDAX_API_PASSPHRASE
    products = config.GDAX_PRODUCTS
    public_client = gdax_client.PublicClient()
    private_client = gdax_client.AuthenticatedClient(
        api_key,
        api_secret,
        api_passphrase
    )
    shortable = True
    account_balances = {}
    update_time = None
    tick = defaultdict(dict)

    def accounts(self):
        if not self.should_update:
            return self.account_balances

        _accounts = self.private_client.get_accounts()
        for acc in _accounts:
            self.account_balances[acc['currency']] = {
                'currency': acc['currency'],
                'balance': float(acc['balance']),
            }
        return self.account_balances

    def account(self, currency=None, id=None):
        if currency is None and id is None:
            raise ValueError('Currency or id must be passed in')

        self.accounts()
        return self.account_balances[currency]

    def orderbook(self, product='BTC-USD'):
        _orderbook = self.public_client.get_product_order_book(
            level=2,
            product_id=product
        )

        return self._clean_orderbook(_orderbook)

    def buy(self, price, size, product='BTC-USD'):
        return self.private_client.buy(**{
            'type': 'limit',
            'product': product,
            'price': price,
            'size': size,
        })

    def sell(self, price, size, product='BTC-USD'):
        return self.private_client.sell(**{
            'type': 'limit',
            'product': product,
            'price': price,
            'size': size,
        })

    def orders(self):
        return self.private_client.get_orders()

    def order(self, id):
        return self.private_client.get_order(id)

    def bid(self, product='BTC-USD'):
        self.ticker()
        return self.tick[product]['bid']

    def ask(self, product='BTC-USD'):
        self.ticker()
        return self.tick[product]['ask']

    def ticker(self):
        if not self.should_update and self.tick and all(self.tick.values()):
            return self.tick

        for product in self.products:
            result = self.public_client.get_product_ticker(product_id=product)
            self.tick[product]['bid'] = float(result['bid'])
            self.tick[product]['ask'] = float(result['ask'])

        return self.tick


gdax = GDAX()
