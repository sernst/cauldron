import unittest
import json
import datetime
import numpy as np
import pandas as pd

from cauldron.render.encoding import ComplexJsonEncoder


class TestRenderEncoding(unittest.TestCase):

    def test_standard_types(self):
        """ should serialize bytes """

        source = dict(a='hello', b=True, c=3.14)
        output = json.dumps(source, cls=ComplexJsonEncoder)
        self.assertIsInstance(output, str)

    def test_bytes(self):
        """ should serialize bytes """

        source = dict(key=b'123456789abcdefghijklmnopqrstuvwxyz')
        output = json.dumps(source, cls=ComplexJsonEncoder)
        self.assertIsInstance(output, str)

    def test_pandas_series(self):
        """ should serialize bytes """

        source = dict(key=pd.Series([1, 2, 3, 4, 5]))
        output = json.dumps(source, cls=ComplexJsonEncoder)
        self.assertIsInstance(output, str)

    def test_date(self):
        """ should serialize datetime.date """

        source = dict(key=datetime.date(2016, 1, 1))
        output = json.dumps(source, cls=ComplexJsonEncoder)
        self.assertIsInstance(output, str)

    def test_datetime(self):
        """ should serialize datetime.datetime """

        source = dict(key=datetime.datetime(2007, 7, 16))
        output = json.dumps(source, cls=ComplexJsonEncoder)
        self.assertIsInstance(output, str)

    def test_time(self):
        """ should serialize datetime.time """

        source = dict(key=datetime.time(8, 7, 16))
        output = json.dumps(source, cls=ComplexJsonEncoder)
        self.assertIsInstance(output, str)

    def test_timedelta(self):
        """ should serialize datetime.timedelta """

        delta = (
            datetime.datetime(2016, 4, 4) -
            datetime.datetime(2014, 3, 12)
        )

        source = dict(key=delta)
        output = json.dumps(source, cls=ComplexJsonEncoder)
        self.assertIsInstance(output, str)

    def test_ndarray(self):
        """ should serialize numpy.ndarray """

        source = dict(key=np.zeros([3, 3]))
        output = json.dumps(source, cls=ComplexJsonEncoder)
        self.assertIsInstance(output, str)

    def test_numpy_ints(self):
        """ should serialize numpy int types """

        source = dict(
            key8=np.int8(12),
            key16=np.int16(12),
            key32=np.int32(12),
            key64=np.int64(12)
        )

        output = json.dumps(source, cls=ComplexJsonEncoder)
        self.assertIsInstance(output, str)

    def test_numpy_floats(self):
        """ should serialize numpy float types """

        source = dict(
            key16=np.float16(np.pi),
            key32=np.float32(np.pi),
            key64=np.float64(np.pi)
        )

        output = json.dumps(source, cls=ComplexJsonEncoder)
        self.assertIsInstance(output, str)

    def test_odd_dates(self):
        """
        Should convert to iso strings where numpy or pandas datetimes are found.
        """
        dt64 = np.datetime64('2002-06-28T01:00:00')
        source = dict(
            datetime64=dt64,
            timestamp=pd.Timestamp(dt64)
        )

        output = json.dumps(source, cls=ComplexJsonEncoder)
        self.assertIsInstance(output, str)
        self.assertEqual(2, output.count('2002-06-28T01:00:00'))
