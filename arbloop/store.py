# -*- coding: utf-8 -*-
from datetime import datetime

from dateutil.tz import tzutc
import pymongo

from arbloop import config

_missing = object()


def now():
    return datetime.now(tzutc()).replace(microsecond=0)


class MongoStore(object):
    _client = None
    _collection = None

    @property
    def client(self):
        if not self._client:
            client = pymongo.MongoClient(
                host=config.MONGO_HOST,
                port=config.MONGO_PORT,
                tz_aware=True,
                read_preference=pymongo.ReadPreference.NEAREST
            )[config.MONGO_DB]

            self._client = client

        return self._client

    @property
    def collection(self):
        if not self._collection:
            self._collection = self.client[config.MONGO_COLLECTION]
        return self._collection

    def store(self, trade):
        trade['last_modified'] = created_at = now()

        if not trade.get('created_at'):
            trade['created_at'] = created_at

        _id = self.collection.insert_one(
            trade
        ).inserted_id

        return str(_id)

    def list(self, *args, **kwargs):
        cursor = self.collection.find(*args, **kwargs)
        if kwargs.get('batch_size'):
            cursor = cursor.batch_size(kwargs['batch_size'])
        return cursor
