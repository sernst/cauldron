import flask
import requests
from cauldron import environ
from cauldron.ui import arguments
from cauldron.ui import configs as ui_configs
from cauldron.ui import statuses as ui_statuses
from cauldron.ui.routes.apis.statuses import reconciler

blueprint = flask.Blueprint(
    name='statuses',
    import_name=__name__,
    url_prefix='{}/api'.format(ui_configs.ROOT_PREFIX)
)


@blueprint.route('/status', methods=['POST'])
def status():
    """
    Returns the current status of the cauldron kernel application, which is
    used to keep the
    :return:
    """
    args = arguments.from_request()
    last_timestamp = args.get('last_timestamp', 0)
    force = args.get('force', False)

    if not environ.remote_connection.active:
        results = ui_statuses.get_status(last_timestamp, force)
        return flask.jsonify(results)

    # When connected remotely, get the status from the remote kernel and
    # then merge it with local information that may not have been synced
    # to the remote kernel yet.
    try:
        remote_status = requests.post(
            '{}/ui-status'.format(environ.remote_connection.url),
            json=args
        ).json()
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

    # Steps modified locally should be identified as dirty
    # or the status display.
    remote_status['project'] = reconciler.localize_dirty_steps(
        remote_status.get('project')
    )

    # We care about the local remote connection, which is active,
    # not the remote one.
    remote_status['remote'] = environ.remote_connection.serialize()

    return flask.jsonify(remote_status)
