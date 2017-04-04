from unittest.mock import patch

from cauldron import environ
from cauldron.cli.commands.open import opener
from cauldron.environ import Response
from cauldron.test import support
from cauldron.test.support import scaffolds

INVALID_PATH = environ.paths.clean('~/invalid-path/that/does/not/exist/')


def opener_package(*args) -> str:
    root = ['cauldron', 'cli', 'commands', 'open', 'opener']
    return '.'.join(root + list(args))


class TestOpenOpener(scaffolds.ResultsTest):
    """ """

    def test_not_exists(self):
        """ should return False when the project does not exist """

        self.assertFalse(opener.project_exists(Response(), INVALID_PATH))

    def test_not_exists_load(self):
        """ should return False when the project does not exist """

        self.assertFalse(opener.load_project(Response(), INVALID_PATH))

    def test_not_exists_open(self):
        """ should fail when the project does not exist """

        response = opener.open_project(INVALID_PATH, forget=True)
        self.assertTrue(response.failed)

    @patch(opener_package('project_exists'), return_value=True)
    def test_not_loadable_open(self, project_exists):
        """ should fail when project does not load """

        response = opener.open_project(INVALID_PATH, forget=True)
        self.assertTrue(response.failed)

    @patch(opener_package('project_exists'), return_value=True)
    @patch(opener_package('load_project'), return_value=True)
    @patch(opener_package('update_recent_paths'), return_value=False)
    def test_not_update(self, *args):
        """ should fail when project does not load """

        response = opener.open_project(INVALID_PATH, forget=False)
        self.assertTrue(response.failed)

    @patch(opener_package('initialize_results'), return_value=False)
    def test_bad_initialize_results(self, *args):
        """ should fail opening when initialization fails """

        response = support.create_project(self, 'minnesota', confirm=False)
        self.assertTrue(response.failed)
        support.run_command('close')

    @patch(opener_package('write_results'), return_value=False)
    def test_bad_write_results(self, *args):
        """ should fail opening when writing initial results fails """

        response = support.create_project(self, 'iowa', confirm=False)
        self.assertTrue(response.failed)
        support.run_command('close')

    @patch('cauldron.runner.initialize')
    def test_load_project_bad(self, runner_initialize):
        runner_initialize.side_effect = FileNotFoundError()

        response = Response()
        self.assertFalse(opener.load_project(response, INVALID_PATH))
        self.assertTrue(response.errors[0].code == 'PROJECT_NOT_FOUND')

    @patch('cauldron.runner.initialize')
    def test_load_project_bad_2(self, runner_initialize):
        runner_initialize.side_effect = ValueError()

        response = Response()
        self.assertFalse(opener.load_project(response, INVALID_PATH))
        self.assertTrue(response.errors[0].code == 'PROJECT_INIT_FAILURE')
