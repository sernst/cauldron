import tempfile

import pytest

import cauldron
from cauldron import cli
from cauldron import environ
from cauldron.cli import commander
from cauldron.cli.commands import close


class ProjectLifecycleTester:

    def __init__(self):
        self.results_directory = None
        self.temp_directories = dict()

    def set_up(self):
        """Called before the test process begins."""
        results_directory = tempfile.mkdtemp(
            prefix='cd-test-results-{}--'.format(self.__class__.__name__)
        )
        self.results_directory = results_directory
        environ.configs.put(results_directory=results_directory, persists=False)
        self.temp_directories = dict()

    def tear_down(self):
        """Called after the test process is complete."""
        # Close any open project so that it doesn't persist to the next test
        if cauldron.project.internal_project is not None:
            close.execute(cli.make_command_context('close'))

        environ.configs.remove('results_directory', include_persists=False)

        environ.systems.remove(self.results_directory)
        self.results_directory = None

        for key, path in self.temp_directories.items():  # pragma: no cover
            environ.systems.remove(path)

        if cauldron.environ.remote_connection.active:  # pragma: no cover
            commander.execute('disconnect', '')


def make_project_lifecycle_fixture(fixture_name: str = 'tester'):
    """..."""
    @pytest.fixture(name=fixture_name)
    def project_lifecycle_fixture():
        tester = ProjectLifecycleTester()
        tester.set_up()
        yield tester
        tester.tear_down()

    return project_lifecycle_fixture
