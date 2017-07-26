# Arbloop :coffin:

---

Not much of a README right now

Disclaimer: Seriously, don't use real money.

### Who

Who, who

What are you? An owl?

### What

Arbloop is an automated cryptocurrency arbitrage trader.

Literally it does nothing else.

### Where

Hmm...

### When

One hacknight spread out over a few months.

### Why?

I'm still wondering why I did this.

Perhaps to start and finish a project?

Perhaps to gain some insight into gevent, python, and arbitrage?

Perhaps to earn a few coins to stake a gerbil in a poker game?

Perhaps to be a normiecoin magnate?

### Dependencies

* mongo (make sure you have it running ...)

### Install

```
    git clone
    cd arbloop
    virtualenv venv
    . ./venv/bin/activate
    pip install -r requirements.txt
```

### Setup

Create a file called `config.py` in the instance folder.
Place all of your api credentials in there ...
Checkout `sample_config.py` for a sample ...

### Run

paper trade:

```
    python manage.py trade
```

with real money:

```
    python manage.py trade --live
```

Arbloop writes logs to `arbloop.log`

### Monies

* Bitcoin

* Ethereum

* Litecoin

* More to come ...

### Exchanges

* [GDAX](https://github.com/danpaquin/GDAX-Python)

* [Kraken](https://github.com/veox/python2-krakenex)

* More to come ...

### TODO

* Fees per product per exchange

* Clean up logging

* Clean up trader

* Implement more exchanges

* Allow for dynamic setup of tradeable assets

* Rewrite Kraken client

* Profit

### Treats

Send your thots and prayers in crypto to:

BTC: 174R9c3XNdHZnqV4iWym2ntvUSu5d2nT3J

ETH: 0x83A776DB2e79e9BeB0A07A93c0d5D768Ff6D933C

LTC: LdTXkf5bZ64t9ai9b4kejkgC6onF2b9PRD