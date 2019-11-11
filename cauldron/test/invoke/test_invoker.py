from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
from cauldron.invoke import invoker
from cauldron.invoke import parser


def run_command(command: str) -> int:
    """Executes the specified command by parsing the args and running them"""
    args = parser.parse(command.split(' '))
    return invoker.run(args.get('command'), args)


def test_run_version():
    """Should run the version command without error."""
    assert 0 == run_command('version')


@patch('cauldron.cli.server.run.execute')
def test_run_kernel(server_execute: MagicMock):
    """Should start the kernel."""
    assert 0 == run_command('kernel')
    assert 1 == server_execute.call_count


@patch('cauldron.cli.shell.CauldronShell.cmdloop')
def test_run_shell(cmdloop: MagicMock):
    """Should run the shell command loop."""
    assert 0 == run_command('shell')
    assert 1 == cmdloop.call_count


@patch('cauldron.invoke.invoker.in_project_directory')
@patch('cauldron.cli.shell.CauldronShell.cmdloop')
def test_run_shell_with_open(
        cmdloop: MagicMock,
        in_project_directory: MagicMock
):
    """Should run shell command loop with an open project command."""
    in_project_directory.return_value = True

    assert 0 == run_command('shell')
    assert 1 == cmdloop.call_count


@patch('cauldron.cli.shell.CauldronShell.cmdloop')
@patch('cauldron.invoke.invoker.run_batch')
def test_run_shell_batch(run_batch: MagicMock, cmdloop: MagicMock):
    """Should run batch from shell command."""
    run_batch.return_value = 42

    assert 42 == run_command('shell --project=fake')
    assert 1 == run_batch.call_count
    assert 0 == cmdloop.call_count


@patch('cauldron.cli.batcher.run_project')
def test_run_batch(run_project: MagicMock):
    """Should run batch project."""
    assert 0 == invoker.run_batch({})
    assert 1 == run_project.call_count


def test_load_shared_data_none():
    """Should return empty dictionary when value is None."""
    assert isinstance(invoker.load_shared_data(None), dict)


def test_load_shared_data_missing():
    """Should raise an exception if file not found."""
    with pytest.raises(FileNotFoundError):
        invoker.load_shared_data('nosuchfileorpath')


@patch('os.path.exists')
def test_load_shared_data_open_error(exists: MagicMock):
    """Should raise error if unable to read file."""
    exists.return_value = True

    with pytest.raises(IOError):
        invoker.load_shared_data('fakepaththatexists')


@patch('json.load')
def test_load_shared_data_data_error(json_load: MagicMock):
    """Should raise error if JSON isn't a dictionary."""
    json_load.return_value = []

    with pytest.raises(ValueError):
        invoker.load_shared_data(__file__)


@patch('json.load')
def test_load_shared_data(json_load: MagicMock):
    """Should raise error if JSON isn't a dictionary"""
    json_load.return_value = {}

    result = invoker.load_shared_data(__file__)
    assert isinstance(result, dict)


def test_no_such_command():
    """Should return error code if the command is not recognized"""
    assert 1 == invoker.run('fake', {'parser': MagicMock()})


@patch('cauldron.invoke.invoker.ui.start')
def test_run_ui(ui_start: MagicMock):
    """Should start the UI."""
    assert 0 == run_command('ui --name=123.123.123.123')
    assert 1 == ui_start.call_count


@patch('cauldron.invoke.invoker.CauldronShell')
def test_run_view(shell_constructor: MagicMock):
    """Should launch a view through the UI."""
    shell = MagicMock()
    shell_constructor.return_value = shell
    assert 0 == run_command('view foo.cauldron')
    assert 1 == shell_constructor.call_count
    assert 1 == shell.default.call_count
