from unittest.mock import MagicMock
from unittest.mock import patch

from cauldron.ui.routes import notebooks


@patch('cauldron.ui.routes.notebooks.flask.request')
@patch('cauldron.ui.routes.notebooks.requests.request')
def test_get_remote_view(
        requests_request: MagicMock,
        flask_request: MagicMock,
):
    """Should retrieve remote view via request."""
    remote_response = MagicMock()
    remote_response.raw.headers = {'foo': 'bar'}
    remote_response.content = 'hello'
    remote_response.status_code = 200
    requests_request.return_value = remote_response

    response = notebooks._get_remote_view('foo.js')
    assert 200 == response.status_code
    assert b'hello' == response.data
    assert ('foo', 'bar') in list(response.headers)
