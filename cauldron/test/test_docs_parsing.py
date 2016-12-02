from cauldron.docs import parsing as doc_parsing
from cauldron.session import display
from cauldron.test.support import scaffolds


class TestCreate(scaffolds.ResultsTest):
    """

    """

    def test_parse_module(self):
        """"""

        result = doc_parsing.module(display)
        self.assertIsInstance(result, dict)
        self.assertEqual(result['name'], 'cauldron.session.display')
        self.assertIsInstance(result['functions'], list)
        self.assertGreaterEqual(len(result['functions']), 10)
