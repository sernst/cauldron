import os
from unittest.mock import MagicMock
from unittest.mock import patch

from cauldron import environ
from cauldron.test import support

MY_DIRECTORY = environ.paths.clean(os.path.dirname(__file__))


@patch('cauldron.cli.commands.cd.os.chdir')
def test_cd(os_chdir: MagicMock):
    """Should change to the specified directory."""
    response = support.run_command('cd "{}"'.format(MY_DIRECTORY))
    assert response.success, 'Expect cd to succeed.'
    assert MY_DIRECTORY == os_chdir.call_args[0][0], """
        Expect to change to the specified directory, removing the
        wrapped quotation marks along the way.
        """


@patch('cauldron.cli.commands.cd.os.chdir')
def test_cd_no_such_directory(os_chdir: MagicMock):
    """Should fail to change to non-existent directory."""
    os_chdir.side_effect = FileNotFoundError
    response = support.run_command('cd "{}"'.format(MY_DIRECTORY))
    assert support.has_error_code(response, 'NO_SUCH_DIRECTORY')


@patch('cauldron.cli.commands.cd.os.chdir')
def test_cd_permission_error(os_chdir: MagicMock):
    """Should fail to change to directory one cannot access."""
    os_chdir.side_effect = PermissionError
    response = support.run_command('cd "{}"'.format(MY_DIRECTORY))
    assert support.has_error_code(response, 'PERMISSION_DENIED')
