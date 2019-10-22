import flask

from cauldron.cli.server import run as server_runner
from cauldron.ui import arguments
from cauldron.ui import statuses


@server_runner.APPLICATION.route('/ui-status', methods=['POST'])
def ui_status():
    args = arguments.from_request()
    last_timestamp = args.get('last_timestamp', 0)
    force = args.get('force', False)
    results = statuses.get_status(last_timestamp, force)
    return flask.jsonify(results)
