# -*- coding: utf-8 -*-
from bson import ObjectId
import itertools
import logging
import math
import time

from marshmallow import ValidationError

from arbloop import config
import arbloop.exchanges
from arbloop.schemas.order import OrderSchema
from arbloop.store import MongoStore, now


class Trader(object):
    _exchanges = None

    def __init__(self, product, live=False):
        logging.info('Trader initializing for %s' % product)

        self.product = product
        self.live = live

        self.poll_interval = config.TRADER_POLL_INTERVAL
        self.maximum_balance_exposure = config.MAXIMUM_BALANCE_EXPOSURE
        self.maximum_exposure = config.MAXIMUM_EXPOSURE
        self.exposure = config.EXPOSURE
        self.max_trade_life = config.MAX_TRADE_LIFE
        self.minimum_spread = config.MINIMUM_SPREAD
        self.minimum_profit = config.MINIMUM_PROFIT
        self.maximum_slippage = config.MAXIMUM_SLIPPAGE
        self.orderbook_factor = config.ORDERBOOK_FACTOR

        self.order_store = MongoStore()
        self.order_schema = OrderSchema()

        if len(self.exchanges) < 2:
            raise AttributeError('Arbloop needs at least 2 exchanges enabled')

    def _average(self, *args):
        return float(sum(args)) / len(args)

    def _decay_profit(self, time_passed):
        return self.minimum_profit*math.exp(-0.2*time_passed)

    def _calculate_exposure(self, exchange_a, exchange_b):
        return min([
            exchange_a.account('USD') * self.maximum_balance_exposure,
            exchange_b.account('USD') * self.maximum_balance_exposure,
            self.exposure,
            self.maximum_exposure,
        ])

    def _calculate_slippage(self, avg_price, initial_price):
        return float((avg_price - initial_price)) / initial_price

    def _calculate_spread(self, bid, ask):
        return (bid - ask) / self._average(bid, ask)

    def _limit_volume(self, price, exposure):
        return float(exposure) / price

    def _limit_price(self, orderbook, volume):
        if not orderbook or not volume:
            return (None, None)

        mult_volume = volume * self.orderbook_factor
        _volume = 0.0
        price = 0.0
        weighted_prices = []
        for row in orderbook:
            if _volume >= mult_volume:
                break

            if _volume < volume:
                volume_needed = volume - _volume
                _vol = row['volume']
                if volume_needed < row['volume']:
                    _vol = volume_needed
                weighted_prices.append(_vol * row['price'])

            price = row['price']
            _volume += row['volume']

        avg_price = float(sum(weighted_prices)) / volume
        return price, avg_price

    def handle_open_order(self, order):
        long_exchange = self.exchanges[order['long_exchange']]
        short_exchange = self.exchanges[order['short_exchange']]

        long_volume = order['long_volume']
        short_volume = order['short_volume']

        current_long_limit_price, current_long_avg_price = self._limit_price(
            long_exchange.orderbook(product=self.product)['bids'],
            long_volume
        )
        current_short_limit_price, current_short_avg_price = self._limit_price(
            short_exchange.orderbook(product=self.product)['asks'],
            short_volume
        )

        current_spread = self._calculate_spread(
            current_short_avg_price * (1 + order['short_fee']),
            current_long_avg_price * (1 - order['long_fee'])
        )

        current_profit = order['spread'] - current_spread

        time_delta = now() - order['created_at']
        delta_seconds = time_delta.total_seconds()
        time_passed = float(delta_seconds) / (60 * 60 * 24)
        decayed_profit = self._decay_profit(time_passed)

        is_time_up = delta_seconds >= self.max_trade_life

        if decayed_profit > current_profit and not is_time_up:
            return

        logging.info(
            'Closed order {id} with profit ${profit}'.format(
                id=order['_id'],
                profit=current_profit * order['exposure']
            )
        )

        if self.live:
            long_exchange.sell(
                current_long_limit_price,
                long_volume,
                product=self.product
            )

            short_exchange.buy(
                current_short_limit_price,
                short_volume,
                product=self.product
            )

        self.order_store.collection.update(
            {
                '_id': ObjectId(order['_id'])
            },
            {
                '$set': {
                    'is_open': False,
                    'last_modified': now(),
                    'close_long_price': current_long_avg_price,
                    'close_short_price': current_short_avg_price,
                    'profit': current_profit,
                }
            }
        )

    def check_opp(self, exchange_a, exchange_b):
        a_bid = exchange_a.bid(self.product)
        a_ask = exchange_a.ask(self.product)
        b_bid = exchange_b.bid(self.product)
        b_ask = exchange_b.ask(self.product)

        ba_spread = self._calculate_spread(b_bid, a_ask)
        ab_spread = self._calculate_spread(a_bid, b_ask)

        spread_conditions = any([
            ab_spread >= self.minimum_spread,
            ba_spread >= self.minimum_spread,
        ])
        if not spread_conditions:
            logging.debug('Spread conditions not met for %s' % self.product)
            return

        spread = max([ab_spread, ba_spread])

        if ab_spread == spread and not exchange_a.shortable:
            return

        if ba_spread == spread and not exchange_b.shortable:
            return

        long_exchange, short_exchange = exchange_a, exchange_b

        if ab_spread > ba_spread:
            long_exchange, short_exchange = exchange_b, exchange_a

        exposure = self.exposure

        if self.live:
            exposure = self._calculate_exposure(exchange_a, exchange_b)

        if not exposure:
            return

        long_price = long_exchange.ask(product=self.product)
        long_limit_volume = self._limit_volume(long_price, exposure)

        if not long_limit_volume:
            return

        long_limit_price, long_avg_price = self._limit_price(
            long_exchange.orderbook(product=self.product)['asks'],
            long_limit_volume
        )

        if not long_limit_price:
            return

        short_price = short_exchange.bid(product=self.product)
        short_limit_volume = self._limit_volume(short_price, exposure)

        if not short_limit_volume:
            return

        short_limit_price, short_avg_price = self._limit_price(
            short_exchange.orderbook(product=self.product)['bids'],
            short_limit_volume
        )

        if not short_limit_price:
            return

        short_slippage = self._calculate_slippage(
            short_avg_price,
            short_price
        )
        if short_slippage > self.maximum_slippage:
            logging.debug(
                'Opportunity found, but short limit price beyond slippage'
            )
            return

        long_slippage = self._calculate_slippage(long_avg_price, long_price)
        if long_slippage > self.maximum_slippage:
            logging.debug(
                'Opportunity found, but long limit price beyond slippage'
            )
            return

        limit_spread = self._calculate_spread(
            short_avg_price * (1 - short_exchange.fee),
            long_avg_price * (1 + long_exchange.fee)
        )

        if limit_spread < self.minimum_spread:
            logging.debug('Limit Order Spread less than minimum limit spread')
            return

        if self.live:
            long_exchange.buy(
                long_limit_price,
                long_limit_volume,
                product=self.product
            )

            short_exchange.sell(
                short_limit_price,
                short_limit_volume,
                product=self.product
            )

        order_data = {
            'long_exchange': long_exchange.name,
            'long_price': long_limit_price,
            'long_volume': long_limit_volume,
            'short_exchange': short_exchange.name,
            'short_price': short_limit_price,
            'short_volume': short_limit_volume,
            'spread': limit_spread,
            'short_fee': short_exchange.fee,
            'long_fee': long_exchange.fee,
            'exposure': exposure,
            'product': self.product,
            'live': self.live,
            'is_open': True,
        }

        logging.info('Entering %s Trade @ %s' % (self.product, time.ctime()))

        order, errors = self.order_schema.load(order_data)

        if errors:
            raise ValidationError(errors)

        return self.order_store.store(order)

    def get_open_exchanges(self):
        for exchange in self.exchanges.values():
            orders = self.order_store.list(
                {
                    'is_open': True,
                    'product': self.product,
                    'live': self.live,
                    '$or': [
                        {'long_exchange': exchange.name},
                        {'short_exchange': exchange.name},
                    ]
                },
                projection={'long_exchange': 1, 'short_exchange': 1}
            )

            if orders.count():
                continue

            yield exchange

    def scan(self):
        exchanges = self.get_open_exchanges()
        iterable = itertools.combinations(exchanges, 2)

        for exchange_a, exchange_b in iterable:
            order_id = self.check_opp(exchange_a, exchange_b)

            if order_id is None:
                continue

            logging.info('exectuted order with id %s' % order_id)
            logging.info()

    def trade(self):
        try:
            while True:
                self.check()
                self.scan()
                time.sleep(self.poll_interval)
        except KeyboardInterrupt:
            logging.info('Exiting ...')
        except:
            logging.error('Ratelimit hit ...')
            logging.error('Sleeping for 10 minutes ...')
            time.sleep(60*10)

    def check(self):
        orders = self.order_store.list({
            'is_open': True,
            'product': self.product,
            'live': self.live,
        })
        for order in orders:
            self.handle_open_order(order)

    @property
    def exchanges(self):
        if self._exchanges is not None:
            return self._exchanges

        xch = {}
        for e in arbloop.exchanges.__all__:
            if e.name not in config.TRADER_EXCHANGES:
                continue

            if self.product not in e.products:
                continue

            xch[e.name] = e()

        self._exchanges = xch
        return self._exchanges
