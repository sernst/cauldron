import flask
import requests
from requests import exceptions as requests_exceptions
from urllib3 import exceptions as url_exceptions

from cauldron import environ
from cauldron.ui import arguments
from cauldron.ui import configs as ui_configs
from cauldron.ui import statuses as ui_statuses

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
    lost_errors = (
        ConnectionError,
        requests_exceptions.ConnectionError,
        requests_exceptions.ConnectTimeout,
        url_exceptions.MaxRetryError,
    )

    try:
        remote_status = requests.post(
            '{}/ui-status'.format(environ.remote_connection.url),
            json=args
        ).json()
    except lost_errors as error:
        ui_configs.status_failures += 1
        return (
            environ.Response().fail(
                code='LOST_REMOTE_CONNECTION',
                message='Unable to communicate with the remote kernel.',
                error=error
            )
            .console_if(
                display_condition=ui_configs.status_failures < 2,
                whitespace=1
            )
            .response
            .flask_serialize()
        )

    ui_configs.status_failures = 0
    return flask.jsonify(ui_statuses.merge_local_state(remote_status, force))
