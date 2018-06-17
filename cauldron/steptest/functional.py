import os
import sys
import tempfile

from cauldron import environ
from cauldron import runner
from cauldron.cli import commander
from cauldron.session import exposed  # noqa
from cauldron.steptest import support
from cauldron.steptest.results import StepTestRunResult

try:
    import pytest
except ImportError:  # pragma: no cover
    pytest = None

# @pytest.fixture(name='tester')
# def tester_fixture() -> CauldronTest:
#     """Create the Cauldron project test environment"""
#     tester = CauldronTest(project_path=os.path.dirname(__file__))
#     tester.setup()
#     yield tester
#     tester.tear_down()


def create_test_fixture(test_file_path: str, fixture_name: str = 'tester'):
    """..."""
    path = os.path.realpath(
        os.path.dirname(test_file_path)
        if os.path.isfile(test_file_path) else
        test_file_path
    )

    @pytest.fixture(name=fixture_name)
    def tester_fixture() -> CauldronTest:
        tester = CauldronTest(project_path=path)
        tester.setup()
        yield tester
        tester.tear_down()

    return tester_fixture


class CauldronTest:
    """
    A Dependency injection class for use with the Pytest or similar testing
    framework.
    """

    def __init__(self, project_path: str, *args, **kwargs):
        """
        Initializes the decorator with default values that will be populated
        during the lifecycle of the decorator and test.
        """
        self.project_path = os.path.realpath(project_path)
        self._call_args = args
        self._call_kwargs = kwargs
        self._test_function = None
        self.results_directory = None
        self.temp_directories = dict()
        self._library_paths = []

    def setup(self) -> 'CauldronTest':
        """
        Handles initializing the environment and opening the project for
        testing.
        """
        environ.modes.add(environ.modes.TESTING)

        project_path = self.make_project_path('cauldron.json')
        self._library_paths = [
            path
            for path in support.get_library_paths(project_path)
            if path not in sys.path
        ]
        sys.path.extend(self._library_paths)

        # Load libraries before calling test functions so that patching works
        # correctly, but do this during the decoration process so subsequent
        # patching isn't reverted.
        runner.reload_libraries(self._library_paths)

        results_directory = tempfile.mkdtemp(
            prefix='cd-step-test-results-{}--'.format(self.__class__.__name__)
        )
        self.results_directory = results_directory
        environ.configs.put(results_directory=results_directory, persists=False)
        self.temp_directories = dict()
        self.open_project()

        return self

    def make_project_path(self, *args) -> str:
        """
        Returns an absolute path to the specified location within the Cauldron
        project directory where this test file is located.

        :param args:
            Relative path components within the Cauldron project directory
        :return:
            The absolute path to the location within the project. If no path
            components are specified, the location returned will be the
            project directory itself.
        """
        project_directory = support.find_project_directory(self.project_path)
        return os.path.join(project_directory, *args)

    def open_project(self) -> 'exposed.ExposedProject':
        """
        Opens the project associated with this test and returns the public
        (exposed) project after it has been loaded. If the project cannot be
        opened the test will fail with an AssertionError.
        """
        try:
            project_path = self.make_project_path()
            return support.open_project(project_path)
        except RuntimeError as error:
            raise AssertionError('{}'.format(error))

    @classmethod
    def run_step(
            cls,
            step_name: str,
            allow_failure: bool = False
    ) -> StepTestRunResult:
        """
        Runs the specified step by name its complete filename including extension

        :param step_name:
            The full filename of the step to be run including its extension.
        :param allow_failure:
            Whether or not to allow a failed result to be returned. If False,
            a failed attempt to run a step will cause the current test to
            fail immediately before returning a value from this function call.
            Override this with a True value to have the step failure data
            passed back for inspection.
        :return:
            A StepTestRunResult instance containing information about the
            execution of the step.
        """
        return support.run_step(step_name, allow_failure)

    def make_temp_path(self, identifier, *args) -> str:
        """
        Creates a temporary path within a named directory created
        for the test being executed. If any directories in the path don't exist
        already, they will be created before returning the path.

        :param identifier:
            The identifier for the test the is used to name the folder in which
            the temp path will reside within the root test folder for the given
            test.
        :param args:
            Any additional path elements to identify the path that will
            appear beneath the identifier folder.
        """
        return support.make_temp_path(self.temp_directories, identifier, *args)

    def tear_down(self):
        """
        After a test is run this function is used to undo any side effects that
        were created by setting up and running the test. This includes removing
        the temporary directories that were created to store test information
        during test execution.
        """
        # Close any open project so that it doesn't persist to the next test
        closed = commander.execute('close', '')
        closed.thread.join()

        environ.configs.remove('results_directory', include_persists=False)

        environ.systems.remove(self.results_directory)
        self.results_directory = None

        for path in self.temp_directories.values():
            environ.systems.remove(path)

        paths_to_remove = [p for p in self._library_paths if p in sys.path]
        for path in paths_to_remove:
            sys.path.remove(path)

        environ.modes.remove(environ.modes.TESTING)
