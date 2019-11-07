from unittest.mock import MagicMock
from unittest.mock import patch

from cauldron import environ
from cauldron import ui


@patch('cauldron.ui.launcher')
@patch('cauldron.ui.connect')
@patch('cauldron.ui.environ.remote_connection')
@patch('cauldron.ui.environ.systems')
@patch('cauldron.ui.configs')
@patch('flask.Flask')
def test_start_defaults(
        flask_constructor: MagicMock,
        ui_configs: MagicMock,
        environ_systems: MagicMock,
        remote_connection: MagicMock,
        connect: MagicMock,
        launcher: MagicMock,
):
    """Should start the ui with default configuration."""
    ui_configs.UI_APP_DATA = {}
    ui_configs.LAUNCH_THREAD = None
    connect.clean_url.return_value = 'foo'
    connect.check_connection.return_value = environ.Response().fail().response
    launcher.find_open_port.return_value = 1234

    app = MagicMock()
    flask_constructor.return_value = app
    ui.start()

    expected = {'port': 1234, 'debug': False, 'host': None}
    assert expected == app.run.call_args[1], """
        Expect app run configuration to be {}
        """.format(expected)
    assert all(
        item in ui_configs.UI_APP_DATA.items()
        for item in expected.items()
    ), """
        Expect configs.UI_APP_DATA to have {}
        """.format(expected)
    assert 0 == environ_systems.end.call_count, """
        Expected no call to end the application execution process.
        """
    assert ui_configs.LAUNCH_THREAD is not None, 'Expect a launch thread.'


@patch('cauldron.ui.launcher')
@patch('cauldron.ui.connect')
@patch('cauldron.ui.environ.remote_connection')
@patch('cauldron.ui.environ.systems')
@patch('cauldron.ui.configs')
@patch('flask.Flask')
def test_start_customized(
        flask_constructor: MagicMock,
        ui_configs: MagicMock,
        environ_systems: MagicMock,
        remote_connection: MagicMock,
        connect: MagicMock,
        launcher: MagicMock,
):
    """Should start the ui with customized configuration."""
    ui_configs.UI_APP_DATA = {}
    ui_configs.LAUNCH_THREAD = None
    connect.clean_url.return_value = 'foo'
    connect.check_connection.return_value = environ.Response().fail().response
    launcher.find_open_port.return_value = 1234

    app = MagicMock()
    flask_constructor.return_value = app
    ui.start(port=4321, debug=True, public=True)

    expected = {'port': 4321, 'debug': True, 'host': '0.0.0.0'}
    assert expected == app.run.call_args[1], """
        Expect app run configuration to be {}
        """.format(expected)
    assert all(
        item in ui_configs.UI_APP_DATA.items()
        for item in expected.items()
    ), """
        Expect configs.UI_APP_DATA to have {}
        """.format(expected)
    assert 0 == environ_systems.end.call_count, """
        Expected no call to end the application execution process.
        """
    assert ui_configs.LAUNCH_THREAD is None, """
        Expect no launch thread when run in debug mode because 
        auto-reloading causes problems.
        """


@patch('cauldron.ui.launcher')
@patch('cauldron.ui.connect')
@patch('cauldron.ui.environ.remote_connection')
@patch('cauldron.ui.environ.systems')
@patch('cauldron.ui.configs')
@patch('flask.Flask')
def test_start_remote_connection(
        flask_constructor: MagicMock,
        ui_configs: MagicMock,
        environ_systems: MagicMock,
        remote_connection: MagicMock,
        connect: MagicMock,
        launcher: MagicMock,
):
    """Should start the ui with a remote connection."""
    ui_configs.UI_APP_DATA = {}
    ui_configs.LAUNCH_THREAD = None
    connect.clean_url.return_value = 'foo'
    connect.check_connection.return_value = environ.Response()
    launcher.find_open_port.return_value = 1234

    app = MagicMock()
    flask_constructor.return_value = app
    ui.start(port=4321, debug=True, host='bar', connection_url='foo:8080')

    expected = {'port': 4321, 'debug': True, 'host': 'bar'}
    assert expected == app.run.call_args[1], """
        Expect app run configuration to be {}
        """.format(expected)
    assert all(
        item in ui_configs.UI_APP_DATA.items()
        for item in expected.items()
    ), """
        Expect configs.UI_APP_DATA to have {}
        """.format(expected)
    assert 0 == environ_systems.end.call_count, """
        Expected no call to end the application execution process.
        """
    assert ui_configs.LAUNCH_THREAD is None, """
        Expect no launch thread when run in debug mode because 
        auto-reloading causes problems.
        """
    assert remote_connection.url == 'foo'
    assert remote_connection.active


@patch('cauldron.ui.launcher')
@patch('cauldron.ui.connect')
@patch('cauldron.ui.environ.remote_connection')
@patch('cauldron.ui.environ.systems')
@patch('cauldron.ui.configs')
@patch('flask.Flask')
def test_start_remote_connection_failed(
        flask_constructor: MagicMock,
        ui_configs: MagicMock,
        environ_systems: MagicMock,
        remote_connection: MagicMock,
        connect: MagicMock,
        launcher: MagicMock,
):
    """Should start the ui with a remote connection."""
    ui_configs.UI_APP_DATA = {}
    ui_configs.LAUNCH_THREAD = None
    connect.clean_url.return_value = 'foo'
    connect.check_connection.return_value = environ.Response().fail().response
    launcher.find_open_port.return_value = 1234

    app = MagicMock()
    flask_constructor.return_value = app
    ui.start(port=4321, debug=True, host='bar', connection_url='foo:8080')

    assert 0 == app.run.call_count, 'Expect no application to start.'
    assert (1,) == environ_systems.end.call_args[0], """
        Expected exit to be called one with a 1 returncode due to the
        error in establishing a remote connection.
        """


@patch('cauldron.ui.launcher')
@patch('cauldron.ui.connect')
@patch('cauldron.ui.environ.remote_connection')
@patch('cauldron.ui.environ.systems')
@patch('cauldron.ui.configs')
@patch('flask.Flask')
def test_start_version(
        flask_constructor: MagicMock,
        ui_configs: MagicMock,
        environ_systems: MagicMock,
        remote_connection: MagicMock,
        connect: MagicMock,
        launcher: MagicMock,
):
    """Should show version information and then exit without error."""
    ui_configs.UI_APP_DATA = {}
    ui_configs.LAUNCH_THREAD = None
    connect.clean_url.return_value = 'foo'
    connect.check_connection.return_value = environ.Response().fail().response
    launcher.find_open_port.return_value = 1234

    app = MagicMock()
    flask_constructor.return_value = app
    ui.start(version=True)

    assert 0 == app.run.call_count, 'Expect no application to start.'
    assert (0,) == environ_systems.end.call_args[0], """
        Expected exit to be called one with a zero returncode.
        """
