from unittest.mock import MagicMock
from unittest.mock import patch

from cauldron.ui import arguments


@patch('cauldron.ui.arguments.flask_request')
def test_mocked_request_defaulted(flask_request: MagicMock):
    """Should default to empty dict when no args present on request."""
    result = arguments.from_request('invalid-request-value')
    assert {} == result, """
        Expect empty result because nothing else had values.
        """
    assert 0 == flask_request.get_json.call_count, """
        Expect no interaction with imported flask request object because
        one has been passed in instead.
        """


@patch('cauldron.ui.arguments.flask_request')
def test_mocked_request_json(flask_request: MagicMock):
    """Should return json dict when json args present on request."""
    flask_request.get_json.return_value = {'a': 1}
    result = arguments.from_request()
    assert {'a': 1} == result, """
        Expect results to come from the get_json return value.
        """
    assert 1 == flask_request.get_json.call_count, """
        Expect the get_json method to be called.
        """


@patch('cauldron.ui.arguments.flask_request')
def test_mocked_request_values(flask_request: MagicMock):
    """Should return values dict when get args present on request."""
    flask_request.get_json.side_effect = ValueError
    flask_request.values = {'b': 2}
    result = arguments.from_request()

    assert {'b': 2} == result, """
        Expect results to come from the values attribute.
        """
    assert 1 == flask_request.get_json.call_count, """
        Expect the get_json method to be called but fails with error.
        """
