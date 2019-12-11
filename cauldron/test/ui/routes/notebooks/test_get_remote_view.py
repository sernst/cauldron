from unittest.mock import MagicMock
from unittest.mock import patch

from cauldron.ui.routes import notebooks


@patch('cauldron.ui.routes.notebooks.flask')
@patch('cauldron.ui.routes.notebooks.requests.request')
def test_get_remote_view(
        requests_request: MagicMock,
        mock_flask: MagicMock,
):
    """Should retrieve remote view via request."""
    remote_response = MagicMock()
    remote_response.raw.headers = {'foo': 'bar'}
    remote_response.content = 'hello'
    remote_response.status_code = 200
    requests_request.return_value = remote_response

    response = notebooks._get_remote_view('foo.js')
    assert response is not None

    args = mock_flask.Response.call_args[0]
    assert 'hello' == args[0]
    assert 200 == args[1]
    assert ('foo', 'bar') in list(args[2])
