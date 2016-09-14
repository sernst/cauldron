import datetime
import json


class ComplexJsonEncoder(json.JSONEncoder):
    """

    """

    def default(self, value):
        if isinstance(value, datetime.date):
            return value.isoformat()
        elif isinstance(value, datetime.datetime):
            return value.isoformat()

        return json.JSONEncoder.default(self, value)
