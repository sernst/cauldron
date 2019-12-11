from unittest.mock import MagicMock
from unittest.mock import patch

import flask
from cauldron.ui import configs
from cauldron.ui.routes import apps
from pytest import mark

test_app = flask.Flask(__name__)
test_app.register_blueprint(apps.blueprint)


SCENARIOS = [
    {'exists': True, 'endpoint': '', 'match': 'index.html'},
    {'exists': True, 'endpoint': 'foo.js', 'match': 'foo.js'},
    {'exists': False, 'endpoint': 'foo.js'},
]


@mark.parametrize('scenario', SCENARIOS)
@patch('cauldron.ui.routes.apps.os.path.exists')
@patch('cauldron.ui.routes.apps.flask.send_file')
def test_view(
        flask_send_file: MagicMock,
        exists: MagicMock,
        scenario: dict,
):
    """Should return app file based on the scenario."""
    flask_send_file.return_value = flask.Response()
    exists.return_value = scenario['exists']

    client = test_app.test_client()
    response = client.get('{}/app/{}'.format(
        configs.ROOT_PREFIX,
        scenario['endpoint']
    ))

    code = 200 if scenario['exists'] else 204
    assert 1 == exists.call_count
    assert code == response.status_code, """
        Expect the default success response to be returned.
        """

    if scenario['exists']:
        path = flask_send_file.call_args[0][0]
        assert path.endswith(scenario['match'])
    else:
        assert not flask_send_file.called
