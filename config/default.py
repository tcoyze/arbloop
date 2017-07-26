# -*- coding: utf-8 -*-
EXCHANGE_POLL_INTERVAL = 60  # in seconds

TRADER_PRODUCTS = [
    'BTC-USD',
    'ETH-USD',
    'LTC-USD',
]
TRADER_EXCHANGES = [
    'gdax',
    'kraken',
]
TRADER_POLL_INTERVAL = 60  # in seconds

MAXIMUM_BALANCE_EXPOSURE = .95  # in fraction of account balance allowed to trade
MAXIMUM_EXPOSURE = 50  # in dollars per product per exchange
EXPOSURE = 100  # in dollars per product per exchange

MAX_TRADE_LIFE = 30 * 24 * 60 * 60  # 30 days in seconds

MINIMUM_SPREAD = 0.01  # as a rate : (bid - ask) / ( bid + ask / 2)
MINIMUM_PROFIT = 0.005  # initial minimum profit to use with decay function
MAXIMUM_SLIPPAGE = 0.001  # rate in between market price and average price

ORDERBOOK_FACTOR = 3.0  # prevents stale orders ensuring liquidity exists

MONGO_HOST = 'localhost'
MONGO_PORT = 27017
MONGO_DB = 'arbloop'
MONGO_COLLECTION = 'trades'

GDAX_FEE = 0.0025
GDAX_PRODUCTS = [
    'BTC-USD',
    'ETH-USD',
    'LTC-USD',
]

KRAKEN_FEE = 0.0026
KRAKEN_PRODUCTS = [
    'BTC-USD',
    'ETH-USD',
    'LTC-USD',
]
