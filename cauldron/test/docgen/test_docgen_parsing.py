import random
import typing

import cauldron
from cauldron.docgen import parsing as doc_parsing
from cauldron.session import display
from cauldron.session.exposed import ExposedStep
from cauldron.steptest import StepTestCase
from cauldron.test.support import scaffolds


class TestDocGenParsing(scaffolds.ResultsTest):
    """Test suite for the docgen module"""

    @property
    def test_prop(self) -> typing.Union[str, None, dict]:
        """A test property used to document properties"""
        return random.choice(['hello', None, {}])

    def test_parse_module(self):
        """"""

        result = doc_parsing.container(display)
        self.assertIsInstance(result, dict)
        self.assertEqual(result['name'], 'cauldron.session.display')
        self.assertIsInstance(result['functions'], list)
        self.assertGreaterEqual(len(result['functions']), 10)

    def test_parse_cauldron_module(self):
        """"""

        result = doc_parsing.container(cauldron)
        self.assertIsInstance(result, dict)
        self.assertEqual(result['name'], 'cauldron')
        self.assertIsInstance(result['functions'], list)
        self.assertGreaterEqual(len(result['functions']), 1)

    def test_class(self):
        """"""

        result = doc_parsing.container(ExposedStep)
        self.assertIsInstance(result, dict)
        self.assertIsInstance(result['functions'], list)
        self.assertGreaterEqual(len(result['functions']), 2)

    def test_class_with_props_and_returns(self):
        """"""

        result = doc_parsing.container(StepTestCase)
        self.assertIsInstance(result, dict)
        self.assertIsInstance(result['functions'], list)
        self.assertGreaterEqual(len(result['functions']), 2)
        self.assertIsInstance(result['variables'], list)
        self.assertGreaterEqual(len(result['variables']), 2)

    def test_complex_function_args(self):
        """Should properly parse complex function args"""

        result = doc_parsing.parse_function('plotly', display.plotly)
        self.assertIsInstance(result, dict)

        for param in result['params']:
            self.assertIsInstance(param['type'], str)

    def test_all_optional(self):
        """Should parse optional args correctly"""

        result = doc_parsing.parse_function('markdown', display.markdown)
        self.assertIsInstance(result, dict)

        for param in result['params']:
            self.assertTrue(param['optional'], '{}'.format(param))

    def test_variable(self):
        """Should properly parse a property"""

        result = doc_parsing.variable('test', self.__class__.test_prop)
        self.assertIsInstance(result, dict)

    def test_variable_invalid(self):
        """Should return even if parsing not a property"""

        value = self.test_prop
        result = doc_parsing.variable('test', value)
        self.assertIsInstance(result, dict)
