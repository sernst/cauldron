from unittest.mock import patch
from unittest.mock import MagicMock

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

    @patch('time.sleep')
    def test_not_exists(self,  *args):
        """ should return False when the project does not exist """
        self.assertFalse(opener.project_exists(Response(), INVALID_PATH))

    @patch('time.sleep')
    def test_not_exists_load(self, *args):
        """ should return False when the project does not exist """
        self.assertFalse(opener.load_project(Response(), INVALID_PATH))

    @patch('time.sleep')
    def test_not_exists_open(self, *args):
        """ should fail when the project does not exist """
        response = opener.open_project(INVALID_PATH, forget=True)
        self.assertTrue(response.failed)

    @patch('time.sleep')
    @patch(opener_package('project_exists'), return_value=True)
    def test_not_loadable_open(self, *args):
        """ should fail when project does not load """
        response = opener.open_project(INVALID_PATH, forget=True)
        self.assertTrue(response.failed)

    @patch('time.sleep')
    @patch(opener_package('project_exists'), return_value=True)
    @patch(opener_package('load_project'), return_value=True)
    @patch(opener_package('update_recent_paths'), return_value=False)
    def test_not_update(self, *args):
        """ should fail when project does not load """
        response = opener.open_project(INVALID_PATH, forget=False)
        self.assertTrue(response.failed)

    @patch('time.sleep')
    @patch(opener_package('initialize_results'), return_value=False)
    def test_bad_initialize_results(self, *args):
        """ should fail opening when initialization fails """
        response = support.create_project(self, 'minnesota', confirm=False)
        self.assertTrue(response.failed)

    @patch('time.sleep')
    @patch(opener_package('write_results'), return_value=False)
    def test_bad_write_results(self, *args):
        """ should fail opening when writing initial results fails """
        response = support.create_project(self, 'iowa', confirm=False)
        self.assertTrue(response.failed)

    @patch('time.sleep')
    @patch('cauldron.runner.initialize')
    def test_load_project_bad(self, runner_initialize, *args):
        runner_initialize.side_effect = FileNotFoundError()

        response = Response()
        self.assertFalse(opener.load_project(response, INVALID_PATH))
        self.assertTrue(response.errors[0].code == 'PROJECT_NOT_FOUND')

    @patch('time.sleep')
    @patch('cauldron.runner.initialize')
    def test_load_project_bad_2(self, runner_initialize, *args):
        runner_initialize.side_effect = ValueError()
        response = Response()
        self.assertFalse(opener.load_project(response, INVALID_PATH))
        self.assertTrue(response.errors[0].code == 'PROJECT_INIT_FAILURE')

    @patch('time.sleep')
    @patch('cauldron.session.initialize_results_path')
    def test_initialize_results_abort(
            self,
            initialize_results_path: MagicMock,
            *args
    ):
        """Should abort initializing project has no results path"""
        response = Response()
        project = MagicMock()
        project.results_path = None
        result = opener.initialize_results(response, project)
        self.assertTrue(result)
        self.assertEqual(0, initialize_results_path.call_count)

    @patch('time.sleep')
    @patch('cauldron.session.initialize_results_path')
    def test_initialize_results(
            self,
            initialize_results_path: MagicMock,
            *args
    ):
        """Should initialize paths for project"""
        response = Response()
        project = MagicMock()
        result = opener.initialize_results(response, project)
        self.assertTrue(result)
        self.assertEqual(1, initialize_results_path.call_count)

    @patch('time.sleep')
    @patch('cauldron.session.initialize_results_path')
    def test_initialize_results_error(
            self,
            initialize_results_path: MagicMock,
            *args
    ):
        """Should fail to initialize paths for project"""
        initialize_results_path.side_effect = ValueError('FAKE')
        response = Response()
        project = MagicMock()
        result = opener.initialize_results(response, project)
        self.assertFalse(result)
        self.assertTrue(response.failed)
        self.assertEqual(1, initialize_results_path.call_count)
