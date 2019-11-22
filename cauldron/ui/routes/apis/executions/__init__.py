import flask

import requests
from cauldron import environ
from cauldron.ui import configs as ui_configs
from cauldron.ui.routes.apis.executions import runner

blueprint = flask.Blueprint(
    name='executions',
    import_name=__name__,
    url_prefix='{}/api'.format(ui_configs.ROOT_PREFIX)
)


@blueprint.route('/command/sync', methods=['POST'])
def command_sync():
    """Executes a synchronous command."""
    return runner.execute(False)


@blueprint.route('/command/async', methods=['POST'])
def command_async():
    """Executes an asynchronous command."""
    r = ui_configs.ACTIVE_EXECUTION_RESPONSE

    # If a thread was running, wait a bit to see if it is nearly
    # complete. There's a small window of time between a step
    # finishing running and the execution thread completing and
    # this helps prevent an aggressive UI calling run on the nex
    # step from triggering an unnecessary error response.
    if r is not None and r.thread and r.thread.is_alive():
        r.thread.join(0.5)

    if r is not None and r.thread and r.thread.is_alive():
        return (
            environ.Response()
            .fail(
                code='ACTION_BLOCKED',
                message='Another command is currently executing.',
            )
            .response
            .flask_serialize()
        )

    return runner.execute(True)


@blueprint.route('/command/abort', methods=['POST'])
def abort():
    """Aborts the currently running async command."""
    try:
        # When connected remotely, the abort should be sent to the remote
        # kernel and handled there.
        if environ.remote_connection.active:
            return flask.jsonify(requests.get(
                '{}/abort'.format(environ.remote_connection.url),
            ).json())
    except ConnectionError as error:
        return (
            environ.Response()
            .fail(
                code='REMOTE_CONNECTION_FAILED',
                message='Unable to communicate with the remote kernel.',
                error=error
            )
            .console(whitespace=1)
            .response
            .flask_serialize()
        )

    return runner.abort().flask_serialize()
