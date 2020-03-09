import json
from decimal import Decimal
from datetime import date


class AriosJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, date):
            return '{:%Y-%m-%d}'.format(obj)
        return json.JSONEncoder.default(self, obj)
