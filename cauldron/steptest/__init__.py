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

    print('Subdirectory:', subdirectory)
    if os.path.exists(os.path.join(subdirectory, 'cauldron.json')):
        return subdirectory

    parent = os.path.dirname(subdirectory)
    if parent == subdirectory:
        return None

    if os.path.exists(os.path.join(parent, 'cauldron.json')):
        return parent
    return find_project_directory(parent)


class StepTestRunResult:

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
        return self._locals

    @property
    def success(self):
        return not self._response.failed


class StepTestCase(unittest.TestCase):

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

        return cd.project

    def run_step(self, step_name: str) -> StepTestRunResult:
        """ Runs the specified step by name """

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

        if response.failed:
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

    def make_temp_path(self, identifier, *args):
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
