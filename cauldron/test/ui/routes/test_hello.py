import flask

from cauldron.ui import routes

test_app = flask.Flask(__name__)
test_app.register_blueprint(routes.blueprint)


def test_hello():
    """Should return a redirect."""
    client = test_app.test_client()
    response = client.get('/')
    assert 302 == response.status_code
    assert 'http://localhost/v1/app' == response.location
