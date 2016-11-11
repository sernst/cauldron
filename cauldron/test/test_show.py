import sys
from unittest.mock import patch

import cauldron
from cauldron.test import support
from cauldron.test.support import scaffolds


class TestShow(scaffolds.ResultsTest):
    """

    """

    def test_show_fail(self):
        """

        :return:
        """

        support.run_command('close')

        with patch('webbrowser.open') as func:
            r = support.run_command('show')
            self.assertTrue(r.failed, 'should have failed with no project')
            func.assert_not_called()

    def test_show(self):
        """
        """

        support.run_command('open @examples:hello_cauldron')
        url = cauldron.project.internal_project.baked_url

        with patch('webbrowser.open') as func:
            r = support.run_command('show')
            self.assertFalse(r.failed, 'should not have failed')
            func.assert_called_once_with(url)
        support.run_command('close')
