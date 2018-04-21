import builtins
import os
from unittest.mock import patch
from datetime import date

import pandas as pd
from cauldron import render
from cauldron.test.support import scaffolds


class TestRender(scaffolds.ResultsTest):
    """Test suite for the render module"""

    def test_table(self):
        """Should render a table"""

        df = pd.DataFrame([
            {'a': 1, 'b': 'hello', 'c': True, 'd': date(2016, 9, 9)},
            {'a': 1, 'b': 'hello', 'c': True, 'd': date(2016, 9, 9)},
            {'a': 1, 'b': 'hello', 'c': True, 'd': date(2016, 9, 9)},
            {'a': 1, 'b': 'hello', 'c': True, 'd': date(2016, 9, 9)}
        ])

        result = render.table(df, 0.5, include_index=True)
        self.assertGreater(len(result), 1)

    def test_table_series(self):
        """Should render a table for a Series instead of a DataFrame"""

        df = pd.DataFrame([
            {'d': date(2016, 9, 9)},
            {'d': date(2016, 9, 9)},
            {'d': date(2016, 9, 9)},
            {'d': date(2016, 9, 9)}
        ])

        result = render.table(df['d'], 0.5, include_index=False)
        self.assertGreater(len(result), 1)

    def test_table_series_with_index(self):
        """Should render a table for a Series with index"""

        df = pd.DataFrame([
            {'d': date(2016, 9, 9)},
            {'d': date(2016, 9, 9)},
            {'d': date(2016, 9, 9)},
            {'d': date(2016, 9, 9)}
        ])

        result = render.table(df['d'], 0.5, include_index=True)
        self.assertGreater(len(result), 1)

    def test_listing(self):
        """Should render a list of the results"""

        result = render.listing([1, 2, 3, 4, 5])
        self.assertGreater(len(result), 1)

        result = render.listing([1, 2, 3, 4, 5], True)
        self.assertGreater(len(result), 1)

    def test_list_grid(self):
        """Should render a list grid of the results"""

        result = render.list_grid([1, 2, 3, 4, 5])
        self.assertGreater(len(result), 1)

    def test_json(self):
        """Should inject JSON into body"""

        data = {'a': 1, 'b': 'hello', 'c': True, 'd': date(2016, 9, 9)}
        result = render.json(hello=data)
        self.assertGreater(len(result), 1)

    def test_html(self):
        """Should render html"""

        dom = '<div class="test-me">me</div>'

        result = render.html(dom)
        self.assertGreater(len(result), 1)

    def test_code_block_from_file(self):
        """Should render a block of code from the specified path"""

        result = render.code_block(
            path=__file__,
            title='Render Test',
            caption=__file__
        )

        self.assertGreaterEqual(len(result), 1)
        self.assertTrue(result.find('Render Test') != -1)

    def test_code_block_from_string(self):
        """Should render block of code from string argument"""

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

    def test_svg(self):
        """Should properly insert arbitrary svg string"""

        source = '<svg><circle r="1" cx="1" cy="1"></circle></svg>'
        dom = render.svg(source)
        self.assertGreater(dom.find(source), 0)

    def test_code_block_fail(self):
        """Should fail if the open command does not work properly"""

        path = os.path.realpath(__file__)
        with patch('builtins.open') as open_func:
            open_func.side_effect = IOError('Fake Error')
            result = render.code_file(path)

        self.assertEqual(len(result), 0)

    def test_plotly_import_error(self):
        """Should fail if unable to import with plotly"""

        real_import = builtins.__import__

        def fake_import(*args, **kwargs):
            if args and args[0] == 'plotly':
                raise ImportError('Fake Error')
            return real_import(*args, **kwargs)

        with patch('builtins.__import__') as import_func:
            import_func.side_effect = fake_import
            result = render.plotly([], {})

        self.assertGreater(result.find('cd-ImportError'), 0)

    def test_plotly_static(self):
        """Should create a static Plotly plot"""

        trace = dict(
            type='scatter',
            x=[1,2,3,4,5],
            y=[1,2,3,4,5]
        )

        result = render.plotly([trace], {}, static=True)
        self.assertLess(0, result.index('"staticPlot": true'))

    def test_status(self):
        """Should display status of specified data"""

        df = pd.DataFrame([
            {'a': 1, 'b': 2, 'c': 3},
            {'a': 1, 'b': 2, 'c': 3}
        ])

        source = dict(
            a=1,
            b=True,
            c='Hello',
            d=(1, 2, 3),
            e=[{'a': 1}, [1, 2, 3], self],
            f=df
        )

        result = render.status(source)
        self.assertGreater(len(result), 0)

    def test_elapsed(self):
        """Should render an elapsed time"""
        result = render.elapsed_time(3600 + 120 + 12)
        self.assertGreater(result.find('01'), 0)
        self.assertGreater(result.find('02'), 0)
        self.assertGreater(result.find('12'), 0)
