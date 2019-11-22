from unittest.mock import MagicMock
from unittest.mock import patch

import flask
from cauldron import environ
from cauldron.test import support
from cauldron.ui import configs
from cauldron.ui.routes.apis import statuses

test_app = flask.Flask(__name__)
test_app.register_blueprint(statuses.blueprint)


@patch('cauldron.ui.routes.apis.statuses.ui_statuses.get_status')
@patch('cauldron.ui.routes.apis.statuses.environ.remote_connection')
def test_status(
        remote_connection: MagicMock,
        get_status: MagicMock,
):
    """Should return status information from local environment."""
    remote_connection.active = False
    get_status.return_value = {'foo': 'bar'}

    client = test_app.test_client()
    response = client.post(
        '{}/api/status'.format(configs.ROOT_PREFIX),
        json={'last_timestamp': 42, 'force': True}
    )

    assert 200 == response.status_code, 'Expect successful call.'
    assert {'foo': 'bar'} == response.json, """
        Expect the get_status function results to be returned as
        the response payload in JSON format.
        """


@patch('cauldron.ui.routes.apis.statuses.requests.post')
@patch('cauldron.ui.routes.apis.statuses.ui_statuses.merge_local_state')
@patch('cauldron.ui.routes.apis.statuses.ui_statuses.get_status')
@patch('cauldron.ui.routes.apis.statuses.environ.remote_connection')
def test_status_remote(
        remote_connection: MagicMock,
        get_status: MagicMock,
        merge_local_state: MagicMock,
        requests_post: MagicMock,
):
    """Should execute remote status call."""
    remote_connection.active = True
    requests_post.return_value.json.return_value = {'foo': 'bar'}
    merge_local_state.return_value = {'bar': 'foo'}

    client = test_app.test_client()
    response = client.post(
        '{}/api/status'.format(configs.ROOT_PREFIX),
        json={'last_timestamp': 42, 'force': True}
    )

    assert 200 == response.status_code, 'Expect successful call.'
    assert {'bar': 'foo'} == response.json, """
        Expect the merge local state function results to be returned as
        the response payload in JSON format.
        """

    assert not get_status.called, """
        Expect remote status requests to be made as a proxy to the
        remote kernel and not generated from a get_status call.
        """


@patch('cauldron.ui.routes.apis.statuses.requests.post')
@patch('cauldron.ui.routes.apis.statuses.ui_statuses.merge_local_state')
@patch('cauldron.ui.routes.apis.statuses.ui_statuses.get_status')
@patch('cauldron.ui.routes.apis.statuses.environ.remote_connection')
def test_status_remote_error(
        remote_connection: MagicMock,
        get_status: MagicMock,
        merge_local_state: MagicMock,
        requests_post: MagicMock,
):
    """Should fail to execute remote status."""
    remote_connection.active = True
    requests_post.return_value.json.side_effect = ConnectionError

    client = test_app.test_client()
    response = client.post(
        '{}/api/status'.format(configs.ROOT_PREFIX),
        json={'last_timestamp': 123, 'force': False}
    )

    assert 200 == response.status_code, 'Expect successful call.'
    response = environ.Response.deserialize(response.json)
    assert support.has_error_code(response, 'LOST_REMOTE_CONNECTION'), """
        Expect the remote connection to fail and return an error
        message instead.
        """

    assert not get_status.called, """
        Expect remote status requests to be made as a proxy to the
        remote kernel and not generated from a get_status call.
        """
    assert not merge_local_state.called, """
        Expect remote status request failure to prevent merging local
        state and instead returning an error response.
        """
