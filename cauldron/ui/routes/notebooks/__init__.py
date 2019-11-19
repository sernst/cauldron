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
    is_remote = environ.remote_connection.active
    load_from_resources = (
        route.startswith('assets')
        or (
            is_remote
            and route in ['project.css', 'project.js']
        )
    )

    if load_from_resources:
        # If a local version of the asset exists, send that from the
        # resources directory instead of the results directory.
        local_asset_path = environ.paths.resources('web', route)
        if os.path.exists(local_asset_path):
            return flask.send_file(
                local_asset_path,
                mimetype=mimetypes.guess_type(local_asset_path)[0],
                cache_timeout=-1
            )

    if is_remote:
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
