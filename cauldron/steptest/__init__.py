import inspect
import os
import tempfile
import unittest

from cauldron import environ
from cauldron import runner
from cauldron.cli import commander
from cauldron.session import exposed  # noqa
from cauldron.steptest import support
from cauldron.steptest.functional import CauldronTest
from cauldron.steptest.functional import create_test_fixture
from cauldron.steptest.results import StepTestRunResult
from cauldron.steptest.support import find_project_directory


class StepTestCase(unittest.TestCase):
    """
    The base class to use for step "unit" testing. This class overrides
    the default setup and tearDown methods from the unittest.TestCase to add
    functionality for loading and unloading the Cauldron notebook settings
    needed to run and test steps. If you override either of these methods
    make sure that you call their super methods as well or the functionality
    will be lost.
    """

    def __init__(self, *args, **kwargs):
        """
        Initializes a StepTestCase with default attribute values that will be
        populated during the setup and teardown phases of each test.
        """
        super(StepTestCase, self).__init__(*args, **kwargs)
        self.results_directory = None
        self.temp_directories = dict()

    def setUp(self):
        """
        A modified setup function that handles opening the project for testing.
        If you override the setUp function in your tests, be sure to call the
        super function so that this initialization happens properly
        """
        environ.modes.add(environ.modes.TESTING)
        super(StepTestCase, self).setUp()
        results_directory = tempfile.mkdtemp(
            prefix='cd-step-test-results-{}--'.format(self.__class__.__name__)
        )
        self.results_directory = results_directory
        environ.configs.put(results_directory=results_directory, persists=False)
        self.temp_directories = dict()
        self.open_project()

        # Load libraries before calling test functions so that patching works
        # correctly.
        runner.reload_libraries()

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
        filename = inspect.getfile(self.__class__)
        project_directory = support.find_project_directory(filename)
        return os.path.join(project_directory, *args)

    def open_project(self) -> 'exposed.ExposedProject':
        """
        Opens the project associated with this test and returns the public
        (exposed) project after it has been loaded. If the project cannot be
        opened the test will fail.
        """
        try:
            project_path = self.make_project_path()
            return support.open_project(project_path)
        except RuntimeError as error:
            self.fail('{}'.format(error))

    def run_step(
            self,
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
        try:
            return support.run_step(step_name, allow_failure)
        except AssertionError as error:
            self.fail('{}'.format(error))

    def tearDown(self):
        """
        After a test is run this function is used to undo any side effects that
        were created by setting up and running the test. This includes removing
        the temporary directories that were created to store test information
        during test execution.
        """
        super(StepTestCase, self).tearDown()

        # Close any open project so that it doesn't persist to the next test
        closed = commander.execute('close', '')
        closed.thread.join()

        environ.configs.remove('results_directory', include_persists=False)

        environ.systems.remove(self.results_directory)
        self.results_directory = None

        for key, path in self.temp_directories.items():
            environ.systems.remove(path)

        environ.modes.remove(environ.modes.TESTING)

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
