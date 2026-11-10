# -*- coding: utf-8 -*-
import copy
import json

from psycopg2.extras import Json as PsycopgJson

from odoo import fields


class Json(fields.Field):
    """Odoo 15 has no fields.Json (16): the same field, kept in a jsonb column.
    Neither searchable nor mutable in place, like in Odoo 16."""

    type = "json"
    column_type = ("jsonb", "jsonb")

    def convert_to_record(self, value, record):
        """ Return a copy of the value """
        return False if value is None else copy.deepcopy(value)

    def convert_to_cache(self, value, record, validate=True):
        if not value:
            return None
        return json.loads(json.dumps(value))

    def convert_to_column(self, value, record, values=None, validate=True):
        if not value:
            return None
        return PsycopgJson(value)

    def convert_to_export(self, value, record):
        if not value:
            return ""
        return json.dumps(value)
