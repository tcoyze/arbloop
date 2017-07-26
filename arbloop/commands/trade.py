# -*- coding: utf-8 -*-
from gevent import monkey
monkey.patch_all()  # noqa

import logging

import click
import gevent
import signal

from arbloop import config
from arbloop.trader import Trader


@click.command(name='trade')
@click.option('--log-level', help='log settings', default='INFO')
@click.option('--live', help='trade live', is_flag=True)
def cli(log_level, live):
    logging.basicConfig(
        filename='arbloop.log',
        format='[%(asctime)s] [%(levelname)s] %(message)s',
        level=log_level
    )
    logging.info('Warming up traders ...')

    gevent.signal(signal.SIGQUIT, gevent.kill)

    workers = []
    for product in config.TRADER_PRODUCTS or []:
        trader = Trader(product=product, live=live)
        workers.append(
            gevent.spawn(trader.trade)
        )
    gevent.joinall(workers)
