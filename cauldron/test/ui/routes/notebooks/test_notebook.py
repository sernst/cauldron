import os
from unittest.mock import MagicMock
from unittest.mock import patch

import flask
from cauldron import environ
from cauldron.ui import configs
from cauldron.ui.routes import notebooks
from pytest import mark

test_app = flask.Flask(__name__)
test_app.register_blueprint(notebooks.blueprint)

FAKE_RESULTS_DIRECTORY = os.path.realpath(os.path.dirname(__file__))

SCENARIOS = [
    {
        # Asset files should be loaded locally.
        'exists': True,
        'endpoint': 'assets/logo.jpg',
        'remote': False,
        'project': False,
        'local': True,
        'path': environ.paths.resources('web', 'assets', 'logo.jpg'),
        'status': 200,
    },
    {
        # Without a project no file to return.
        'exists': True,
        'endpoint': 'foo.js',
        'remote': False,
        'project': False,
        'local': False,
        'path': None,
        'status': 204,
    },
    {
        # Fail if file does not exist.
        'exists': False,
        'endpoint': 'foo.js',
        'remote': False,
        'project': True,
        'local': False,
        'path': None,
        'status': 204,
    },
    {
        # Load from project results directory.
        'exists': True,
        'endpoint': 'foo.js',
        'remote': False,
        'project': True,
        'local': True,
        'path': os.path.join(FAKE_RESULTS_DIRECTORY, 'foo.js'),
        'status': 200,
    },
    {
        # Load remotely.
        'exists': True,
        'endpoint': 'foo.js',
        'remote': True,
        'project': False,
        'local': False,
        'path': None,
        'status': 200,
    },
    {
        # Asset files should be loaded locally even when remote.
        'exists': True,
        'endpoint': 'assets/logo.jpg',
        'remote': True,
        'project': False,
        'local': True,
        'path': environ.paths.resources('web', 'assets', 'logo.jpg'),
        'status': 200,
    },
]


@mark.parametrize('scenario', SCENARIOS)
@patch('cauldron.project.get_internal_project')
@patch('cauldron.ui.routes.notebooks.environ.remote_connection')
@patch('cauldron.ui.routes.notebooks._get_remote_view')
@patch('cauldron.ui.routes.notebooks.os.path.exists')
@patch('cauldron.ui.routes.notebooks.flask.send_file')
def test_notebook(
        flask_send_file: MagicMock,
        exists: MagicMock,
        _get_remote_view: MagicMock,
        remote_connection: MagicMock,
        get_internal_project: MagicMock,
        scenario: dict,
):
    """Should return a notebook file based on the scenario."""
    flask_send_file.return_value = flask.Response()
    _get_remote_view.return_value = flask.Response()
    exists.return_value = scenario['exists']
    remote_connection.active = scenario['remote']

    if scenario['project']:
        project = MagicMock()
        project.results_path = FAKE_RESULTS_DIRECTORY
    else:
        project = None
    get_internal_project.return_value = project

    client = test_app.test_client()
    response = client.get('{}/notebook/{}'.format(
        configs.ROOT_PREFIX,
        scenario['endpoint']
    ))

    assert scenario['status'] == response.status_code, """
        Expect the default success response to be returned if the
        file exists or a remote call is made.
        """

    if scenario['remote'] and not scenario['local']:
        assert _get_remote_view.called

    if scenario['local'] or scenario['project']:
        assert exists.call_count

    if scenario['path']:
        path = flask_send_file.call_args[0][0]
        assert scenario['path'] == path
    else:
        assert not flask_send_file.called
