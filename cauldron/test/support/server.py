import json
import typing

from flask import Response as FlaskResponse

from cauldron import environ
from cauldron.cli import server

Responses = typing.NamedTuple('TestResponses', [
    ('flask', FlaskResponse),
    ('response', 'environ.Response')
])


def create_test_app():
    """ """

    return server.server_run.APPLICATION.test_client()


def get(app, endpoint: str, **kwargs) -> Responses:
    """ send get request to the test flask application """

    flask_response = app.get(endpoint, **kwargs)
    response = deserialize_flask_response(flask_response)
    return Responses(flask_response, response)


def post(app, endpoint: str, data=None, **kwargs) -> Responses:
    """ send post request to the test flask application """

    args = json.dumps(data) if data else None
    flask_response = app.post(
        endpoint,
        data=args,
        content_type='application/json',
        **kwargs
    )
    response = deserialize_flask_response(flask_response)

    return Responses(flask_response, response)


def deserialize_flask_response(
        flask_response: FlaskResponse
) -> 'environ.Response':
    """ """

    try:
        data = json.loads(flask_response.data.decode('utf-8', 'ignore'))
        response = environ.Response.deserialize(data)
    except Exception as error:
        response = environ.Response().fail(
            code='DESERIALIZE_FLASK_RESPONSE',
            message='Failed to deserialize flask response',
            error=error
        )

    return response
