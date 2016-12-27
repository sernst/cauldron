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

        result = render.json(hello=data)
        self.assertGreater(len(result), 1)

    def test_html(self):
        """ should render html """

        dom = '<div class="test-me">me</div>'

        result = render.html(dom)
        self.assertGreater(len(result), 1)

    def test_code_block_from_file(self):
        """ should render a block of code from the specified path """

        result = render.code_block(
            path=__file__,
            title='Render Test',
            caption=__file__
        )

        self.assertGreaterEqual(len(result), 1)
        self.assertTrue(result.find('Render Test') != -1)

    def test_code_block_from_string(self):
        """ should render block of code from string argument """

        block = '\n'.join([
            'function add(a, b) {',
            ' return a + b;',
            '}',
            'var test = add(2, 3);',
            'console.log(test);'
        ])

        result = render.code_block(
            block=block,
            title='Render Test JavaScript',
            caption='This is a caption',
            language='js'
        )

        self.assertGreaterEqual(len(result), 1)
        self.assertTrue(result.find('caption') != -1)
