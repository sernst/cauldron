from unittest.mock import patch
from unittest.mock import MagicMock

from cauldron.test import support
from cauldron.test.support.messages import Message
from cauldron.test.support import scaffolds


class TestPurge(scaffolds.ResultsTest):
    """ """

    def test_purge_all(self):
        """ should purge current results directory """

        response = support.run_command('purge --force --all')
        self.assertFalse(response.failed, Message(
            'FAILED PURGE ALL',
            'should not have failed to purge all in results directory',
            response=response
        ))

    @patch('cauldron.environ.systems.remove')
    def test_failed_purge(self, remove: MagicMock):
        """ should fail if unable to remove """

        remove.return_value = False

        r = support.run_command('purge --force')
        self.assertTrue(r.failed)
        self.assertEqual(r.errors[0].code, 'PURGE_FAILURE')

    @patch('cauldron.cli.interaction.query.confirm')
    def test_abort(self, confirm: MagicMock):
        """ should fail if unable to remove """

        confirm.return_value = False

        r = support.run_command('purge')
        self.assertFalse(r.failed)
        self.assertEqual(r.messages[0].code, 'NO_PURGE')

    def test_purge_remote(self):
        """ should purge current results directory """

        r = support.run_remote_command('purge --force')
        self.assertFalse(r.failed, 'should not have failed')
