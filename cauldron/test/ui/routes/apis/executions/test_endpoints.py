import os
from unittest.mock import MagicMock
from unittest.mock import patch

import flask

from cauldron import environ
from cauldron.test import support
from cauldron.ui import configs
from cauldron.ui.routes.apis import executions

test_app = flask.Flask(__name__)
test_app.register_blueprint(executions.blueprint)


def test_command_sync():
    """Should execute synchronous command."""
    path = os.path.realpath(os.path.dirname(__file__))
    client = test_app.test_client()
    response = client.post(
        '{}/api/command/sync'.format(configs.ROOT_PREFIX),
        json={'command': 'ls "{}"'.format(path)}
    )
    assert 200 == response.status_code

    r = environ.Response.deserialize(response.json)
    assert r.success


def test_command_async():
    """Should execute asynchronous command."""
    client = test_app.test_client()
    response = client.post(
        '{}/api/command/async'.format(configs.ROOT_PREFIX),
        json={'command': 'version'}
    )
    assert 200 == response.status_code

    r = environ.Response.deserialize(response.json)
    assert r.success


@patch('cauldron.ui.routes.apis.executions.ui_configs')
def test_command_async_blocked(
        ui_configs: MagicMock,
):
    """
    Should abort executing asynchronous command because another is running.
    """
    blocker = MagicMock()
    blocker.thread.is_alive.return_value = True
    ui_configs.ACTIVE_EXECUTION_RESPONSE = blocker

    client = test_app.test_client()
    response = client.post(
        '{}/api/command/async'.format(configs.ROOT_PREFIX),
        json={'command': 'version'}
    )
    assert 200 == response.status_code

    r = environ.Response.deserialize(response.json)
    assert support.has_error_code(r, 'ACTION_BLOCKED')
