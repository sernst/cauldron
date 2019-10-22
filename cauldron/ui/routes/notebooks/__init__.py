import mimetypes
import os

import flask
import requests

import cauldron
from cauldron import environ
from cauldron.ui import configs as ui_configs

blueprint = flask.Blueprint(
    name='notebooks',
    import_name=__name__,
    url_prefix='{}/notebook'.format(ui_configs.ROOT_PREFIX)
)


def get_remote_view(route: str) -> flask.Response:
    endpoint = route.lstrip('/')
    request = flask.request
    response = requests.request(
        method=request.method,
        url='{}/view/{}'.format(environ.remote_connection.url, endpoint),
        headers={k: v for k, v in request.headers if k != 'Host'},
        data=request.get_data(),
        cookies=request.cookies,
        allow_redirects=False
    )

    excluded_headers = [
        'connection',
        'content-encoding',
        'content-length',
        'transfer-encoding',
    ]
    headers = [
        (name, value)
        for name, value in response.raw.headers.items()
        if name.lower() not in excluded_headers
    ]

    return flask.Response(response.content, response.status_code, headers)


@blueprint.route('/<path:route>', methods=['GET', 'POST'])
def notebook(route: str):
    """
    Retrieves the contents of the file specified by the view route if it
    exists.
    """
    if environ.remote_connection.active:
        return get_remote_view(route)

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
