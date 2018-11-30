import os
import typing
from unittest.mock import patch
from unittest.mock import MagicMock

import cauldron
from cauldron.cli import batcher
from cauldron.environ.response import Response
from cauldron.session.definitions import ExecutionResult
from cauldron.test.support import scaffolds
from cauldron.test.support.messages import Message

RunResult = typing.NamedTuple('RunResult', [
    ('result', ExecutionResult),
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

    execution_result = cauldron.run_project(
        project_directory=project_directory,
        output_directory=results_directory,
        logging_path=logging_path,
        reader_path=reader_path
    )

    return RunResult(
        result=execution_result,
        directory=save_directory,
        results_directory=results_directory,
        logging_path=logging_path,
        reader_path=reader_path
    )


class TestBatcher(scaffolds.ResultsTest):
    """Test suite for the batcher module"""

    def run_project(self, project_id: str, project_directory: str):
        directory = self.get_temp_path(project_id)
        run_result = run_project(project_directory, directory)

        self.assertIsNotNone(run_result.result.shared)
        self.assertFalse(run_result.result.failed, Message(
            'Failed to run project',
            response=run_result.result.response
        ))
        self.assertTrue(run_result.result.success, Message(
            'Failed to run project',
            response=run_result.result.response
        ))
        self.assertTrue(os.path.exists(run_result.results_directory))
        self.assertTrue(os.path.exists(os.path.join(
            run_result.results_directory,
            'display.html'
        )))
        self.assertTrue(os.path.exists(run_result.logging_path))
        self.assertTrue(os.path.getsize(run_result.logging_path) > 0)
        self.assertTrue(os.path.exists(run_result.reader_path))

    def test_run_project(self):
        self.run_project('hello-cauldron', '@examples:hello_cauldron')

    def test_run_pyplot_project(self):
        self.run_project('hello-cauldron', '@examples:pyplot')

    def test_run_open_fail(self):
        """Should fail to open a project"""
        directory = self.get_temp_path('open-fail')
        run_result = run_project('fake-project-does-not-exist', directory)
        self.assertFalse(run_result.result.success)

    @patch('cauldron.cli.commands.run.execute')
    def test_run_fail(self, run_execute: MagicMock):
        """Should fail to run a project"""

        run_execute.return_value = Response().fail().response
        directory = self.get_temp_path('run-fail')
        run_result = run_project('@examples:hello_cauldron', directory)
        self.assertFalse(run_result.result.success)

    @patch('cauldron.project.get_internal_project')
    @patch('cauldron.cli.batcher.open_command.execute')
    @patch('cauldron.cli.batcher.run_command.execute')
    @patch('cauldron.cli.batcher.save_command.execute')
    @patch('cauldron.cli.batcher.close_command.execute')
    def test_close_fail(
            self,
            execute_close: MagicMock,
            execute_save: MagicMock,
            execute_run: MagicMock,
            execute_open: MagicMock,
            *args
    ):
        """Should fail to close project."""
        successful = MagicMock()
        successful.failed = False
        execute_open.return_value = successful
        execute_run.return_value = successful
        execute_save.return_value = successful

        failure = MagicMock()
        failure.failed = True
        execute_close.return_value = failure

        directory = self.get_temp_path('run-close-fail')
        run_result = run_project('@examples:hello_cauldron', directory)
        self.assertTrue(run_result.result.failed)

    @patch('os.path.isdir')
    @patch('os.path.exists')
    @patch('os.remove')
    @patch('os.makedirs')
    def test_initialize_logging_path_none(
            self,
            make_dirs: MagicMock,
            remove: MagicMock,
            exists: MagicMock,
            is_dir: MagicMock
    ):
        """Should initialize log path from None."""
        exists.side_effect = (True, False)
        is_dir.return_value = True

        path = batcher.initialize_logging_path(None)
        self.assertEqual(1, make_dirs.call_count)
        self.assertEqual(0, remove.call_count)
        self.assertTrue(path.endswith('cauldron_run.log'))

    @patch('os.path.isdir')
    @patch('os.path.exists')
    @patch('os.remove')
    @patch('os.makedirs')
    def test_initialize_logging_path_file(
            self,
            make_dirs: MagicMock,
            remove: MagicMock,
            exists: MagicMock,
            is_dir: MagicMock
    ):
        """Should initialize log path from a file path."""
        exists.side_effect = (True, False)
        is_dir.return_value = False

        directory = os.path.dirname(__file__)
        source = os.path.join(directory, 'test_log_path.log')
        path = batcher.initialize_logging_path(source)
        self.assertEqual(1, make_dirs.call_count)
        self.assertEqual(1, remove.call_count)
        self.assertFalse(path.endswith('cauldron_run.log'))
