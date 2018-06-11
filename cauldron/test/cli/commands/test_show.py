from unittest.mock import patch

import cauldron
from cauldron import environ
from cauldron.test import support
from cauldron.test.support import scaffolds


class TestShow(scaffolds.ResultsTest):
    """ """

    def test_show_fail(self):
        """ should fail to show when no project is opened """

        with patch('webbrowser.open') as func:
            r = support.run_command('show')
            self.assertTrue(r.failed, 'should have failed with no project')
            func.assert_not_called()

    def test_show(self):
        """ should show local project """

        support.run_command('open @examples:hello_cauldron')
        url = cauldron.project.get_internal_project().baked_url

        with patch('webbrowser.open') as func:
            r = support.run_command('show')
            self.assertFalse(r.failed, 'should not have failed')
            func.assert_called_once_with(url)

    def test_show_remote(self):
        """ should show remote url """

        remote_connection = environ.RemoteConnection(
            url='http://my-fake.url',
            active=True
        )

        support.run_remote_command(
            command='open @examples:hello_cauldron',
            remote_connection=remote_connection
        )

        project = cauldron.project.get_internal_project()
        url = project.make_remote_url(remote_connection.url)

        with patch('webbrowser.open') as func:
            r = support.run_remote_command(
                command='show',
                remote_connection=remote_connection
            )
            self.assertFalse(r.failed, 'should not have failed')
            func.assert_called_once_with(url)
