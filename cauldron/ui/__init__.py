import logging
import os

import flask
import waitress

from cauldron import environ
from cauldron import templating
from cauldron.cli.commands import connect
from cauldron.render.encoding import ComplexFlaskJsonEncoder
from cauldron.ui import configs
from cauldron.ui import launcher
from cauldron.ui import routes
from cauldron.ui.parsing import create_parser  # noqa
from cauldron.ui.routes import apps as apps_routes
from cauldron.ui.routes import notebooks as notebooks_routes
from cauldron.ui.routes import viewers as viewers_routes
from cauldron.ui.routes.apis import executions as executions_routes
from cauldron.ui.routes.apis import statuses as statuses_routes

# Optional includes for APM monitoring during development.
if os.environ.get('ENABLE_APM') is not None:  # pragma: no-cover
    try:
        from scout_apm.flask import ScoutApm
    except ImportError:
        ScoutApm = None

    try:
        # Optional include for APM monitoring during development.
        import newrelic.agent
        newrelic.agent.initialize()
    except ImportError:
        pass
else:
    ScoutApm = None


def create_application(
        port: int = None,
        debug: bool = False,
        public: bool = False,
        host: str = None,
        quiet: bool = False,
        version: bool = False,
        connection_url: str = None,
        **kwargs,
) -> dict:
    """Creates the flask application to run."""
    if version:
        environ.log('VERSION: {}'.format(environ.version))
        return environ.systems.end(0)

    if connection_url:
        url = connect._clean_url(connection_url)
        response = connect.check_connection(url, False)
        if response.failed:
            return environ.systems.end(1)

        environ.remote_connection.url = url
        environ.remote_connection.active = True

    if host is None and public:
        host = '0.0.0.0'

    if not debug:
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)

    if not quiet:
        templating.render_splash()

    was_interactive = environ.modes.has(environ.modes.INTERACTIVE)
    environ.modes.add(environ.modes.INTERACTIVE)
    environ.modes.add(environ.modes.UI)

    app = flask.Flask('Cauldron-Application')
    app.json_encoder = ComplexFlaskJsonEncoder

    app.register_blueprint(routes.blueprint)
    app.register_blueprint(apps_routes.blueprint)
    app.register_blueprint(statuses_routes.blueprint)
    app.register_blueprint(executions_routes.blueprint)
    app.register_blueprint(notebooks_routes.blueprint)
    app.register_blueprint(viewers_routes.blueprint)

    if ScoutApm is not None and os.environ.get('SCOUT_KEY'):
        ScoutApm(app)
        app.config['SCOUT_MONITOR'] = True
        app.config['SCOUT_KEY'] = os.environ['SCOUT_KEY']
        app.config['SCOUT_NAME'] = os.environ.get('SCOUT_NAME', 'cauldron-ui')

    # Either used the specified port for the UI if one was given or
    # find the first available port in the given range and use that
    # one instead.
    ui_port = port or launcher.find_open_port(
        host=host or 'localhost',
        ports=range(8899, 9999)
    )

    # Launches the UI in a web browser once the server has started.
    if not configs.LAUNCH_THREAD and not debug:
        thread = launcher.OpenUiOnStart(host=host, port=ui_port)
        configs.LAUNCH_THREAD = thread
        thread.start()

    configs.UI_APP_DATA.update(
        host=host,
        port=ui_port,
        debug=debug,
        id=environ.start_time.isoformat(),
        was_interactive=was_interactive,
        application=app,
    )
    return configs.UI_APP_DATA


def start(
        port: int = None,
        debug: bool = False,
        public: bool = False,
        host: str = None,
        quiet: bool = False,
        version: bool = False,
        connection_url: str = None,
        **kwargs
):
    """Starts the application UI."""
    ui_app_data = create_application(
        port=port,
        debug=debug,
        public=public,
        host=host,
        quiet=quiet,
        version=version,
        connection_url=connection_url,
        **kwargs
    )

    app = ui_app_data['application']
    if kwargs.get('basic'):
        app.run(
            port=ui_app_data['port'],
            debug=ui_app_data['debug'],
            host=ui_app_data['host'],
            threaded=True
        )
    else:
        waitress.serve(
            app,
            host=ui_app_data['host'] or 'localhost',
            port=ui_app_data['port'],
        )

    environ.modes.remove(environ.modes.UI)
    if not ui_app_data['was_interactive']:
        environ.modes.remove(environ.modes.INTERACTIVE)
