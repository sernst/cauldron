import pandas as pd
import numpy as np
from datetime import date

from cauldron.render import texts
from cauldron.test.support import scaffolds


class TestRenderTexts(scaffolds.ResultsTest):
    """

    """

    def test_data_frame(self):
        """

        :return:
        """

        df = pd.DataFrame([
            {'a': 1, 'b': 'hello', 'c': True, 'd': date(2016, 9, 9)},
            {'a': 1, 'b': 'hello', 'c': True, 'd': date(2016, 9, 9)},
            {'a': 1, 'b': 'hello', 'c': True, 'd': date(2016, 9, 9)},
            {'a': 1, 'b': 'hello', 'c': True, 'd': date(2016, 9, 9)}
        ])

        result = texts.head(df, 3)
        self.assertGreater(len(result), 1)

        result = texts.tail(df, 3)
        self.assertGreater(len(result), 1)

    def test_list(self):
        """

        :return:
        """

        source = [
            {'a': 1, 'b': 'hello', 'c': True, 'd': date(2016, 9, 9)},
            {'a': 1, 'b': 'hello', 'c': True, 'd': date(2016, 9, 9)},
            {'a': 1, 'b': 'hello', 'c': True, 'd': date(2016, 9, 9)},
            {'a': 1, 'b': 'hello', 'c': True, 'd': date(2016, 9, 9)}
        ]

        result = texts.head(source, 3)
        self.assertGreater(len(result), 1)

        result = texts.tail(source, 3)
        self.assertGreater(len(result), 1)

    def test_dict(self):
        """

        :return:
        """

        source = {'a': 1, 'b': 'hello', 'c': True, 'd': date(2016, 9, 9)}

        result = texts.head(source, 2)
        self.assertGreater(len(result), 1)

        result = texts.tail(source, 2)
        self.assertGreater(len(result), 1)

    def test_array(self):
        """

        :return:
        """

        array = np.ndarray([1, 2, 3, 4, 5, 6])

        result = texts.head(array, 2)
        self.assertGreater(len(result), 1)

        result = texts.tail(array, 2)
        self.assertGreater(len(result), 1)

    def test_object(self):
        """

        :return:
        """

        class TestObject(object):

            def __str__(self):
                return 'a\nb\nc\nd\ne'

        result = texts.head(TestObject(), 2)
        self.assertGreater(len(result), 1)

        result = texts.tail(TestObject(), 2)
        self.assertGreater(len(result), 1)
