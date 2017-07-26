# -*- coding: utf-8 -*-
import krakenex.api

from arbloop import config
from .base import Exchange


PAIR_MAPPINGS = {
    'BTC-USD': 'XXBTZUSD',
    'ETH-USD': 'XETHZUSD',
    'LTC-USD': 'XLTCZUSD',
}

CURRENCY_MAPPINGS = {
    'USD': 'ZUSD',
    'BTC': 'XXBT',
    'ETH': 'XETH',
    'LTC': 'XLTC',
}

REVERSE_CURRENCY_MAP = {
    'ZUSD': 'USD',
    'XXBT': 'BTC',
    'XETH': 'ETH',
    'XLTC': 'LTC',
}


class Kraken(Exchange):
    name = 'kraken'
    fee = config.KRAKEN_FEE
    api_key = config.KRAKEN_API_KEY
    api_secret = config.KRAKEN_API_SECRET
    products = config.KRAKEN_PRODUCTS
    kraken_client = krakenex.api.API(key=api_key, secret=api_secret)
    public_client = kraken_client.query_public
    private_client = kraken_client.query_private
    shortable = True
    account_balances = {}

    def accounts(self):
        if not self.should_update:
            return self.account_balances

        _accounts = self.private_client('Balance')
        for k, v in _accounts['result'].iteritems():
            self.account_balances[REVERSE_CURRENCY_MAP[k]] = {
                'currency': REVERSE_CURRENCY_MAP[k],
                'balance': float(v),
            }
        return self.account_balances

    def account(self, currency):
        self.accounts()
        return self.account_balances[currency]

    def orderbook(self, product='BTC-USD'):
        asset = PAIR_MAPPINGS[product]
        _orderbook = self.public_client(
            'Depth',
            {'pair': asset, 'count': 20}
        )['result'].get(asset)
        return self._clean_orderbook(_orderbook)

    def buy(self, price, size, product='BTC-USD'):
        asset = PAIR_MAPPINGS[product]
        return self.private_client(
            'AddOrder',
            {
                'pair': asset,
                'type': 'buy',
                'ordertype': 'limit',
                'price': price,
                'volume': size,
            },
        )

    def sell(self, price, size, product='BTC-USD'):
        asset = PAIR_MAPPINGS[product]
        return self.private_client({
            'AddOrder',
            {
                'pair': asset,
                'type': 'sell',
                'ordertype': 'limit',
                'price': price,
                'volume': size,
            }
        })

    def orders(self):
        return self.private_client('OpenOrders')

    def order(self, id):
        return self.private_client('QueryOrders', {'txid': id})

    def bid(self, product='BTC-USD'):
        self.ticker(product=product)
        return self.tick[product]['bid']

    def ask(self, product='BTC-USD'):
        self.ticker(product=product)
        return self.tick[product]['ask']

    def ticker(self, product='BTC-USD'):
        if not self.should_update:
            return
        asset = PAIR_MAPPINGS[product]
        result = self.public_client('Ticker', {'pair': asset})
        self.tick[product]['ask'] = float(result['result'][asset]['a'][0])
        self.tick[product]['bid'] = float(result['result'][asset]['b'][0])
        return self.tick
