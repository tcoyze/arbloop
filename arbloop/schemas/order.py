# -*- coding: utf-8 -*-
from marshmallow import Schema, fields


class OrderSchema(Schema):
    product = fields.String()
    long_price = fields.Float()
    long_volume = fields.Float()
    long_exchange = fields.String()
    short_price = fields.Float()
    short_volume = fields.Float()
    short_exchange = fields.String()
    spread = fields.Float()
    exposure = fields.Float()
    long_fee = fields.Float()
    short_fee = fields.Float()
    is_open = fields.Boolean(default=True)
    live = fields.Boolean(default=False)
    created_at = fields.DateTime()
    last_modified = fields.DateTime()
    close_long_price = fields.Float()
    close_short_price = fields.Float()
    close_spread = fields.Float()
    profit = fields.Float()
