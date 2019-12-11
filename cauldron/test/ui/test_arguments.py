from unittest.mock import MagicMock
from unittest.mock import patch

from cauldron.ui import arguments


@patch('cauldron.ui.arguments.flask')
def test_mocked_request_defaulted(mocked_flask: MagicMock):
    """Should default to empty dict when no args present on request."""
    request = MagicMock()
    mocked_flask.request = request
    result = arguments.from_request('invalid-request-value')
    assert {} == result, """
        Expect empty result because nothing else had values.
        """
    assert 0 == request.get_json.call_count, """
        Expect no interaction with imported flask request object because
        one has been passed in instead.
        """


@patch('cauldron.ui.arguments.flask')
def test_mocked_request_json(mocked_flask: MagicMock):
    """Should return json dict when json args present on request."""
    request = MagicMock()
    request.get_json.return_value = {'a': 1}
    mocked_flask.request = request

    result = arguments.from_request()
    assert {'a': 1} == result, """
        Expect results to come from the get_json return value.
        """
    assert 1 == request.get_json.call_count, """
        Expect the get_json method to be called.
        """


@patch('cauldron.ui.arguments.flask')
def test_mocked_request_values(mocked_flask: MagicMock):
    """Should return values dict when get args present on request."""
    request = MagicMock()
    request.get_json.side_effect = ValueError
    request.values = {'b': 2}
    mocked_flask.request = request

    result = arguments.from_request()

    assert {'b': 2} == result, """
        Expect results to come from the values attribute.
        """
    assert 1 == request.get_json.call_count, """
        Expect the get_json method to be called but fails with error.
        """
