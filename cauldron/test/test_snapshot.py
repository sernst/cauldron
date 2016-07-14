from unittest.mock import patch

import cauldron
from cauldron.test import support
from cauldron.test.support import scaffolds


class TestSnapshot(scaffolds.ResultsTest):
    """

    """

    def test_snapshot_fail(self):
        """
        """

        support.run_command('close')

        r = support.run_command('snapshot add fake')
        self.assertTrue(r.failed, 'should have failed with no project')

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



