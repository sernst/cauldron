import os
from unittest.mock import MagicMock
from unittest.mock import patch

import flask
from cauldron.ui import configs
from cauldron.ui.routes import viewers
from pytest import mark

test_app = flask.Flask(__name__)
test_app.register_blueprint(viewers.blueprint)


SCENARIOS = [
    {'exists': True, 'endpoint': 'notebook/foo.js', 'match': 'web/foo.js'},
    {'exists': True, 'endpoint': 'cache/foo.js', 'match': 'foo.js'},
    {'exists': False, 'endpoint': 'notebook/foo.js'},
    {'exists': False, 'endpoint': 'cache/foo.js'},
]


@mark.parametrize('scenario', SCENARIOS)
@patch('cauldron.ui.routes.viewers.os.path.exists')
@patch('cauldron.ui.routes.viewers.flask.send_file')
def test_view(
        flask_send_file: MagicMock,
        exists: MagicMock,
        scenario: dict,
):
    """Should return a viewer file based on the scenario."""
    flask_send_file.return_value = flask.Response()
    exists.return_value = scenario['exists']

    client = test_app.test_client()
    response = client.get('{}/view/{}'.format(
        configs.ROOT_PREFIX,
        scenario['endpoint']
    ))

    assert 1 == exists.call_count

    code = 200 if scenario['exists'] else 204
    assert code == response.status_code, """
        Expect the default success response to be returned.
        """

    if scenario['exists']:
        path = flask_send_file.call_args[0][0]
        assert path.endswith(scenario['match'].replace('/', os.path.sep))
    else:
        assert not flask_send_file.called
