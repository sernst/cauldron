from unittest.mock import MagicMock
from unittest.mock import patch

from cauldron import environ
from cauldron.test import support
from cauldron.ui.routes.apis.executions import runner


@patch('cauldron.ui.routes.apis.executions.runner.parse_command_args')
def test_execute_parse_failure(parse_command_args: MagicMock):
    """Should fail execution if unable to parse command arguments."""
    parse_command_args.return_value = environ.Response().fail().response
    response = runner.execute()
    assert response.failed


@patch('cauldron.ui.routes.apis.executions.runner.ui_configs')
@patch('cauldron.ui.routes.apis.executions.runner.commander.execute')
def test_execute_still_running(
        commander_execute: MagicMock,
        ui_configs: MagicMock,
):
    """Should succeed with a still running state."""
    ui_configs.ACTIVE_EXECUTION_RESPONSE = None

    thread = MagicMock()
    thread.is_alive.return_value = True
    response = environ.Response()
    response.thread = thread
    commander_execute.return_value = response

    response = runner.execute(asynchronous=True)

    assert response.success, 'Expect execution to succeed.'
    assert response.data['run_status'] == 'running', """
        Expect the command to still be running after starting
        it and waiting a brief period.
        """
    assert ui_configs.ACTIVE_EXECUTION_RESPONSE is not None, """
        Expect the still-running response to be stored in the
        configs for future access.
        """
    assert 5 == thread.join.call_count, """
        Expect five join attempts to see if the thread has
        completed before returning a running state response.
        """


@patch('cauldron.ui.routes.apis.executions.runner.ui_configs')
@patch('cauldron.ui.routes.apis.executions.runner.commander.execute')
def test_execute_synchronous(
        commander_execute: MagicMock,
        ui_configs: MagicMock,
):
    """Should succeed after waiting for the execution to complete."""
    ui_configs.ACTIVE_EXECUTION_RESPONSE = None

    thread = MagicMock()
    thread.is_alive.return_value = False
    response = environ.Response()
    response.thread = thread
    commander_execute.return_value = response

    response = runner.execute(asynchronous=False)

    assert response.success, 'Expect execution to succeed.'
    assert response.data['run_status'] == 'complete', """
        Expect the command to be completed before returning.
        """
    assert ui_configs.ACTIVE_EXECUTION_RESPONSE is None, """
        Expect the command to be done and not stored long-term
        in the configs.
        """
    assert 2 == thread.join.call_count, """
        Expect a single join call that waits until the command
        has completed before continuing, followed by one more
        call that confirms that the thread is not still alive.
        """


@patch('cauldron.ui.routes.apis.executions.runner.commander.execute')
def test_execute_error(commander_execute: MagicMock):
    """Should fail after command execution throws an error."""
    commander_execute.side_effect = ValueError
    response = runner.execute(asynchronous=False)
    assert support.has_error_code(response, 'KERNEL_EXECUTION_FAILURE')
