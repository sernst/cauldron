import cauldron
from cauldron.docgen import parsing as doc_parsing
from cauldron.session import display
from cauldron.test.support import scaffolds
from cauldron.session.exposed import ExposedStep
from cauldron.steptest import StepTestCase


class TestCreate(scaffolds.ResultsTest):
    """"""

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
