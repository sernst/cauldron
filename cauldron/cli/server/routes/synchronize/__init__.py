import flask

import cauldron as cd
from cauldron.cli.server import run as server_runner
from cauldron.cli.server.routes.synchronize import status
from cauldron.environ.response import Response


@server_runner.APPLICATION.route('/sync-status', methods=['GET', 'POST'])
def fetch_synchronize_status():
    """
    Returns the synchronization status information for the currently opened
    project
    """

    r = Response()
    project = cd.project.internal_project

    if not project:
        r.fail(
            code='NO_PROJECT',
            message='No open project on which to retrieve status'
        )
    else:
        result = status.of_project(project)
        r.update(success=True, status=result)

    return flask.jsonify(r.serialize())
