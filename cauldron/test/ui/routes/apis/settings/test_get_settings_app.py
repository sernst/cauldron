from unittest.mock import MagicMock
from unittest.mock import patch

import flask
from cauldron.ui import configs
from cauldron.ui.routes.apis import settings

test_app = flask.Flask(__name__)
test_app.register_blueprint(settings.blueprint)


@patch('cauldron.ui.routes.apis.statuses.environ.configs.fetch')
def test_get_settings_app(
        configs_fetch: MagicMock,
):
    """Should retrieve application settings."""
    configs_fetch.return_value = {'foo': 'bar'}

    client = test_app.test_client()
    response = client.get('{}/settings/app'.format(configs.ROOT_PREFIX))

    assert 200 == response.status_code, 'Expect successful call.'
    assert {'foo': 'bar'} == response.json['settings'], """
        Expect the settings payload in JSON format.
        """
