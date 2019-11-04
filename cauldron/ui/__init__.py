import json
import logging

from flask import Flask

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
from cauldron.ui.routes.apis import executions as executions_routes
from cauldron.ui.routes.apis import statuses as statuses_routes


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
    """
    Starts the application UI.
    """
    if version:
        environ.log('VERSION: {}'.format(environ.version))
        return environ.systems.end(0)

    if connection_url:
        url = connect.clean_url(connection_url)
        response = connect.check_connection(url, False)
        if response.failed:
            return environ.systems.end(1)

        environ.remote_connection.url = url
        environ.remote_connection.active = True

    if host is None and public:
        host = '0.0.0.0'

    configs.UI_APP_DATA.update(
        host=host,
        port=port,
        debug=debug,
        id=environ.start_time.isoformat(),
    )

    if not debug:
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)

    if not quiet:
        with open(environ.paths.package('settings.json'), 'r') as f:
            package_data = json.load(f)

        print('\n{}\n'.format(
            templating.render_template(
                'kernel_introduction.txt',
                version=package_data['version']
            )
        ))

    has_interactive = environ.modes.has(environ.modes.INTERACTIVE)
    environ.modes.add(environ.modes.INTERACTIVE)

    app = Flask('Cauldron-Application')
    app.json_encoder = ComplexFlaskJsonEncoder

    app.register_blueprint(routes.blueprint)
    app.register_blueprint(apps_routes.blueprint)
    app.register_blueprint(statuses_routes.blueprint)
    app.register_blueprint(executions_routes.blueprint)
    app.register_blueprint(notebooks_routes.blueprint)

    # Either used the specified port for the UI if one was given or
    # find the first available port in the given range and use that
    # one instead.
    ui_port = port or launcher.find_open_port(host, range(8899, 9999))

    # Launches the UI in a web browser once the server has started.
    if not configs.LAUNCH_THREAD and not debug:
        thread = launcher.OpenUiOnStart(host=host, port=ui_port)
        configs.LAUNCH_THREAD = thread
        thread.start()

    app.run(port=ui_port, debug=debug, host=host)

    if not has_interactive:
        environ.modes.remove(environ.modes.INTERACTIVE)
