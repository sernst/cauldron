from unittest.mock import MagicMock
from unittest.mock import patch

import flask
from cauldron.ui import configs
from cauldron.ui.routes.apis import settings

test_app = flask.Flask(__name__)
test_app.register_blueprint(settings.blueprint)


@patch('cauldron.ui.routes.apis.statuses.environ.configs.put')
def test_set_settings_app(
        configs_put: MagicMock,
):
    """Should store specified settings in persistent configs."""
    values = {'foo': 'bar', 'spam': 42}

    client = test_app.test_client()
    response = client.post(
        '{}/settings/app'.format(configs.ROOT_PREFIX),
        json={'settings': values},
    )

    assert 200 == response.status_code, 'Expect successful call.'
    call_kwargs = configs_put.call_args[1]
    assert values == call_kwargs['application_settings'], """
        Expect the settings payload to be put into the configs.
        """
    assert call_kwargs.get('persists'), 'Expect configs to persist.'


@patch('cauldron.ui.routes.apis.statuses.environ.configs.put')
def test_set_settings_app_default(
        configs_put: MagicMock,
):
    """Should reset settings in persistent configs."""
    client = test_app.test_client()
    response = client.post(
        '{}/settings/app'.format(configs.ROOT_PREFIX),
        json={},
    )

    assert 200 == response.status_code, 'Expect successful call.'
    call_kwargs = configs_put.call_args[1]
    assert {} == call_kwargs['application_settings'], """
        Expect the default empty settings payload to be put into the configs.
        """
    assert call_kwargs.get('persists'), 'Expect configs to persist.'
