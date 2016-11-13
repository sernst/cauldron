from unittest.mock import patch

import sys
import cauldron
from cauldron.test import support
from cauldron.test.support import scaffolds
from cauldron.test.support.messages import Message


class TestSnapshot(scaffolds.ResultsTest):
    """

    """

    def test_snapshot_no_command(self):
        """
        """

        support.create_project(self, 'ted')

        r = support.run_command('snapshot')
        self.assertTrue(r.failed, Message(
            'Should fail if there is no command action',
            response=r
        ))

        support.run_command('close')

    def test_snapshot_fail(self):
        """
        """

        support.run_command('close')

        r = support.run_command('snapshot add fake --no-show')
        self.assertTrue(r.failed, Message(
            'should have failed with no project',
            response=r
        ))

    def test_snapshot_open(self):
        """
        """

        support.create_project(self, 'gerald')

        r = support.run_command('snapshot add fake --no-show')
        self.assertFalse(r.failed, Message(
            'should have created snapshot',
            response=r
        ))

        r = support.run_command('snapshot open fake --no-show')
        self.assertFalse(r.failed, Message(
            'should have opened snapshot',
            response=r
        ))

        support.run_command('close')

    def test_snapshot_remove(self):
        """
        """

        support.create_project(self, 'xena')

        r = support.run_command('snapshot add fake --no-show')

        patch_target = 'cauldron.cli.commands.snapshot.actions.query.confirm'
        with patch(patch_target, return_value=True):
            r = support.run_command('snapshot remove fake')
            self.assertFalse(r.failed, Message(
                'should have removed snapshot',
                response=r
            ))

        support.run_command('close')

    def test_snapshot_remove_all(self):
        """
        """

        support.create_project(self, 'veronica')
        support.run_command('snapshot add first --no-show')
        support.run_command('snapshot add second --no-show')

        patch_target = 'cauldron.cli.commands.snapshot.actions.query.confirm'
        with patch(patch_target, return_value=True):
            r = support.run_command('snapshot remove')
            self.assertFalse(r.failed, Message(
                'should have removed all snapshots',
                response=r
            ))

        support.run_command('close')

    def test_snapshot_add(self):
        """
        """

        support.run_command('open @examples:hello_text')
        support.run_command('run')

        with patch('webbrowser.open') as func:
            r = support.run_command('snapshot add fake')
            self.assertFalse(r.failed, 'should not have failed')
            self.assertGreater(func.call_count, 0)

        r = support.run_command('snapshot list')
        self.assertFalse(r.failed, 'should not have failed')

        support.run_command('close')

    def test_autocomplete(self):
        """

        :return:
        """

        support.create_project(self, 'gina')

        result = support.autocomplete('snapshot a')
        self.assertIn('add', result)

        support.run_command('snapshot add TEST --no-show')
        result = support.autocomplete('snapshot remove ')
        self.assertEqual(
            len(result), 1,
            'TEST should be here {}'.format(result)
        )

        support.run_command('close')


