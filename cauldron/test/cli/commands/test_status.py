from unittest.mock import patch
from unittest.mock import MagicMock

from cauldron.test import support
from cauldron.test.support import scaffolds
from cauldron.cli.commands import status


class TestStatus(scaffolds.ResultsTest):
    """ """

    def test_status_fail(self):
        """ """

        r = support.run_command('status')
        self.assertTrue(r.failed, 'should have failed without open project')
        self.assertEqual(r.errors[0].code, 'NO_OPEN_PROJECT')

    def test_status(self):
        """ """

        support.run_command('open @examples:seaborn')
        r = support.run_command('status')
        self.assertFalse(r.failed, 'should not have failed')
        self.assertEqual(r.messages[0].code, 'STATUS_CREATED')

    def test_status_with_data(self):
        """ """

        support.run_command('open @examples:hello_text')
        support.run_command('run')
        r = support.run_command('status')
        self.assertFalse(r.failed, 'should not have failed')
        self.assertEqual(r.messages[0].code, 'STATUS_CREATED')

    @patch('cauldron.cli.commands.status.to_console_formatted_string')
    def test_status_failure(self, to_console_formatted_string: MagicMock):
        """ """

        to_console_formatted_string.side_effect = ValueError('Fake Error')

        support.run_command('open @examples:hello_text')
        r = support.run_command('status')
        self.assertTrue(r.failed, 'should have failed')
        self.assertEqual(r.errors[0].code, 'STATUS_ERROR')

    def test_console_formatting(self):
        """ """

        result = status.to_console_formatted_string(dict(
            __cauldron__='SKIP ME',
            complex=self,
            simple=True,
            value='HELLO'
        ))

        self.assertEqual(result.find('SKIP ME'), -1)
        self.assertGreater(result.find('HELLO'), 0)

    def test_status_remote(self):
        """ """

        support.run_command('open @examples:seaborn')
        r = support.run_remote_command('status')
        self.assertFalse(r.failed, 'should not have failed')
        self.assertEqual(r.messages[0].code, 'STATUS_CREATED')
