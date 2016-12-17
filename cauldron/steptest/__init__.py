import os
import tempfile
import unittest
import typing
import inspect

from cauldron import environ
from cauldron.cli import commander


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

    def open_project(self) -> 'environ.Response':
        """
        Returns the Response object populated by the open project command
        """

        res = environ.Response()
        commander.execute(
            'open', '{} --forget'.format(self.make_project_path()),
            res
        )
        res.thread.join()
        return res

    def run_step(self, step_name: str):
        """ Runs the specified step by name """

        response = commander.execute('run', '{} --force'.format(step_name))
        response.thread.join()

        if response.failed:
            self.fail('Failed to run step "{}"'.format(step_name))
        else:
            return response

    def tearDown(self):
        super(StepTestCase, self).tearDown()

        # Close any open project so that it doesn't persist to the next test
        commander.execute('close', '')

        environ.configs.remove('results_directory', include_persists=False)

        environ.systems.remove(self.results_directory)
        self.results_directory = None

        for key, path in self.temp_directories.items():
            environ.systems.remove(path)

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
