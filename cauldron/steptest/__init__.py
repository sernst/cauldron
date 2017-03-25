import os
import tempfile
import unittest
import typing
import inspect

import cauldron as cd
from cauldron import environ
from cauldron.session import projects
from cauldron.session import exposed
from cauldron.cli import commander
from cauldron.session.caching import SharedCache


def find_project_directory(subdirectory: str) -> typing.Union[str, None]:
    """
    Finds the root project directory from a subdirectory within the project
    folder.

    :param subdirectory:
        The subdirectory to use to search for the project directory. The
        subdirectory may also be the project directory.
    :return:
        The project directory that contains the specified subdirectory or None
        if no project directory was found.
    """

    if os.path.exists(os.path.join(subdirectory, 'cauldron.json')):
        return subdirectory

    parent = os.path.dirname(subdirectory)
    if parent == subdirectory:
        return None

    if os.path.exists(os.path.join(parent, 'cauldron.json')):
        return parent
    return find_project_directory(parent)


class StepTestRunResult:
    """
    This class contains information returned from running a step during testing.
    """

    def __init__(
            self,
            step: 'projects.ProjectStep',
            response: 'environ.Response'
    ):
        self._step = step  # type: projects.ProjectStep
        self._response = response  # type: environ.Response
        self._locals = SharedCache().put(**step.test_locals)

    @property
    def local(self) -> SharedCache:
        """
        Container object that holds all of the local variables that were
        defined within the run step
        """

        return self._locals

    @property
    def success(self) -> bool:
        """
        Whether or not the step was successfully run. This value will be
        False if there as an uncaught exception during the execution of the
        step.
        """

        return not self._response.failed

    def echo_error(self) -> str:
        """
        Creates a string representation of the exception that cause the step
        to fail if an exception occurred. Otherwise, an empty string is returned.

        :return:
            The string representation of the exception that caused the running
            step to fail or a blank string if no exception occurred
        """

        if not self._response.errors:
            return ''

        return '{}'.format(self._response.errors[0].serialize())


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
        project_directory = find_project_directory(filename)

        if project_directory is None:
            raise FileNotFoundError(' '.join([
                'StepTest does not appear to be located within',
                'a Cauldron project directory'
            ]))

        return os.path.join(project_directory, *args)

    def open_project(self) -> 'exposed.ExposedProject':
        """
        Returns the Response object populated by the open project command
        """

        project_path = self.make_project_path()
        res = environ.Response()
        commander.execute(
            'open', '{} --forget'.format(project_path),
            res
        )
        res.thread.join()

        if res.failed:
            self.fail(
                'Unable to open project at path "{}"'
                .format(project_path)
            )

        os.chdir(cd.project.internal_project.source_directory)

        return cd.project

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

        project = cd.project.internal_project
        if not project:
            self.fail(
                'No project was open. Unable to run step "{}"'
                .format(step_name)
            )

        step = project.get_step(step_name)
        if not step:
            self.fail('No step named "{}" was found'.format(step_name))

        response = commander.execute('run', '"{}" --force'.format(step_name))
        response.thread.join()

        if not allow_failure and response.failed:
            self.fail('Failed to run step "{}"'.format(step_name))

        return StepTestRunResult(step, response)

    def tearDown(self):
        super(StepTestCase, self).tearDown()

        # Close any open project so that it doesn't persist to the next test
        commander.execute('close', '')

        environ.configs.remove('results_directory', include_persists=False)

        environ.systems.remove(self.results_directory)
        self.results_directory = None

        for key, path in self.temp_directories.items():
            environ.systems.remove(path)

        environ.modes.remove(environ.modes.TESTING)

    def make_temp_path(self, identifier, *args) -> str:
        """

        :param identifier:
        :param args:
        :return:
        """

        if identifier not in self.temp_directories:
            self.temp_directories[identifier] = tempfile.mkdtemp(
                prefix='cd-step-test-{}'.format(identifier)
            )

        return os.path.realpath(
            os.path.join(self.temp_directories[identifier], *args)
        )
