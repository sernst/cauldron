from unittest.mock import MagicMock
from unittest.mock import mock_open
from unittest.mock import patch

from cauldron.test import support
from pytest import mark


@patch('cauldron.cli.commands.view.ui_command.execute')
@patch('cauldron.cli.commands.view.zipfile.ZipFile')
def test_view_launch_ui(
        zipfile_constructor: MagicMock,
        ui_execute: MagicMock,
):
    """Should open a cauldron view file in the UI."""
    mock_file = mock_open(read_data='{"foo": "bar"}')
    with patch('builtins.open', new=mock_file):
        response = support.run_command('view open foo.cauldron')
    assert response.success, 'Expect command to succeed.'
    assert 1 == ui_execute.call_count, 'Expect ui to be started.'


@patch('cauldron.environ.modes._current_modes', new=['ui'])
@patch('cauldron.cli.commands.view.ui_command.execute')
@patch('cauldron.cli.commands.view.zipfile.ZipFile')
def test_view_no_ui_launch(
        zipfile_constructor: MagicMock,
        ui_execute: MagicMock,
):
    """Should open a cauldron view file in the UI."""
    mock_file = mock_open(read_data='{"foo": "bar"}')
    with patch('builtins.open', new=mock_file):
        response = support.run_command('view open foo.cauldron')
    assert response.success, 'Expect command to succeed.'
    assert 0 == ui_execute.call_count, """
        Expect ui not to be started because it is already running
        as indicated by having the "ui" mode.
        """


@patch('cauldron.environ.view', new={'directory': 'foo'})
@patch('cauldron.environ.systems.remove')
@patch('cauldron.cli.commands.view.zipfile.ZipFile')
def test_view_close(
        zipfile_constructor: MagicMock,
        systems_remove: MagicMock,
):
    """Should close a cauldron view file."""
    response = support.run_command('view close')
    assert 'CLOSED_VIEW_FILE' == response.messages[0].code, """
        Expect command to succeed in running with the expected output.
        """
    assert 0 == zipfile_constructor.call_count, """
        Expect close to return before the ZipFile constructor would 
        be called.
        """
    assert 1 == systems_remove.call_count, """
        Expect the systems removal to be called as part of the close
        process.
        """


@patch('cauldron.environ.view', new=None)
@patch('cauldron.environ.systems.remove')
@patch('cauldron.cli.commands.view.zipfile.ZipFile')
def test_view_close_skipped(
        zipfile_constructor: MagicMock,
        systems_remove: MagicMock,
):
    """Should skip closing a view file if none are open."""
    response = support.run_command('view close')
    assert 'NO_VIEW_OPEN' == response.messages[0].code, """
        Expect command to succeed in skipping.
        """
    assert 0 == zipfile_constructor.call_count, """
        Expect close to return before the ZipFile constructor would 
        be called.
        """
    assert 0 == systems_remove.call_count, """
        Expect no removal invocation given the close process was
        skipped.
        """


AUTOCOMPLETE_SCENARIOS = [
    ('view o', {'open'}),
    ('view open ', {'path_foo', 'path_bar'}),
    ('view close ', set()),
]


@mark.parametrize('command, expected', AUTOCOMPLETE_SCENARIOS)
@patch('cauldron.cli.interaction.autocompletion.match_path')
def test_ui_autocomplete(
        match_path: MagicMock,
        command: str,
        expected: set
):
    """Should return the expected autocomplete options."""
    match_path.return_value = ['path_foo', 'path_bar']
    results = support.autocomplete(command)
    assert expected == set(results)
