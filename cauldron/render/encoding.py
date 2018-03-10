import datetime
import json
import numpy as np
import pandas as pd
import typing
from collections import namedtuple

from flask.json import JSONEncoder as FlaskJsonEncoder


NOT_OVERRIDEN = namedtuple('NOT_OVERRIDEN', [])


def default_override(value: typing.Any):
    """ """

    if isinstance(value, datetime.date):
        return value.isoformat()
    elif isinstance(value, datetime.datetime):
        return value.isoformat()
    elif isinstance(value, datetime.time):
        return value.isoformat()
    elif isinstance(value, pd.Timestamp):
        return value.to_pydatetime().isoformat()
    elif isinstance(value, np.datetime64):
        return pd.Timestamp(value).to_pydatetime().isoformat()
    elif isinstance(value, datetime.timedelta):
        return value.total_seconds()
    elif isinstance(value, np.ndarray):
        return value.tolist()
    elif isinstance(value, (np.int8, np.int16, np.int32, np.int64)):
        return int(value)
    elif isinstance(value, (np.float16, np.float32, np.float64)):
        return float(value)
    elif isinstance(value, pd.Series):
        return value.tolist()
    elif isinstance(value, bytes):
        return value.decode()

    return NOT_OVERRIDEN()


class ComplexJsonEncoder(json.JSONEncoder):
    """
    Expands JSON encoding to include commonly observed types in scientific
    data, such as dates/times and numpy arrays.
    """

    def default(self, value):
        result = default_override(value)

        return (
            json.JSONEncoder.default(self, value)
            if isinstance(result, NOT_OVERRIDEN) else
            result
        )


class ComplexFlaskJsonEncoder(FlaskJsonEncoder):
    """
    Expands JSON encoding
    """

    def default(self, value):
        result = default_override(value)

        return (
            json.JSONEncoder.default(self, value)
            if isinstance(result, NOT_OVERRIDEN) else
            result
        )
