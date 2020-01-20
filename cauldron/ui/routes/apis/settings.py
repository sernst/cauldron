import flask

from cauldron import environ
from cauldron.ui import arguments
from cauldron.ui import configs as ui_configs

blueprint = flask.Blueprint(
    name='settings',
    import_name=__name__,
    url_prefix='{}/settings'.format(ui_configs.ROOT_PREFIX)
)


@blueprint.route('/app', methods=['GET'])
def get_settings_app():
    """Returns the current application configuration settings."""
    settings = environ.configs.fetch('application_settings', default_value={})
    return flask.jsonify({'settings': settings, 'success': True})


@blueprint.route('/app', methods=['POST'])
def set_settings_app():
    """Saves the application configuration settings."""
    args = arguments.from_request()
    settings = args.get('settings', {})
    environ.configs.put(application_settings=settings, persists=True)
    return flask.jsonify({'success': True})


@blueprint.route('/app', methods=['PUT'])
def update_settings_app():
    """Updates the given key(s) in the configuration settings."""
    args = arguments.from_request()

    updates = args.get('settings', {})
    settings = environ.configs.fetch('application_settings', default_value={})
    merged = { **settings, **updates}

    environ.configs.put(application_settings=merged, persists=True)
    return flask.jsonify({'success': True, 'settings': merged})
