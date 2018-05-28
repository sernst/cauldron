import inspect
import os
import sys
import tempfile

from cauldron import environ
from cauldron import runner
from cauldron.cli import commander
from cauldron.session import exposed
from cauldron.steptest import support
from cauldron.steptest.results import StepTestRunResult


class CauldronTest:
    """..."""

    def __init__(self, *args, **kwargs):
        """..."""
        self._call_args = args
        self._call_kwargs = kwargs
        self._test_function = None
        self.results_directory = None
        self.temp_directories = dict()

    def __call__(self, test_function):
        """..."""
        self._test_function = test_function

        def cauldron_test_wrapper(*args, **kwargs):
            return self.run_test(*args, **kwargs)

        project_path = self.make_project_path('cauldron.json')
        self._library_paths = support.get_library_paths(project_path)
        sys.path.extend(self._library_paths)

        # Load libraries before calling test functions so that patching works
        # correctly, but do this during the decoration process so subsequent
        # patching isn't reverted.
        runner.reload_libraries(self._library_paths)

        cauldron_test_wrapper.__name__ = test_function.__name__
        return cauldron_test_wrapper

    def setup(self):
        """..."""
        environ.modes.add(environ.modes.TESTING)
        results_directory = tempfile.mkdtemp(
            prefix='cd-step-test-results-{}--'.format(self.__class__.__name__)
        )
        self.results_directory = results_directory
        environ.configs.put(results_directory=results_directory, persists=False)
        self.temp_directories = dict()
        self.open_project()

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
        filename = inspect.getfile(self._test_function)
        project_directory = support.find_project_directory(filename)
        return os.path.join(project_directory, *args)

    def open_project(self) -> 'exposed.ExposedProject':
        """
        Returns the Response object populated by the open project command
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
        :param identifier:
        :param args:
        :return:
        """
        return support.make_temp_path(self.temp_directories, identifier, *args)

    def run_test(self, *args, **kwargs):
        """..."""
        self.setup()
        result = self._test_function(self, *args, **kwargs)
        self.tear_down()
        return result

    def tear_down(self):
        """..."""

        # Close any open project so that it doesn't persist to the next test
        closed = commander.execute('close', '')
        closed.thread.join()

        environ.configs.remove('results_directory', include_persists=False)

        environ.systems.remove(self.results_directory)
        self.results_directory = None

        for key, path in self.temp_directories.items():
            environ.systems.remove(path)

        paths_to_remove = [p for p in self._library_paths if p in sys.path]
        for path in paths_to_remove:
            sys.path.remove(path)

        environ.modes.remove(environ.modes.TESTING)
