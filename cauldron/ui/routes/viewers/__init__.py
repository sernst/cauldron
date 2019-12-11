import mimetypes
import os

import flask
from cauldron import environ
from cauldron.ui import configs as ui_configs

blueprint = flask.Blueprint(
    name='viewers',
    import_name=__name__,
    url_prefix='{}/view'.format(ui_configs.ROOT_PREFIX)
)


@blueprint.route('/notebook/<path:route>', methods=['GET', 'POST'])
def view(route: str):
    """
    Retrieves the contents of the file specified by the view route if it
    exists.
    """
    path = environ.paths.resources('web', route)
    if not os.path.exists(path):
        return '', 204

    return flask.send_file(
        path,
        mimetype=mimetypes.guess_type(path)[0],
        cache_timeout=-1
    )


@blueprint.route('/cache/<path:route>', methods=['GET', 'POST'])
def cache(route: str):
    """
    Retrieves the contents of the file specified by the cache route if it
    exists.
    """
    path = environ.paths.user('reader', 'cache', route)
    if not os.path.exists(path):
        return '', 204

    return flask.send_file(
        path,
        mimetype=mimetypes.guess_type(path)[0],
        cache_timeout=-1
    )
