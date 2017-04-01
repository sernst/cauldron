from flask import request as flask_request


def from_request(request=None) -> dict:
    """ Fetches the arguments for the current Flask application request """

    request = request if request else flask_request

    try:
        json_args = request.get_json(silent=True)
    except Exception:
        json_args = None

    try:
        get_args = request.values
    except Exception:
        get_args = None

    arg_sources = list(filter(
        lambda arg: arg is not None,
        [json_args, get_args, {}]
    ))

    return arg_sources[0]
