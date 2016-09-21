import datetime
import json
import numpy as np


class ComplexJsonEncoder(json.JSONEncoder):
    """

    """

    def default(self, value):
        if isinstance(value, datetime.date):
            return value.isoformat()
        elif isinstance(value, datetime.datetime):
            return value.isoformat()
        elif isinstance(value, datetime.time):
            return value.isoformat()
        elif isinstance(value, datetime.timedelta):
            return value.total_seconds()
        elif isinstance(value, (np.int32, np.int64)):
            return int(value)

        return json.JSONEncoder.default(self, value)
