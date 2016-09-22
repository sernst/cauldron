from unittest import mock

from cauldron.cli.interaction import query
from cauldron.test.support import scaffolds


class TestRenderTexts(scaffolds.ResultsTest):
    """

    """

    def test_choice(self):
        """

        :return:
        """

        with mock.patch('builtins.input', return_value=''):
            index, value = query.choice(
                title='Some input',
                prompt='Here are your choices',
                choices=['a', 'b', 'c', 'd'],
                default_index=2
            )
            self.assertEqual(index, 2)
            self.assertEqual(value, 'c')

    def test_confirm(self):
        """

        :return:
        """

        with mock.patch('builtins.input', return_value='y'):
            result = query.confirm(
                question='Ja order Nein',
                default=False
            )
            self.assertTrue(result)

        with mock.patch('builtins.input', return_value='no'):
            result = query.confirm(
                question='Ja order Nein',
                default=False
            )
            self.assertFalse(result)

        with mock.patch('builtins.input', return_value=''):
            result = query.confirm(
                question='Ja order Nein',
                default=False
            )
            self.assertFalse(result)
