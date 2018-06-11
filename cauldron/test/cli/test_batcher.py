import os
import typing
from unittest.mock import patch
from unittest.mock import MagicMock

import cauldron
from cauldron.environ.response import Response
from cauldron.test.support import scaffolds
from cauldron.test.support.messages import Message

RunResult = typing.NamedTuple('RunResult', [
    ('response', Response),
    ('directory', str),
    ('logging_path', str),
    ('results_directory', str),
    ('reader_path', str)
])


def run_project(
        project_directory: str,
        save_directory: str
) -> RunResult:
    """
    Runs the specified project by setting up temporary directories to store

    :param project_directory: 
        Directory where the project to run is located
    :param save_directory:
        A temporary directory where the output is saved for test assertions.
        This directory should be removed at the end of the test.
    :return:
        The response returned by executing the run project
    """

    results_directory = os.path.join(save_directory, 'output')
    reader_path = os.path.join(save_directory, 'reader.cauldron')
    logging_path = os.path.join(save_directory, 'test.log')

    response = cauldron.run_project(
        project_directory=project_directory,
        output_directory=results_directory,
        logging_path=logging_path,
        reader_path=reader_path
    )

    return RunResult(
        response=response,
        directory=save_directory,
        results_directory=results_directory,
        logging_path=logging_path,
        reader_path=reader_path
    )


class TestBatcher(scaffolds.ResultsTest):
    """Test suite for the batcher module"""

    def run_project(self, project_id: str, project_directory: str):
        directory = self.get_temp_path(project_id)
        result = run_project(project_directory, directory)
 
        self.assertFalse(result.response.failed, Message(
            'Failed to run project',
            response=result.response
        ))
        self.assertTrue(os.path.exists(result.results_directory))
        self.assertTrue(os.path.exists(os.path.join(
            result.results_directory,
            'display.html'
        )))
        self.assertTrue(os.path.exists(result.logging_path))
        self.assertTrue(os.path.getsize(result.logging_path) > 0)
        self.assertTrue(os.path.exists(result.reader_path))

    def test_run_project(self):
        self.run_project('hello-cauldron', '@examples:hello_cauldron')

    def test_run_pyplot_project(self):
        self.run_project('hello-cauldron', '@examples:pyplot')

    def test_run_open_fail(self):
        """Should fail to open a project"""
        directory = self.get_temp_path('open-fail')
        result = run_project('fake-project-does-not-exist', directory)
        self.assertFalse(result.response.success)

    @patch('cauldron.cli.commands.run.execute')
    def test_run_fail(self, run_execute: MagicMock):
        """Should fail to run a project"""

        run_execute.return_value = Response().fail().response
        directory = self.get_temp_path('run-fail')
        result = run_project('@examples:hello_cauldron', directory)
        self.assertFalse(result.response.success)
