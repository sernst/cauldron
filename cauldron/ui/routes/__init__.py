import flask
from cauldron.ui import configs as ui_configs

blueprint = flask.Blueprint(
    name='roots',
    import_name=__name__,
)


@blueprint.route('/')
def hello():
    return flask.redirect('{}/app'.format(ui_configs.ROOT_PREFIX), code=302)
