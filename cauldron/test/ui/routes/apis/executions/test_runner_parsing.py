from unittest.mock import MagicMock
from unittest.mock import patch

from pytest import mark

from cauldron.test import support
from cauldron.ui.routes.apis.executions import runner

SCENARIOS = [
    {
        'command': 'ls',
        'args': 'foo.py --help',
        'expected': ('ls', 'foo.py --help')
    },
    {
        'command': 'ls',
        'args': ['foo.py', '--help'],
        'expected': ('ls', 'foo.py --help')
    },
    {
        'command': 'ls foo.py --help',
        'expected': ('ls', 'foo.py --help')
    },
]


@mark.parametrize('scenario', SCENARIOS)
@patch('cauldron.ui.routes.apis.executions.runner.arguments.from_request')
def test_parse(
        arguments_from_request: MagicMock,
        scenario: dict,
):
    """Should parse command into expected result for the given scenario."""
    arguments_from_request.return_value = scenario

    response = runner.parse_command_args()

    assert response.success
    assert scenario['expected'] == response.returned


@patch('cauldron.ui.routes.apis.executions.runner.flask')
@patch('cauldron.ui.routes.apis.executions.runner.arguments.from_request')
def test_parse_failure(
        arguments_from_request: MagicMock,
        mock_flask: MagicMock
):
    """Should fail to parse arguments when args are of the incorrect type."""
    mock_flask.request.mime_type = 'fake/foo'
    mock_flask.request.data = 'this is fake'
    arguments_from_request.return_value = {'command': 'foo', 'args': [1, 2]}

    response = runner.parse_command_args()

    assert support.has_error_code(response, 'INVALID_COMMAND')
    assert response.returned is None
