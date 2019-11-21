from unittest.mock import MagicMock
from unittest.mock import patch

from cauldron import environ
from cauldron.test import support
from pytest import mark

SCENARIOS = [
    {'active': False, 'project': None},
    {'active': False, 'project': MagicMock()},
    {'active': True, 'project': None},
    {'active': True, 'project': MagicMock()},
]


@mark.parametrize('scenario', SCENARIOS)
@patch('cauldron.cli.commands.ls.os.name', new='nt')
@patch('cauldron.cli.commands.ls.os.path.exists')
@patch('cauldron.environ.remote_connection')
@patch('cauldron.project.get_internal_project')
def test_ls(
        get_internal_project: MagicMock,
        remote_connection: MagicMock,
        os_path_exists: MagicMock,
        scenario: dict
):
    """Should list the contents of the specified directory."""
    os_path_exists.return_value = True
    remote_connection.active = scenario['active']
    get_internal_project.return_value = scenario['project']

    path = environ.paths.resources('examples', 'hello_cauldron')
    response = support.run_command('ls "{}"'.format(path))
    assert response.success, 'Expect ls to succeed.'

    data = response.data
    assert path == data['current_directory'], """
        Expect the current directory to be the one specified in
        the command arguments.
        """
    assert path.startswith(data['parent_directory'])
    assert data['shortened_directory'].endswith('hello_cauldron')
    assert 'hello_cauldron' == data['spec']['name'], """
        Expect this to be a project directory and to load the
        project spec.
        """
    assert {'step_tests'} == {d['folder'] for d in data['children']}, """
        Expect one child directory named 'step_test'.
        """
    expected = {'cauldron.json', 'S01-create-data.py', 'S02-plot-data.py'}
    assert expected == {f['name'] for f in data['current_files']}, """
        Expect three specific files in the selected directory.
        """
    offset = 1 if scenario['active'] or scenario['project'] else 0
    assert 27 + offset == len(data['standard_locations']), """
        Expect home directory, parent directory and one windows root
        drive location for each letter of the alphabet except Z. 
        Also expect one for the project directory if a local or
        remote project is open.
        """


@patch('cauldron.cli.commands.ls.os.listdir')
def test_ls_permissions_error(os_listdir: MagicMock):
    """Should fail to list directory due to lack of permissions."""
    os_listdir.side_effect = PermissionError
    path = environ.paths.resources('examples', 'hello_cauldron')
    response = support.run_command('ls "{}"'.format(path))
    assert support.has_error_code(response, 'PERMISSION_DENIED')
