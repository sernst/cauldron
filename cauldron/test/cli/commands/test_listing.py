import os
from unittest.mock import MagicMock
from unittest.mock import patch

from cauldron import environ
from cauldron.test import support
from pytest import mark

CONFIG_VALUES = {
    'recent_paths': [
        environ.paths.resources('examples', 'hello_cauldron'),
        environ.paths.resources('examples', 'hello_text'),
        environ.paths.resources('examples', 'does_not_exist'),
    ],
    'folder_aliases': {}
}


@patch('cauldron.environ.configs')
def test_list_all(configs: MagicMock):
    """Should list all known projects."""
    configs.fetch.side_effect = CONFIG_VALUES.get
    response = support.run_command('list all')

    assert response.success, 'Expect command to succeed.'
    assert support.has_success_code(response, 'FOUND')

    examples_directory = environ.paths.resources('examples')
    data = response.data
    assert {examples_directory} == set(data['spec_groups'].keys()), """
        Expect only a single spec group because we've only given
        the discovery function a single project to work from in the
        examples directory.
        """

    children = os.listdir(examples_directory)
    assert len(children) == len(data['spec_groups'][examples_directory]), """
        Expect each folder in the examples directory to be a project
        that should be represented within the spec group.
        """
    assert len(children) == len(data['specs']), """
        Expect each folder in the examples directory to be a project
        that should be represented by a spec.
        """


@patch('cauldron.environ.configs')
def test_list_recent(configs: MagicMock):
    """Should list recent existing projects."""
    configs.fetch.side_effect = CONFIG_VALUES.get
    response = support.run_command('list recent')

    assert response.success, 'Expect command to succeed.'
    assert support.has_success_code(response, 'PROJECT_HISTORY')

    examples_directory = environ.paths.resources('examples')
    data = response.data
    names = {'hello_cauldron', 'hello_text'}
    assert names == {p['name'] for p in data['projects']}, """
        Expect one entry for each of the projects listed in the configs
        that exist. The third non-existent project should be ignored from
        the returned results.
        """


@patch('cauldron.environ.configs')
def test_list_recent_none_available(configs: MagicMock):
    """Should list no recent projects when none are available."""
    configs.fetch.side_effect = {}.get
    response = support.run_command('list recent')

    assert response.success, 'Expect command to succeed.'
    assert support.has_success_code(response, 'PROJECT_HISTORY')
    assert response.messages[0].message == 'No recent projects found.'


ERASE_SCENARIOS = [
    {'args': '', 'code': 'NO_IDENTIFIER_SET', 'success': False},
    {'args': 'a', 'code': 'NO_MATCH_FOUND', 'success': False},
    {'args': 'hello_text', 'code': 'USER_ABORTED', 'success': True},
    {'args': 'hello_text', 'code': 'REMOVED', 'success': True, 'input': 'yes'},
    {'args': 'hello_text --yes', 'code': 'REMOVED', 'success': True},
]


@mark.parametrize('scenario', ERASE_SCENARIOS)
@patch('cauldron.cli.commands.listing._remover.input')
@patch('cauldron.environ.configs')
def test_list_erase(
        configs: MagicMock,
        remover_input: MagicMock,
        scenario: dict
):
    """Should execute remove action according to specified scenario."""
    configs.fetch.side_effect = CONFIG_VALUES.get
    remover_input.return_value = scenario.get('input', '')

    response = support.run_command('list erase {}'.format(scenario['args']))

    if scenario['success']:
        assert response.success, 'Expect command to succeed.'
        assert support.has_success_code(response, scenario['code'])
    else:
        assert response.failed, 'Expect command to fail.'
        assert support.has_error_code(response, scenario['code'])

    assert configs.put.called == (scenario['code'] == 'REMOVED')


AUTO_COMPLETE_SCENARIOS = [
    {'args': '', 'expected': {'all', 'erase', 'recent'}},
    {'args': 'r', 'expected': {'recent'}},
    {'args': 'recent ', 'expected': set()},
]


@mark.parametrize('scenario', AUTO_COMPLETE_SCENARIOS)
def test_autocomplete(scenario):
    """Should return expected autocompletes based on scenario."""
    result = support.autocomplete('list {}'.format(scenario['args']))
    assert scenario['expected'] == set(result)
