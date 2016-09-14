from datetime import date

import pandas as pd
from cauldron import render
from cauldron.test.support import scaffolds


class TestRenderTexts(scaffolds.ResultsTest):
    """

    """

    def test_table(self):
        """

        :return:
        """

        df = pd.DataFrame([
            {'a': 1, 'b': 'hello', 'c': True, 'd': date(2016, 9, 9)},
            {'a': 1, 'b': 'hello', 'c': True, 'd': date(2016, 9, 9)},
            {'a': 1, 'b': 'hello', 'c': True, 'd': date(2016, 9, 9)},
            {'a': 1, 'b': 'hello', 'c': True, 'd': date(2016, 9, 9)}
        ])

        result = render.table(df, 0.5)
        self.assertGreater(len(result), 1)

    def test_listing(self):
        """

        :return:
        """

        result = render.listing([1, 2, 3, 4, 5])
        self.assertGreater(len(result), 1)

        result = render.listing([1, 2, 3, 4, 5], True)
        self.assertGreater(len(result), 1)

    def test_json(self):
        """

        :return:
        """

        data = {'a': 1, 'b': 'hello', 'c': True, 'd': date(2016, 9, 9)}

        result = render.json('HELLO', data)
        self.assertGreater(len(result), 1)

    def test_html(self):

        dom = '<div class="test-me">me</div>'

        result = render.html(dom)
        self.assertGreater(len(result), 1)

