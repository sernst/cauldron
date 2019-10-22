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

    if environ.remote_connection.active:
        status = requests.post(
            '{}/ui-status'.format(environ.remote_connection.url),
            json=args
        ).json()

        # Steps modified locally should be identified as dirty
        # or the status display.
        status['project'] = reconciler.localize_dirty_steps(
            status.get('project')
        )
        return flask.jsonify(status)

    results = ui_statuses.get_status(last_timestamp, force)
    return flask.jsonify(results)
