from unittest.mock import MagicMock
from unittest.mock import patch

import flask
from cauldron.ui import configs
from cauldron.ui.routes.apis import settings

test_app = flask.Flask(__name__)
test_app.register_blueprint(settings.blueprint)


@patch('cauldron.ui.routes.apis.statuses.environ.configs.put')
@patch('cauldron.ui.routes.apis.statuses.environ.configs.fetch')
def test_update_settings_app(
        configs_fetch: MagicMock,
        configs_put: MagicMock,
):
    """Should update specified settings in persistent configs."""
    existing = {'foo': 'bar', 'spam': 42}
    updates = {'spam': 43, 'ham': False}

    configs_fetch.return_value = existing

    client = test_app.test_client()
    response = client.put(
        '{}/settings/app'.format(configs.ROOT_PREFIX),
        json={'settings': updates},
    )

    assert 200 == response.status_code, 'Expect successful call.'
    call_kwargs = configs_put.call_args[1]
    assert call_kwargs.get('persists'), 'Expect configs to persist.'

    expected = {'foo': 'bar', 'spam': 43, 'ham': False}
    merged = call_kwargs['application_settings']
    assert merged == expected, """
        Expect the settings payload to be merged into existing configs.
        """


@patch('cauldron.ui.routes.apis.statuses.environ.configs.put')
@patch('cauldron.ui.routes.apis.statuses.environ.configs.fetch')
def test_update_settings_app_empty(
        configs_fetch: MagicMock,
        configs_put: MagicMock,
):
    """Should leave settings as is in persistent configs."""
    existing = {'foo': 'bar', 'spam': 42}
    configs_fetch.return_value = existing

    client = test_app.test_client()
    response = client.put(
        '{}/settings/app'.format(configs.ROOT_PREFIX),
        json={},
    )

    assert 200 == response.status_code, 'Expect successful call.'
    call_kwargs = configs_put.call_args[1]
    assert call_kwargs.get('persists'), 'Expect configs to persist.'
    assert existing == call_kwargs['application_settings'], """
        Expect no changes to the existing application settings.
        """
