import mimetypes
import os

import cauldron
import flask
from cauldron.cli.server import run as server_run


@server_run.APPLICATION.route('/view/<path:route>', methods=['GET', 'POST'])
def view(route: str):
    """
    Retrieves the contents of the file specified by the view route if it
    exists.
    """
    project = cauldron.project.get_internal_project()
    results_path = project.results_path if project else None
    if not project or not results_path:
        return '', 204

    path = os.path.join(results_path, route)
    if not os.path.exists(path):
        return '', 204

    return flask.send_file(
        path,
        mimetype=mimetypes.guess_type(path)[0],
        cache_timeout=-1
    )
