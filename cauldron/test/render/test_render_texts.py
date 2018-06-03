from datetime import date
from unittest.mock import MagicMock
from unittest.mock import patch

import numpy as np
import pandas as pd
from cauldron.render import texts
from cauldron.test.support import scaffolds


class TestRenderTexts(scaffolds.ResultsTest):
    """Test suite for the render texts module"""

    def test_data_frame(self):
        """Should render data Frame"""
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

    def test_head_no_rows(self):
        """Should return an empty string when no rows are set for display."""
        result = texts.head(None, 0)
        self.assertEqual('', result)

    def test_tail_no_rows(self):
        """Should return an empty string when no rows are set for display."""
        result = texts.tail(None, 0)
        self.assertEqual('', result)

    def test_head_empty_data_frame(self):
        """
        Should return an empty string when there are no rows to head.
        """
        result = texts.head(pd.DataFrame([]))
        self.assertEqual('', result)

    def test_tail_empty_data_frame(self):
        """
        Should return an empty string when there are no rows to head.
        """
        result = texts.tail(pd.DataFrame([]))
        self.assertEqual('', result)

    def test_head_string(self):
        """Should show first 3 lines of string"""
        source = 'a\nb\nc\nd\ne\nf'
        result = texts.head(source, 3)
        self.assertTrue(0 < result.find('a\nb\nc'))

    def test_tail_string(self):
        """Should show last 3 lines of string"""
        source = 'a\nb\nc\nd\ne\nf'
        result = texts.tail(source, 3)
        self.assertTrue(0 < result.find('d\ne\nf'))

    def test_head_mock(self):
        """Should show 3 lines of mock object"""
        target = MagicMock()
        target.head.side_effect = ValueError('FAKE')
        target.__len__.return_value = 10
        target.__iter__.return_value = range(10)
        result = texts.head(target, 3)
        self.assertLess(0, len(result), 'Result should not be empty')

    def test_tail_mock(self):
        """Should show last 3 lines of mock object"""
        target = MagicMock()
        target.tail.side_effect = ValueError('FAKE')
        target.__len__.return_value = 10
        target.__iter__.return_value = range(10)
        result = texts.tail(target, 3)
        self.assertLess(
            0, len(result),
            'Result should not be empty'
        )

    def test_list(self):
        """Should render list"""
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
        """Should render dictionary"""
        source = {'a': 1, 'b': 'hello', 'c': True, 'd': date(2016, 9, 9)}

        result = texts.head(source, 2)
        self.assertGreater(len(result), 1)

        result = texts.tail(source, 2)
        self.assertGreater(len(result), 1)

    def test_array(self):
        """Should render array"""
        array = np.ndarray([1, 2, 3, 4, 5, 6])

        result = texts.head(array, 2)
        self.assertGreater(len(result), 1)

        result = texts.tail(array, 2)
        self.assertGreater(len(result), 1)

    def test_object(self):
        """Should render object"""

        class TestObject(object):

            def __str__(self):
                return 'a\nb\nc\nd\ne'

        result = texts.head(TestObject(), 2)
        self.assertGreater(len(result), 1)

        result = texts.tail(TestObject(), 2)
        self.assertGreater(len(result), 1)

    def test_text(self):
        """Should create 3 paragraphs"""
        source = 'a\n \nb\nc\n\nd\n\n\n'
        result = texts.text(source)
        self.assertEqual(3, result.count('</p>'))

    @patch('cauldron.render.texts.md', new=None)
    def test_markdown_unavailable(self, *args):
        """
        Should raise an import error is the markdown package isn't available.
        """
        with self.assertRaises(ImportError):
            texts.markdown('this is a test')

    def test_markdown_unfinished_latex(self):
        """Should not render latex that has no closing $$."""
        source = 'Hello world $$ x_b = 12'
        result = texts.markdown(source)
        self.assertTrue(0 < result['body'].find('$$'))
