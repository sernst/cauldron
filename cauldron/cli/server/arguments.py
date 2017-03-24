from flask import request


def from_request() -> dict:
    """ Fetches the arguments for the current Flask application request """

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



