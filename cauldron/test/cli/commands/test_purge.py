from unittest.mock import patch
from unittest.mock import MagicMock

from cauldron.test import support
from cauldron.test.support.messages import Message
from cauldron.test.support import scaffolds


def _create_mock_project():
    """Helper function for creating a mock internal project."""
    project = MagicMock()
    project.steps = [MagicMock()]
    return project


class TestPurge(scaffolds.ResultsTest):
    """..."""

    @patch('cauldron.environ.systems.remove')
    def test_purge_all(self, remove: MagicMock):
        """Should purge current results directory."""
        response = support.run_command('purge --yes --all')
        self.assertFalse(response.failed, Message(
            'FAILED PURGE ALL',
            'should not have failed to purge all in results directory',
            response=response
        ))
        self.assertEqual(1, remove.call_count)

    @patch('cauldron.environ.systems.remove')
    def test_purge_all_fails(self, remove: MagicMock):
        """Should fail to purge current results directory."""
        remove.return_value = False
        response = support.run_command('purge --yes --all')
        self.assertFalse(response.success, Message(
            'PURGED ALL',
            'should not have purged all in results directory',
            response=response
        ))
        self.assertEqual(1, remove.call_count)

    @patch('cauldron.cli.commands.purge.opener.initialize_results')
    @patch('cauldron.project.get_internal_project')
    @patch('cauldron.environ.systems.remove')
    def test_purge_project(
            self,
            remove: MagicMock,
            get_internal_project: MagicMock,
            initialize_results: MagicMock,
    ):
        """Should purge local project results directory."""
        project = _create_mock_project()
        get_internal_project.return_value = project

        r = support.run_command('purge --yes')
        self.assertTrue(r.success, Message(
            'FAILED TO PURGE',
            'Expected the project purge to have succeed.',
            response=r
        ))
        self.assertEqual(1, remove.call_count)
        self.assertEqual(1, initialize_results.call_count)

    @patch('cauldron.project.get_internal_project')
    @patch('cauldron.environ.systems.remove')
    def test_failed_project_purge(
            self,
            remove: MagicMock,
            get_internal_project: MagicMock,
    ):
        """Should fail if unable to remove."""
        project = MagicMock()
        project.steps = [MagicMock()]
        get_internal_project.return_value = project
        remove.return_value = False

        r = support.run_command('purge --yes')
        self.assertTrue(r.failed)
        self.assertEqual(r.errors[0].code, 'UNABLE_TO_REMOVE')

    @patch('cauldron.project.get_internal_project')
    def test_no_project(self, get_internal_project: MagicMock):
        """Should fail if not --all and no open project."""
        get_internal_project.return_value = None
        r = support.run_command('purge --yes')
        self.assertFalse(r.success, Message(
            'UNEXPECTED PURGE',
            'Expected the purge process to fail when there is no project.',
            response=r
        ))
        self.assertEqual(r.errors[0].code, 'NO_OPEN_PROJECT')

    @patch('cauldron.cli.interaction.query.confirm')
    def test_abort(self, confirm: MagicMock):
        """Should fail if unable to remove."""
        confirm.return_value = False

        r = support.run_command('purge')
        self.assertFalse(r.failed)
        self.assertEqual(r.messages[0].code, 'NO_PURGE')

    @patch('cauldron.cli.commands.purge.opener.initialize_results')
    @patch('cauldron.project.get_internal_project')
    @patch('cauldron.environ.systems.remove')
    def test_purge_remote(
            self,
            remove: MagicMock,
            get_internal_project: MagicMock,
            initialize_results: MagicMock,
    ):
        """Should purge current results directory."""
        project = _create_mock_project()
        get_internal_project.return_value = project

        r = support.run_remote_command('purge --yes')
        self.assertTrue(r.success, Message(
            'FAILED TO REMOTE PURGE',
            'Expected the remote purge to have succeed.',
            response=r
        ))
        self.assertEqual(1, remove.call_count)
        self.assertEqual(1, initialize_results.call_count)
